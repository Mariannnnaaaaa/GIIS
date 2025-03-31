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

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.add_vertex)
        self.canvas.bind("<Double-Button-1>", self.finish_polygon)
        self.canvas.bind("<Button-3>", self.check_point_in_polygon)  # Right click to check point
        self.canvas.bind("<Control-Button-1>", self.check_segment_intersection)  # Ctrl+click для отрезка
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

        # Вычисление и отображение внутренних нормалей
        if is_convex:
            self.show_internal_normals()

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

        # Находим точку с минимальной y (и минимальной x при равенстве)
        pivot = min(points, key=lambda p: (p[1], p[0]))

        # Сортируем по полярному углу относительно pivot
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

        # Находим самую левую точку
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

            # Вычисляем вектор ребра
            edge_x = p2[0] - p1[0]
            edge_y = p2[1] - p1[1]

            # Нормаль к ребру (повернута на 90 градусов внутрь)
            normal_x = -edge_y
            normal_y = edge_x

            # Нормализуем вектор нормали
            length = math.sqrt(normal_x ** 2 + normal_y ** 2)
            if length > 0:
                normal_x /= length
                normal_y /= length

            # Центр ребра
            center_x = (p1[0] + p2[0]) / 2
            center_y = (p1[1] + p2[1]) / 2

            # Рисуем нормаль
            end_x = center_x + normal_x * 20
            end_y = center_y + normal_y * 20
            self.canvas.create_line(center_x, center_y, end_x, end_y,
                                    arrow="last", fill="green", width=2, tags="normal")

    def check_segment_intersection(self, event):
        """Обработчик для проверки пересечения отрезка с полигоном"""
        if not hasattr(self, 'segment_start'):
            # Первый клик - начало отрезка
            self.segment_start = (event.x, event.y)
            self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                    fill="blue", tags="segment_point")
            print(f"Начало отрезка установлено в ({event.x}, {event.y})")
        else:
            # Второй клик - конец отрезка, ищем пересечения
            self.segment_end = (event.x, event.y)
            self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                    fill="blue", tags="segment_point")
            self.canvas.create_line(self.segment_start[0], self.segment_start[1],
                                    self.segment_end[0], self.segment_end[1],
                                    fill="purple", width=2, tags="segment_line")

            # Очищаем предыдущие пересечения
            self.canvas.delete("intersection")

            # Находим пересечения
            intersections = self.segment_polygon_intersections(self.segment_start, self.segment_end)

            if intersections:
                print(f"Найдено {len(intersections)} точек пересечения:")
                for pt in intersections:
                    print(f"({pt[0]:.1f}, {pt[1]:.1f})")
            else:
                print("Пересечений не найдено")

            # Сбрасываем отрезок
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
        """Точное определение точки пересечения двух отрезков"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # Вычисляем знаменатель
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # Если отрезки параллельны
        if denom == 0:
            return None

        # Вычисляем параметры t и u
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        # Проверяем, что пересечение находится на обоих отрезках
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Вычисляем точку пересечения
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            # Округляем координаты до 1 decimal place для лучшей читаемости
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