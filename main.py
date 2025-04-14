import tkinter as tk
from tkinter import messagebox
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import numpy as np

class TriangulationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Триангуляция Делоне и диаграмма Вороного")
        self.canvas = tk.Canvas(master, width=500, height=500, bg="white")
        self.canvas.pack()

        self.points = []
        self.canvas.bind("<Button-1>", self.add_point)

        btn_frame = tk.Frame(master)
        btn_frame.pack()

        tk.Button(btn_frame, text="Построить", command=self.build).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Очистить", command=self.clear).pack(side=tk.LEFT)

    def add_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        r = 3
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")

    def clear(self):
        self.points.clear()
        self.canvas.delete("all")

    def build(self):
        if len(self.points) < 3:
            messagebox.showwarning("Недостаточно точек", "Необходимо хотя бы 3 точки.")
            return
        points = np.array(self.points)
        transformed_points = np.array([[p[0], 500 - p[1]] for p in self.points])
        tri = Delaunay(transformed_points)
        vor = Voronoi(transformed_points)

        fig, ax = plt.subplots()
        ax.set_title("Триангуляция Делоне и диаграмма Вороного")
        ax.set_aspect("equal")
        voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='orange', line_width=2)
        ax.triplot(transformed_points[:, 0], transformed_points[:, 1], tri.simplices.copy(), color='blue')
        ax.plot(transformed_points[:, 0], transformed_points[:, 1], 'ko')

        plt.show()

root = tk.Tk()
app = TriangulationApp(root)
root.mainloop()
