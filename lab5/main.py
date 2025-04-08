import tkinter as tk
from tkinter import ttk, Menu
from PolygonEditor import PolygonEditor


class LineEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Графический редактор")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = self.start_y = None
        self.end_x = self.end_y = None
        self.algorithm = "CDA"
        self.hull_method = "Graham"

        self.create_menu()
        self.create_toolbar()
        self.create_status_bar()

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<Motion>", self.track_mouse)

        self.polygon_editor = None
        self.current_mode = "line" 

    def create_menu(self):
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        # Меню алгоритмов
        algo_menu = Menu(menu_bar, tearoff=0)
        algo_menu.add_command(label="ЦДА", command=lambda: self.set_algorithm("CDA"))
        algo_menu.add_command(label="Брезенхем", command=lambda: self.set_algorithm("Bresenham"))
        algo_menu.add_command(label="Ву", command=lambda: self.set_algorithm("Wu"))
        menu_bar.add_cascade(label="Алгоритм", menu=algo_menu)

        # Меню режимов
        mode_menu = Menu(menu_bar, tearoff=0)
        mode_menu.add_command(label="Режим линий", command=self.enable_line_mode)
        mode_menu.add_command(label="Режим полигонов", command=self.enable_polygon_mode)
        menu_bar.add_cascade(label="Режим", menu=mode_menu)

        # Меню методов выпуклой оболочки
        hull_menu = Menu(menu_bar, tearoff=0)
        hull_menu.add_command(label="Метод Грэхема", command=lambda: self.set_hull_method("Graham"))
        hull_menu.add_command(label="Метод Джарвиса", command=lambda: self.set_hull_method("Jarvis"))
        menu_bar.add_cascade(label="Выпуклая оболочка", menu=hull_menu)

    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=tk.X)

        # Выбор алгоритма линии
        ttk.Label(toolbar, text="Алгоритм линии:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value=self.algorithm)
        algo_combobox = ttk.Combobox(toolbar, textvariable=self.algo_var,
                                     values=["CDA", "Bresenham", "Wu"], state="readonly")
        algo_combobox.pack(side=tk.LEFT)
        algo_combobox.bind("<<ComboboxSelected>>", lambda e: self.set_algorithm(self.algo_var.get()))

        # Выбор метода выпуклой оболочки
        ttk.Label(toolbar, text="Метод оболочки:").pack(side=tk.LEFT, padx=(10, 0))
        self.hull_var = tk.StringVar(value=self.hull_method)
        hull_combobox = ttk.Combobox(toolbar, textvariable=self.hull_var,
                                     values=["Graham", "Jarvis"], state="readonly")
        hull_combobox.pack(side=tk.LEFT)
        hull_combobox.bind("<<ComboboxSelected>>", lambda e: self.set_hull_method(self.hull_var.get()))

        # Кнопки переключения режимов
        ttk.Button(toolbar, text="Режим линий", command=self.enable_line_mode).pack(side=tk.LEFT, padx=10)
        ttk.Button(toolbar, text="Режим полигонов", command=self.enable_polygon_mode).pack(side=tk.LEFT)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Готово. Режим: линии")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def track_mouse(self, event):
        if self.current_mode == "line" and self.start_x is not None:
            self.status_var.set(
                f"Рисование линии из ({self.start_x}, {self.start_y}) в ({event.x}, {event.y})")

    def enable_line_mode(self):
        self.current_mode = "line"
        self.clear_canvas_editors()
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Double-Button-1>")
        self.canvas.unbind("<Button-3>")

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.status_var.set("Режим: рисование линий")

    def enable_polygon_mode(self):
        self.current_mode = "polygon"
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")

        if not self.polygon_editor:
            self.polygon_editor = PolygonEditor(self.canvas)

        self.polygon_editor.hull_method = self.hull_method
        self.status_var.set(
            "Режим: построение полигонов. ЛКМ - добавить вершину, ПКМ - проверить точку, Ctrl+ЛКМ - проверить отрезок")

    def clear_canvas_editors(self):
        self.polygon_editor = None

    def set_algorithm(self, algo):
        self.algorithm = algo
        print(f"Алгоритм изменён на: {algo}")

    def set_hull_method(self, method):
        self.hull_method = method
        if self.polygon_editor:
            self.polygon_editor.hull_method = method
        print(f"Метод выпуклой оболочки изменён на: {method}")

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, event.y

    def end_draw(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.draw_line()

    def draw_line(self):
        if None in [self.start_x, self.start_y, self.end_x, self.end_y]:
            return

        self.canvas.delete("line")  # Удаляем предыдущую линию

        if self.algorithm == "CDA":
            self.draw_cda()
        elif self.algorithm == "Bresenham":
            self.draw_bresenham()
        elif self.algorithm == "Wu":
            self.draw_wu()

    def draw_cda(self):
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return

        x_inc = dx / steps
        y_inc = dy / steps
        x, y = self.start_x, self.start_y

        for _ in range(steps + 1):
            self.canvas.create_oval(x, y, x + 1, y + 1,
                                    fill="black", tags="line")
            x += x_inc
            y += y_inc

    def draw_bresenham(self):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = self.end_x, self.end_y

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.canvas.create_oval(x1, y1, x1 + 1, y1 + 1,
                                    fill="black", tags="line")

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def draw_wu(self):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = self.end_x, self.end_y

        def plot(x, y, c):
            intensity = int(255 * (1 - c))
            color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
            self.canvas.create_oval(x, y, x + 1, y + 1,
                                    fill=color, outline="", tags="line")

        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1

        # Первая конечная точка
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = 1 - (x1 + 0.5) % 1
        xpxl1 = xend
        ypxl1 = int(yend)

        if steep:
            plot(ypxl1, xpxl1, 1 - (yend % 1) * xgap)
            plot(ypxl1 + 1, xpxl1, (yend % 1) * xgap)
        else:
            plot(xpxl1, ypxl1, 1 - (yend % 1) * xgap)
            plot(xpxl1, ypxl1 + 1, (yend % 1) * xgap)

        intery = yend + gradient

        # Вторая конечная точка
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = (x2 + 0.5) % 1
        xpxl2 = xend
        ypxl2 = int(yend)

        if steep:
            plot(ypxl2, xpxl2, 1 - (yend % 1) * xgap)
            plot(ypxl2 + 1, xpxl2, (yend % 1) * xgap)
        else:
            plot(xpxl2, ypxl2, 1 - (yend % 1) * xgap)
            plot(xpxl2, ypxl2 + 1, (yend % 1) * xgap)

        # Основной цикл
        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                plot(int(intery), x, 1 - (intery % 1))
                plot(int(intery) + 1, x, intery % 1)
            else:
                plot(x, int(intery), 1 - (intery % 1))
                plot(x, int(intery) + 1, intery % 1)
            intery += gradient


if __name__ == "__main__":
    app = LineEditor()
    app.mainloop()