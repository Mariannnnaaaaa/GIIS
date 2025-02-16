import tkinter as tk
from tkinter import ttk, Menu
import math


class LineEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Графический редактор")
        self.geometry("1000x600")  

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = self.start_y = None
        self.end_x = self.end_y = None
        self.algorithm = "CDA"
        self.curve_type = "Circle"

        self.create_menu()
        self.create_toolbar()
        self.create_table()  

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

    def create_menu(self):
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        algo_menu = Menu(menu_bar, tearoff=0)
        algo_menu.add_command(label="ЦДА", command=lambda: self.set_algorithm("CDA"))
        algo_menu.add_command(label="Брезенхем", command=lambda: self.set_algorithm("Bresenham"))
        algo_menu.add_command(label="Ву", command=lambda: self.set_algorithm("Wu"))
        menu_bar.add_cascade(label="Алгоритм", menu=algo_menu)

        curve_menu = Menu(menu_bar, tearoff=0)
        curve_menu.add_command(label="Окружность", command=lambda: self.set_curve("Circle"))
        curve_menu.add_command(label="Эллипс", command=lambda: self.set_curve("Ellipse"))
        curve_menu.add_command(label="Гипербола", command=lambda: self.set_curve("Hyperbola"))
        curve_menu.add_command(label="Парабола", command=lambda: self.set_curve("Parabola"))
        menu_bar.add_cascade(label="Линии второго порядка", menu=curve_menu)

    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=tk.X)

        ttk.Label(toolbar, text="Алгоритм: ").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value=self.algorithm)
        algo_selector = ttk.Combobox(toolbar, textvariable=self.algo_var, values=["CDA", "Bresenham", "Wu"], state="readonly")
        algo_selector.pack(side=tk.LEFT)
        algo_selector.bind("<<ComboboxSelected>>", lambda e: self.set_algorithm(algo_selector.get()))

        ttk.Label(toolbar, text="Кривая: ").pack(side=tk.LEFT)
        self.curve_var = tk.StringVar(value=self.curve_type)
        curve_selector = ttk.Combobox(toolbar, textvariable=self.curve_var,
                                      values=["Circle", "Ellipse", "Hyperbola", "Parabola"], state="readonly")
        curve_selector.pack(side=tk.LEFT)
        curve_selector.bind("<<ComboboxSelected>>", lambda e: self.set_curve(curve_selector.get()))

    def create_table(self):
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)

        columns = ["Итерация", "X", "Y", "Plot(X,Y)"]
        self.table = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        self.table.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, anchor="center")

    def log_debug(self, text):
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.insert(tk.END, text + "\n")
        self.debug_text.config(state=tk.DISABLED)

    def transform_y(self, y):
        return self.canvas.winfo_height() - y

    def set_algorithm(self, algo):
        self.algorithm = algo
        self.algo_var.set(algo)

    def set_curve(self, curve):
        self.curve_type = curve
        self.curve_var.set(curve)

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, self.transform_y(event.y)

    def end_draw(self, event):
        self.end_x, self.end_y = event.x, self.transform_y(event.y)
        if self.curve_type == "Circle":
            self.draw_circle()
        elif self.curve_type == "Ellipse":
            self.draw_ellipse()
        elif self.curve_type == "Hyperbola":
            self.draw_hyperbola()
        elif self.curve_type == "Parabola":
            self.draw_parabola()

    def draw_circle(self):
        r = abs(self.end_x - self.start_x)
        x, y = 0, r
        d = 3 - 2 * r

        for row in self.table.get_children():
            self.table.delete(row)

        iteration = 0
        while x <= y:
            for dx, dy in [(x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)]:
                self.canvas.create_oval(self.start_x + dx, self.transform_y(self.start_y + dy),
                                        self.start_x + dx + 1, self.transform_y(self.start_y + dy) + 1, fill="black")
                self.table.insert("", "end", values=[iteration, self.start_x + dx, self.start_y + dy,
                                                     f"Plot({self.start_x + dx}, {self.start_y + dy})"])
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1
            iteration += 1

    def draw_ellipse(self):
        rx = abs(self.end_x - self.start_x)
        ry = abs(self.end_y - self.start_y)
        x, y = 0, ry
        d1 = ry**2 - rx**2 * ry + 0.25 * rx**2
        dx, dy = 2 * ry**2 * x, 2 * rx**2 * y

        for row in self.table.get_children():
            self.table.delete(row)

        iteration = 0
        while dx < dy:
            self.plot_ellipse_points(x, y, iteration)
            if d1 < 0:
                x += 1
                dx += 2 * ry**2
                d1 += dx + ry**2
            else:
                x += 1
                y -= 1
                dx += 2 * ry**2
                dy -= 2 * rx**2
                d1 += dx - dy + ry**2

        d2 = ry**2 * (x + 0.5)**2 + rx**2 * (y - 1)**2 - rx**2 * ry**2
        while y >= 0:
            self.plot_ellipse_points(x, y, iteration)
            if d2 > 0:
                y -= 1
                dy -= 2 * rx**2
                d2 += rx**2 - dy
            else:
                y -= 1
                x += 1
                dx += 2 * ry**2
                dy -= 2 * rx**2
                d2 += dx - dy + rx**2

    def plot_ellipse_points(self, x, y, iteration):
        for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
            self.canvas.create_oval(self.start_x + dx, self.transform_y(self.start_y + dy),
                                    self.start_x + dx + 1, self.transform_y(self.start_y + dy) + 1, fill="black")
            self.table.insert("", "end", values=[iteration, self.start_x + dx, self.start_y + dy,
                                                 f"Plot({self.start_x + dx}, {self.start_y + dy})"])

    def draw_hyperbola(self):
        a = abs(self.end_x - self.start_x)
        b = abs(self.end_y - self.start_y)
        x = a
        iteration = 0

        for row in self.table.get_children():
            self.table.delete(row)

        while x < self.canvas.winfo_width():
            y = b * math.sqrt((x ** 2 / a ** 2) - 1)
            self.plot_symmetric_points(x, y, iteration)
            x += 1
            iteration += 1

    def draw_parabola(self):
        p = abs(self.end_y - self.start_y) // 2
        x = 0
        y = 0
        iteration = 0

        for row in self.table.get_children():
            self.table.delete(row)

        while y < self.canvas.winfo_height():
            y = (x ** 2) / (2 * p)
            self.plot_symmetric_points(x, y, iteration)
            x += 1
            iteration += 1

    def plot_symmetric_points(self, x, y, iteration):
        for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
            self.canvas.create_oval(self.start_x + dx, self.transform_y(self.start_y + dy),
                                    self.start_x + dx + 1, self.transform_y(self.start_y + dy) + 1, fill="black")
            self.table.insert("", "end", values=[iteration, self.start_x + dx, self.start_y + dy,
                                                 f"Plot({self.start_x + dx}, {self.start_y + dy})"])


if __name__ == "__main__":
    app = LineEditor()
    app.mainloop()
