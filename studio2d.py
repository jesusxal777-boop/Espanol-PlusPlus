#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E++ Studio 2D - Animación pixel por pixel
Dibuja frame a frame con el cursor.
Todo tiene botón de cerrar.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser
import json
import os

class Studio2D:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E++ Studio 2D — Pixel Animation")
        self.root.geometry("820x620")
        self.root.configure(bg="#1a1a2e")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.cols = 32
        self.rows = 24
        self.pixel = 16
        self.frame_actual = 0
        self.frames = []          # lista de matrices de color
        self.color = "#ff2d55"
        self.dibujando = False

        self._nuevo_frame()
        self._ui()
        self._redibujar()

        self.root.mainloop()

    def _nuevo_frame(self):
        matriz = [["#0a0a12" for _ in range(self.cols)] for _ in range(self.rows)]
        self.frames.append(matriz)

    def _ui(self):
        # Barra superior con CERRAR bien visible
        top = tk.Frame(self.root, bg="#16213e", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Button(top, text="✕ Cerrar", command=self.cerrar,
                  bg="#ff5f57", fg="white", relief=tk.FLAT,
                  font=("Segoe UI", 10, "bold"), padx=10).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Label(top, text="E++ Studio 2D", bg="#16213e", fg="#eaeaea",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10)

        self.lbl_frame = tk.Label(top, text="Frame 1/1", bg="#16213e", fg="#aaa")
        self.lbl_frame.pack(side=tk.RIGHT, padx=12)

        # Canvas de dibujo
        self.canvas = tk.Canvas(self.root, bg="#0a0a12",
                                width=self.cols*self.pixel,
                                height=self.rows*self.pixel,
                                highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<B1-Motion>", self._click)
        self.canvas.bind("<Button-3>", self._borrar)      # click derecho borra
        self.canvas.bind("<B3-Motion>", self._borrar)

        # Controles
        ctrl = tk.Frame(self.root, bg="#1a1a2e")
        ctrl.pack(fill=tk.X, padx=10)

        tk.Button(ctrl, text="🎨 Color", command=self._elegir_color,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        self.muestra = tk.Label(ctrl, text="   ", bg=self.color, width=3)
        self.muestra.pack(side=tk.LEFT, padx=4)

        tk.Button(ctrl, text="+ Frame", command=self._add_frame,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(ctrl, text="◀ Prev", command=self._prev,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(ctrl, text="Next ▶", command=self._next,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(ctrl, text="▶ Play", command=self._play,
                  bg="#e94560", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=6)
        tk.Button(ctrl, text="💾 Guardar", command=self._guardar,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(ctrl, text="📂 Cargar", command=self._cargar,
                  bg="#0f3460", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)

        tk.Label(self.root, text="Click izquierdo = pintar · Click derecho = borrar · Cada frame es una imagen",
                 bg="#1a1a2e", fg="#777", font=("Segoe UI", 9)).pack(pady=6)

    def _redibujar(self):
        self.canvas.delete("all")
        mat = self.frames[self.frame_actual]
        for y in range(self.rows):
            for x in range(self.cols):
                color = mat[y][x]
                self.canvas.create_rectangle(
                    x*self.pixel, y*self.pixel,
                    (x+1)*self.pixel, (y+1)*self.pixel,
                    fill=color, outline="#1a1a2e"
                )
        self.lbl_frame.config(text=f"Frame {self.frame_actual+1}/{len(self.frames)}")

    def _click(self, event):
        x = event.x // self.pixel
        y = event.y // self.pixel
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.frames[self.frame_actual][y][x] = self.color
            self.canvas.create_rectangle(
                x*self.pixel, y*self.pixel,
                (x+1)*self.pixel, (y+1)*self.pixel,
                fill=self.color, outline="#1a1a2e"
            )

    def _borrar(self, event):
        x = event.x // self.pixel
        y = event.y // self.pixel
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.frames[self.frame_actual][y][x] = "#0a0a12"
            self.canvas.create_rectangle(
                x*self.pixel, y*self.pixel,
                (x+1)*self.pixel, (y+1)*self.pixel,
                fill="#0a0a12", outline="#1a1a2e"
            )

    def _elegir_color(self):
        c = colorchooser.askcolor(color=self.color)[1]
        if c:
            self.color = c
            self.muestra.config(bg=c)

    def _add_frame(self):
        # Copia el frame actual como base del nuevo
        import copy
        self.frames.append(copy.deepcopy(self.frames[self.frame_actual]))
        self.frame_actual = len(self.frames) - 1
        self._redibujar()

    def _prev(self):
        if self.frame_actual > 0:
            self.frame_actual -= 1
            self._redibujar()

    def _next(self):
        if self.frame_actual < len(self.frames) - 1:
            self.frame_actual += 1
            self._redibujar()

    def _play(self):
        self._reproducir(0)

    def _reproducir(self, idx):
        if idx >= len(self.frames):
            self.frame_actual = 0
            self._redibujar()
            return
        self.frame_actual = idx
        self._redibujar()
        self.root.after(200, lambda: self._reproducir(idx + 1))

    def _guardar(self):
        path = simpledialog.askstring("Guardar", "Nombre del archivo (sin extensión):", parent=self.root)
        if not path:
            return
        path = path.strip() + ".e2d"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"cols": self.cols, "rows": self.rows, "frames": self.frames}, f)
            messagebox.showinfo("Guardado", f"Animación guardada en:\n{path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def _cargar(self):
        path = simpledialog.askstring("Cargar", "Nombre del archivo .e2d:", parent=self.root)
        if not path:
            return
        if not path.endswith(".e2d"):
            path += ".e2d"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.cols = data["cols"]
            self.rows = data["rows"]
            self.frames = data["frames"]
            self.frame_actual = 0
            self._redibujar()
            messagebox.showinfo("Cargado", "Animación cargada", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def cerrar(self):
        self.root.destroy()


if __name__ == "__main__":
    Studio2D()
