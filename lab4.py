import pygame
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Transformations")

angle_x, angle_y, angle_z = 0, 0, 0
scale = 1.0
distance = 5
translate_x, translate_y, translate_z = 0, 0, 0
vertices, faces = np.array([]), np.array([])

def load_object(filename):
    global vertices, faces

    vertices = []
    faces = []

    try:
        with open(filename, 'r') as file:
            reading_faces = False
            for line in file:
                if line.startswith("#") or line.strip() == "":
                    reading_faces = True
                    continue

                parts = line.strip().split()
                if reading_faces:
                    faces.append(list(map(int, parts)))
                else:
                    vertices.append(list(map(float, parts)))

        vertices = np.array(vertices)
        faces = np.array(faces)

        if vertices.size == 0 or faces.size == 0:
            raise ValueError("Invalid object file format or empty content.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load 3D object: {e}")
        vertices = np.array([])
        faces = np.array([])

def transform(matrix, vertices):
    if vertices.size == 0:
        return vertices

    if vertices.ndim != 2 or vertices.shape[1] != 3:
        messagebox.showerror("Error", "Invalid vertex format.")
        return vertices

    vertices = np.hstack((vertices, np.ones((len(vertices), 1))))
    return np.dot(vertices, matrix.T)[:, :3]

def draw_object():
    screen.fill(WHITE)

    if vertices.size == 0 or faces.size == 0:
        return

    rx = np.array([
        [1, 0, 0, 0],
        [0, math.cos(angle_x), -math.sin(angle_x), 0],
        [0, math.sin(angle_x), math.cos(angle_x), 0],
        [0, 0, 0, 1]
    ])

    ry = np.array([
        [math.cos(angle_y), 0, math.sin(angle_y), 0],
        [0, 1, 0, 0],
        [-math.sin(angle_y), 0, math.cos(angle_y), 0],
        [0, 0, 0, 1]
    ])

    rz = np.array([
        [math.cos(angle_z), -math.sin(angle_z), 0, 0],
        [math.sin(angle_z), math.cos(angle_z), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    scale_matrix = np.array([
        [scale, 0, 0, 0],
        [0, scale, 0, 0],
        [0, 0, scale, 0],
        [0, 0, 0, 1]
    ])

    translation_matrix = np.array([
        [1, 0, 0, translate_x],
        [0, 1, 0, translate_y],
        [0, 0, 1, translate_z],
        [0, 0, 0, 1]
    ])

    transformation = np.dot(rx, ry)
    transformation = np.dot(transformation, rz)
    transformation = np.dot(transformation, scale_matrix)
    transformation = np.dot(translation_matrix, transformation)

    transformed_vertices = transform(transformation, vertices)

    projected_vertices = np.array([
        [x / (z + distance), y / (z + distance), z]
        for x, y, z in transformed_vertices
    ])

    offset = np.array([WIDTH // 2, HEIGHT // 2])
    projected_vertices[:, :2] *= 200
    projected_vertices[:, :2] += offset

    for face in faces:
        points = [projected_vertices[i][:2] for i in face]
        pygame.draw.polygon(screen, GRAY, points, 1)

    pygame.display.flip()

def pygame_render():
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_object()
        clock.tick(60)

    pygame.quit()

def gui():
    global angle_x, angle_y, angle_z, scale, distance
    global translate_x, translate_y, translate_z
    global x_slider, y_slider, z_slider, scale_slider, distance_slider
    global tx_slider, ty_slider, tz_slider

    def update_values():
        global angle_x, angle_y, angle_z, scale, distance, translate_x, translate_y, translate_z
        angle_x = math.radians(x_slider.get())
        angle_y = math.radians(y_slider.get())
        angle_z = math.radians(z_slider.get())
        scale = scale_slider.get()
        distance = distance_slider.get()
        translate_x = tx_slider.get()
        translate_y = ty_slider.get()
        translate_z = tz_slider.get()

    def load_file():
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            load_object(filename)

    def reset_values():
        x_slider.set(0)
        y_slider.set(0)
        z_slider.set(0)
        scale_slider.set(1.0)
        distance_slider.set(5.0)
        tx_slider.set(0)
        ty_slider.set(0)
        tz_slider.set(0)
        update_values()

    root = tk.Tk()
    root.title("3D Transformations GUI")
    root.geometry("400x700")

    ttk.Button(root, text="Load 3D Object", command=load_file).pack(pady=10)

    ttk.Label(root, text="Rotate X").pack()
    x_slider = ttk.Scale(root, from_=-180, to=180, command=lambda _: update_values())
    x_slider.pack()

    ttk.Label(root, text="Rotate Y").pack()
    y_slider = ttk.Scale(root, from_=-180, to=180, command=lambda _: update_values())
    y_slider.pack()

    ttk.Label(root, text="Rotate Z").pack()
    z_slider = ttk.Scale(root, from_=-180, to=180, command=lambda _: update_values())
    z_slider.pack()

    ttk.Label(root, text="Scale").pack()
    scale_slider = ttk.Scale(root, from_=0.1, to=5.0, command=lambda _: update_values())
    scale_slider.set(1.0)
    scale_slider.pack()

    ttk.Label(root, text="Perspective Distance").pack()
    distance_slider = ttk.Scale(root, from_=1.0, to=10.0, command=lambda _: update_values())
    distance_slider.set(5.0)
    distance_slider.pack()

    ttk.Label(root, text="Translate X").pack()
    tx_slider = ttk.Scale(root, from_=-10.0, to=10.0, command=lambda _: update_values())
    tx_slider.pack()

    ttk.Label(root, text="Translate Y").pack()
    ty_slider = ttk.Scale(root, from_=-10.0, to=10.0, command=lambda _: update_values())
    ty_slider.pack()

    ttk.Label(root, text="Translate Z").pack()
    tz_slider = ttk.Scale(root, from_=-10.0, to=10.0, command=lambda _: update_values())
    tz_slider.pack()

    ttk.Button(root, text="Reset", command=reset_values).pack(pady=10)
    ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    import threading
    threading.Thread(target=pygame_render, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    gui()
