import tkinter as tk
from tkinter import ttk, Menu


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

        self.create_menu()
        self.create_toolbar()
        self.create_debug_panel()

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

    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=tk.X)

        ttk.Label(toolbar, text="Алгоритм: ").pack(side=tk.LEFT)

        self.algo_var = tk.StringVar(value=self.algorithm)
        algo_selector = ttk.Combobox(toolbar, textvariable=self.algo_var, values=["CDA", "Bresenham", "Wu"],
                                     state="readonly")
        algo_selector.pack(side=tk.LEFT)
        algo_selector.bind("<<ComboboxSelected>>", lambda e: self.set_algorithm(algo_selector.get()))

    def create_debug_panel(self):
        self.debug_frame = ttk.Frame(self, padding=5)
        self.debug_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.debug_label = ttk.Label(self.debug_frame, text="Отладка: Ожидание ввода точек")
        self.debug_label.pack()

        self.debug_text = tk.Text(self.debug_frame, height=10, state=tk.DISABLED)
        self.debug_text.pack(fill=tk.BOTH, expand=True)

    def log_debug(self, text):
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.insert(tk.END, text + "\n")
        self.debug_text.config(state=tk.DISABLED)

    def transform_y(self, y):
        return self.canvas.winfo_height() - y

    def set_algorithm(self, algo):
        self.algorithm = algo
        self.algo_var.set(algo)

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, self.transform_y(event.y)

    def end_draw(self, event):
        self.end_x, self.end_y = event.x, self.transform_y(event.y)
        self.draw_line()

    def draw_line(self):
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.config(state=tk.DISABLED)

        if self.algorithm == "CDA":
            self.draw_cda()
        elif self.algorithm == "Bresenham":
            self.draw_bresenham()
        elif self.algorithm == "Wu":
            self.draw_wu()

    def draw_cda(self):
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        steps = max(abs(dx), abs(dy))    # выбирается единица растра
        x_inc = dx / steps
        y_inc = dy / steps
        x, y = self.start_x, self.start_y

        self.log_debug(f"Итерация\tX\tY\tPlot(X, Y)")
        self.log_debug(f"-----------------------------------------------------------------")

        for i in range(steps + 1):
            self.canvas.create_oval(x, self.transform_y(y), x + 1, self.transform_y(y) + 1, fill="black")
            self.log_debug(f"{i}\t{x:.2f}\t{y:.2f}\t({int(x)}, {int(y)})")
            x += x_inc
            y += y_inc

    def draw_bresenham(self):
        x1, y1, x2, y2 = self.start_x, self.start_y, self.end_x, self.end_y
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        is_steep = dy > dx
        if is_steep:
            dx, dy = dy, dx

        e = 2 * dy - dx

        self.log_debug(f"Итерация\tОшибка e\tX\tY\tКорр. ошибка e'\tPlot(X, Y)")
        self.log_debug(f"-----------------------------------------------------------------")

        for i in range(dx + 1):
            self.canvas.create_oval(x1, self.transform_y(y1), x1 + 1, self.transform_y(y1) + 1, fill="black")


            if i == 0:
                self.log_debug(f"{i}\t---\t{x1}\t{y1}\t---\t({x1}, {y1})")
            else:
                self.log_debug(f"{i}\t{prev_e}\t{x1}\t{y1}\t{e}\t({x1}, {y1})")

            prev_e = e

            if e >= 0:
                if is_steep:
                    x1 += sx
                else:
                    y1 += sy
                e -= 2 * dx

            if is_steep:
                y1 += sy
            else:
                x1 += sx
            e += 2 * dy

    def draw_wu(self):
        def plot(x, y, c):
            color = f"#{int(255 * (1 - c)):02x}{int(255 * (1 - c)):02x}{int(255 * (1 - c)):02x}"
            self.canvas.create_oval(x, self.transform_y(y), x + 1, self.transform_y(y) + 1, fill=color, outline="")

        x1, y1, x2, y2 = self.start_x, self.start_y, self.end_x, self.end_y
        dx = x2 - x1
        dy = y2 - y1
        steep = abs(dy) > abs(dx)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1
        y = y1

        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.insert(tk.END, "Итерация\tX\tY\tИнтенсивность\n")
        self.debug_text.insert(tk.END, "--------------------------------\n")

        for i, x in enumerate(range(x1, x2 + 1)):
            intensity1 = 1 - (y - int(y))
            intensity2 = y - int(y)
            plot(x, int(y), intensity1)
            plot(x, int(y) + 1, intensity2)
            self.log_debug(f"{i}\t{x}\t{int(y)}\t{intensity1:.2f}")
            y += gradient

        self.debug_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = LineEditor()
    app.mainloop()
