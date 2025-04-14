import math
import tk


class PolygonEditor:
    def __init__(self, canvas):
        self.canvas = canvas
        self.vertices = []
        self.hull_method = "Graham"
        self.bind_events()
        self.current_polygon_id = None
        self.current_hull_id = None
        self.fill_algorithm = "EdgeList"
        self.debug_mode = False
        self.fill_color = "blue"

    def clear(self):
        self.vertices = []
        self.canvas.delete("polygon")

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.add_vertex)
        self.canvas.bind("<Double-Button-1>", self.finish_polygon)
        self.canvas.bind("<Button-3>", self.check_point_in_polygon)
        self.canvas.bind("<Control-Button-1>", self.check_segment_intersection)
        print("PolygonEditor: Режим построения многоугольника включён.")

    def add_vertex(self, event):
        x, y = event.x, event.y
        self.vertices.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red", tags="vertex")

        if len(self.vertices) > 1:
            x0, y0 = self.vertices[-2]
            if self.current_polygon_id:
                self.canvas.delete(self.current_polygon_id)
            self.current_polygon_id = self.canvas.create_line(x0, y0, x, y, fill="blue", tags="polygon")

        print(f"Добавлена вершина: ({x}, {y})")

    def finish_polygon(self, event=None):
        if len(self.vertices) < 3:
            print("Недостаточно вершин для построения многоугольника.")
            return

        x0, y0 = self.vertices[0]
        x_last, y_last = self.vertices[-1]
        self.canvas.create_line(x_last, y_last, x0, y0, fill="blue", tags="polygon")

        is_convex = self.check_convexity()
        convex_text = "выпуклый" if is_convex else "невыпуклый"
        print(f"Многоугольник замкнут. Он {convex_text}.")

        hull = self.build_convex_hull()
        self.draw_hull(hull)

        if is_convex:
            self.show_internal_normals()

        self.fill_polygon()

    def fill_polygon(self):
        self.canvas.delete("fill")

        if self.debug_mode:
            print(f"Начало заполнения алгоритмом {self.fill_algorithm}")
            self.canvas.create_text(10, 10, text=f"Алгоритм: {self.fill_algorithm}",
                                    anchor="nw", fill="red", tags="debug_info")

        if self.fill_algorithm == "EdgeList":
            self.fill_edge_list()
        elif self.fill_algorithm == "ActiveEdge":
            self.fill_active_edge()
        elif self.fill_algorithm == "SimpleSeed":
            self.fill_simple_seed()
        elif self.fill_algorithm == "ScanlineSeed":
            self.fill_scanline_seed()

        if self.debug_mode:
            print("Заполнение завершено")
            self.canvas.delete("debug_info")

    def fill_edge_list(self):
        """Алгоритм с упорядоченным списком ребер"""
        if len(self.vertices) < 3:
            return

        y_min = min(v[1] for v in self.vertices)
        y_max = max(v[1] for v in self.vertices)

        edges = []
        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]
            if y1 != y2:
                if y1 < y2:
                    edges.append((x1, y1, x2, y2))
                else:
                    edges.append((x2, y2, x1, y1))

        edges.sort(key=lambda e: e[1])

        for y in range(y_min, y_max + 1):
            active_edges = []
            for edge in edges:
                x1, y1, x2, y2 = edge
                if y1 <= y < y2:
                    if y2 != y1:
                        x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                        active_edges.append(x)

            active_edges.sort()

            for i in range(0, len(active_edges), 2):
                if i + 1 >= len(active_edges):
                    break
                x_start = int(active_edges[i])
                x_end = int(active_edges[i + 1])
                for x in range(x_start, x_end + 1):
                    self.canvas.create_rectangle(x, y, x + 1, y + 1,
                                                 fill=self.fill_color, outline="", tags="fill")
                    if self.debug_mode:
                        self.canvas.update()
                        self.canvas.after(10)

    def fill_active_edge(self):
        """Растровая развертка с упорядоченным списком рёбер"""
        if len(self.vertices) < 3:
            return

        y_min = min(v[1] for v in self.vertices)
        y_max = max(v[1] for v in self.vertices)

        edge_table = {}

        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]

            if y1 == y2:
                continue

            if y1 > y2:
                x_top, y_top = x1, y1
                x_bottom, y_bottom = x2, y2
            else:
                x_top, y_top = x2, y2
                x_bottom, y_bottom = x1, y1

            dx = (x_top - x_bottom) / (y_top - y_bottom)
            edge = {'x': x_top, 'dx': -dx, 'y_min': y_bottom}

            if y_top not in edge_table:
                edge_table[y_top] = []
            edge_table[y_top].append(edge)

        aet = []
        for y in range(y_max, y_min - 1, -1):
            if y in edge_table:
                aet.extend(edge_table[y])

            aet = [e for e in aet if e['y_min'] < y]

            aet.sort(key=lambda e: e['x'])

            for i in range(0, len(aet), 2):
                if i + 1 >= len(aet):
                    break
                x_start = int(round(aet[i]['x']))
                x_end = int(round(aet[i + 1]['x']))

                for x in range(x_start, x_end + 1):
                    self.canvas.create_rectangle(x, y, x + 1, y + 1,
                                                 fill=self.fill_color, outline="", tags="fill")
                    if self.debug_mode:
                        self.canvas.update()
                        self.canvas.after(10)

            for edge in aet:
                edge['x'] += edge['dx']

    def fill_simple_seed(self):
        """Простой алгоритм заполнения с затравкой"""
        if len(self.vertices) < 3:
            return

        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        seed = (int(cx), int(cy))

        if not self.point_in_polygon(seed):
            seed = self.find_inner_point()
            if not seed:
                print("Не удалось найти точку внутри полигона")
                return

        stack = [seed]
        filled = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in filled:
                continue

            self.canvas.create_rectangle(x, y, x + 1, y + 1,
                                         fill=self.fill_color, outline="", tags="fill")
            filled.add((x, y))

            if self.debug_mode:
                self.canvas.update()
                self.canvas.after(10)

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in filled and self.point_in_polygon((nx, ny)):
                    stack.append((nx, ny))

    def fill_scanline_seed(self):
        """Построчный алгоритм заполнения с затравкой"""
        if len(self.vertices) < 3:
            return

        seed = self.find_inner_point()
        if not seed:
            print("Не удалось найти точку внутри полигона")
            return

        stack = [seed]
        filled = set()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        while stack:
            x, y = stack.pop()

            # Пропускаем уже заполненные точки и точки вне холста
            if (x, y) in filled or not (0 <= x < canvas_width and 0 <= y < canvas_height):
                continue

            # Находим левую границу
            left = x
            while left > 0 and self.point_in_polygon((left - 1, y)):
                left -= 1

            # Находим правую границу
            right = x
            while right < canvas_width - 1 and self.point_in_polygon((right + 1, y)):
                right += 1

            # Заполняем строку
            for px in range(left, right + 1):
                if (px, y) not in filled:
                    self.canvas.create_rectangle(px, y, px + 1, y + 1,
                                                 fill=self.fill_color, outline="", tags="fill")
                    filled.add((px, y))

                    if self.debug_mode:
                        self.canvas.update()
                        self.canvas.after(10)  # Замедление для отладки

            # Проверяем строки выше и ниже
            for ny in [y - 1, y + 1]:
                if 0 <= ny < canvas_height:
                    # Ищем затравки на следующей строке
                    px = left
                    while px <= right:
                        if self.point_in_polygon((px, ny)) and (px, ny) not in filled:
                            # Нашли начало нового сегмента
                            start = px
                            while px <= right and self.point_in_polygon((px, ny)) and (px, ny) not in filled:
                                px += 1
                            # Добавляем середину сегмента в стек
                            stack.append((start + (px - start) // 2, ny))
                        else:
                            px += 1

    def find_inner_point(self):
        """Более надежный поиск внутренней точки"""
        if not self.vertices:
            return None

        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        if self.point_in_polygon((cx, cy)):
            return (int(cx), int(cy))

        for y in range(int(min(v[1] for v in self.vertices)) + 1, int(max(v[1] for v in self.vertices)), 2):
            intersections = []
            n = len(self.vertices)
            for i in range(n):
                x1, y1 = self.vertices[i]
                x2, y2 = self.vertices[(i + 1) % n]
                if (y1 <= y <= y2) or (y2 <= y <= y1):
                    if y1 != y2:
                        x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                        intersections.append(x)

            intersections.sort()
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    mid_x = (intersections[i] + intersections[i + 1]) / 2
                    if self.point_in_polygon((mid_x, y)):
                        return (int(mid_x), y)

        return None

    def check_convexity(self):
        n = len(self.vertices)
        if n < 3:
            return False

        sign = None
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]
            x3, y3 = self.vertices[(i + 2) % n]

            dx1, dy1 = x2 - x1, y2 - y1
            dx2, dy2 = x3 - x2, y3 - y2
            cross = dx1 * dy2 - dy1 * dx2

            if cross != 0:
                current_sign = cross > 0
                if sign is None:
                    sign = current_sign
                elif sign != current_sign:
                    return False
        return True

    def build_convex_hull(self):
        if self.hull_method == "Graham":
            return self.convex_hull_graham()
        elif self.hull_method == "Jarvis":
            return self.convex_hull_jarvis()
        else:
            return []

    def convex_hull_graham(self):
        points = self.vertices.copy()
        n = len(points)
        if n < 3:
            return points

        pivot = min(points, key=lambda p: (p[1], p[0]))

        def polar_angle(p):
            angle = math.atan2(p[1] - pivot[1], p[0] - pivot[0])
            return angle

        sorted_points = sorted(points, key=polar_angle)

        hull = [pivot, sorted_points[1]]
        for p in sorted_points[2:]:
            while len(hull) >= 2:
                x1, y1 = hull[-2]
                x2, y2 = hull[-1]
                cross = (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)
                if cross <= 0:
                    hull.pop()
                else:
                    break
            hull.append(p)

        return hull

    def convex_hull_jarvis(self):
        points = self.vertices.copy()
        n = len(points)
        if n < 3:
            return points

        hull = []
        leftmost = min(points, key=lambda p: p[0])
        current = leftmost

        while True:
            hull.append(current)
            next_point = points[0]

            for candidate in points:
                if candidate == current:
                    continue

                cross = (next_point[0] - current[0]) * (candidate[1] - current[1]) - \
                        (next_point[1] - current[1]) * (candidate[0] - current[0])

                if cross < 0 or (cross == 0 and
                                 self.distance(current, candidate) > self.distance(current, next_point)):
                    next_point = candidate

            current = next_point
            if current == hull[0]:
                break

        return hull

    def draw_hull(self, hull):
        if len(hull) < 2:
            return

        if self.current_hull_id:
            self.canvas.delete(self.current_hull_id)

        for i in range(len(hull)):
            p1 = hull[i]
            p2 = hull[(i + 1) % len(hull)]
            self.current_hull_id = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                           fill="red", width=2, tags="hull")

    def show_internal_normals(self):
        n = len(self.vertices)
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]

            edge_x = p2[0] - p1[0]
            edge_y = p2[1] - p1[1]

            normal_x = -edge_y
            normal_y = edge_x

            length = math.sqrt(normal_x ** 2 + normal_y ** 2)
            if length > 0:
                normal_x /= length
                normal_y /= length

            center_x = (p1[0] + p2[0]) / 2
            center_y = (p1[1] + p2[1]) / 2

            end_x = center_x + normal_x * 20
            end_y = center_y + normal_y * 20
            self.canvas.create_line(center_x, center_y, end_x, end_y,
                                    arrow="last", fill="green", width=2, tags="normal")

    def check_segment_intersection(self, event):
        if not hasattr(self, 'segment_start'):
            self.segment_start = (event.x, event.y)
            self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                    fill="blue", tags="segment_point")
            print(f"Начало отрезка установлено в ({event.x}, {event.y})")
        else:
            self.segment_end = (event.x, event.y)
            self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                    fill="blue", tags="segment_point")
            self.canvas.create_line(self.segment_start[0], self.segment_start[1],
                                    self.segment_end[0], self.segment_end[1],
                                    fill="purple", width=2, tags="segment_line")

            self.canvas.delete("intersection")

            intersections = self.segment_polygon_intersections(self.segment_start, self.segment_end)

            if intersections:
                print(f"Найдено {len(intersections)} точек пересечения:")
                for pt in intersections:
                    print(f"({pt[0]:.1f}, {pt[1]:.1f})")
            else:
                print("Пересечений не найдено")

            del self.segment_start

    def segment_polygon_intersections(self, seg_start, seg_end):
        intersections = []
        n = len(self.vertices)

        for i in range(n):
            poly_start = self.vertices[i]
            poly_end = self.vertices[(i + 1) % n]
            pt = self.segment_intersection(seg_start, seg_end, poly_start, poly_end)
            if pt:
                intersections.append(pt)
                self.canvas.create_oval(pt[0] - 4, pt[1] - 4, pt[0] + 4, pt[1] + 4,
                                        fill="orange", tags="intersection")
        return intersections

    def segment_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if denom == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            x_rounded = round(x, 1)
            y_rounded = round(y, 1)

            return (x_rounded, y_rounded)
        return None

    def check_point_in_polygon(self, event):
        point = (event.x, event.y)
        inside = self.point_in_polygon(point)

        color = "green" if inside else "red"
        self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                fill=color, tags="point_check")

        status = "внутри" if inside else "снаружи"
        print(f"Точка ({event.x}, {event.y}) находится {status} многоугольника")

    def point_in_polygon(self, point):
        x, y = point
        n = len(self.vertices)
        inside = False

        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]

            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside

        return inside

    def distance(self, p, q):
        return math.hypot(q[0] - p[0], q[1] - p[1])