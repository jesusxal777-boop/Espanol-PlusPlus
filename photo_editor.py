#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E++ Photo Editor
Editor de imágenes básico estilo Photoshop
Funciona con Tkinter. Si hay Pillow, activa más filtros.
"""

import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, simpledialog
import os
import copy

# Intentar Pillow (mejores filtros y más formatos)
try:
    from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BG = "#1a1a2e"
PANEL = "#16213e"
ACCENT = "#e94560"
TEXT = "#eaeaea"

class PhotoEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E++ Photo Editor")
        self.root.geometry("960x640")
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.imagen = None          # PIL Image o None
        self.tk_img = None
        self.archivo = None
        self.herramienta = "pincel"
        self.color = "#ff2d55"
        self.grosor = 4
        self.historial = []         # undo simple
        self.zoom = 1.0

        self._ui()
        self.root.mainloop()

    def _ui(self):
        # Barra superior
        top = tk.Frame(self.root, bg=PANEL, height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Button(top, text="✕ Cerrar", command=self.cerrar, bg="#ff5f57", fg="white",
                  relief=tk.FLAT, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=6, pady=5)

        tk.Label(top, text="E++ Photo Editor", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=8)

        if not HAS_PIL:
            tk.Label(top, text="(sin Pillow · funciones limitadas)", bg=PANEL, fg="#888",
                     font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Toolbar
        tools = tk.Frame(self.root, bg=BG)
        tools.pack(fill=tk.X, padx=6, pady=4)

        botones = [
            ("📂 Abrir", self.abrir),
            ("💾 Guardar", self.guardar),
            ("↩ Deshacer", self.deshacer),
            ("🖌️ Pincel", lambda: self._set_tool("pincel")),
            ("🧹 Borrar", lambda: self._set_tool("borrar")),
            ("🎨 Color", self._elegir_color),
            ("⬜ Nuevo", self.nuevo),
        ]
        for txt, cmd in botones:
            tk.Button(tools, text=txt, command=cmd, bg=PANEL, fg=TEXT,
                      relief=tk.FLAT, padx=8, pady=3,
                      activebackground=ACCENT).pack(side=tk.LEFT, padx=2)

        self.lbl_tool = tk.Label(tools, text="Herramienta: pincel", bg=BG, fg="#aaa")
        self.lbl_tool.pack(side=tk.RIGHT, padx=8)

        # Filtros (solo si hay Pillow)
        if HAS_PIL:
            filtros = tk.Frame(self.root, bg=BG)
            filtros.pack(fill=tk.X, padx=6)
            for txt, cmd in [
                ("Grises", self.filtro_grises),
                ("Invertir", self.filtro_invertir),
                ("Blur", self.filtro_blur),
                ("Nitidez", self.filtro_nitidez),
                ("+ Brillo", lambda: self.filtro_brillo(1.2)),
                ("- Brillo", lambda: self.filtro_brillo(0.8)),
                ("Espejo H", self.filtro_espejo_h),
                ("Rotar 90°", self.filtro_rotar),
            ]:
                tk.Button(filtros, text=txt, command=cmd, bg="#0f3460", fg=TEXT,
                          relief=tk.FLAT, padx=6, pady=2).pack(side=tk.LEFT, padx=2)

        # Canvas
        canvas_frame = tk.Frame(self.root, bg="#0a0a12")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.canvas = tk.Canvas(canvas_frame, bg="#0a0a12", highlightthickness=0,
                                cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<B1-Motion>", self._arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self._soltar)

        self.ultimo = None

        # Estado
        self.estado = tk.Label(self.root, text="Listo · Abre una imagen o crea un lienzo nuevo",
                               bg=PANEL, fg="#aaa", anchor="w", padx=8)
        self.estado.pack(fill=tk.X, side=tk.BOTTOM)

    def _set_tool(self, nombre):
        self.herramienta = nombre
        self.lbl_tool.config(text=f"Herramienta: {nombre}")

    def _elegir_color(self):
        c = colorchooser.askcolor(color=self.color, parent=self.root)[1]
        if c:
            self.color = c

    def _guardar_estado(self):
        if self.imagen is not None and HAS_PIL:
            self.historial.append(self.imagen.copy())
            if len(self.historial) > 15:
                self.historial.pop(0)

    def deshacer(self):
        if self.historial:
            self.imagen = self.historial.pop()
            self._mostrar()
            self.estado.config(text="Deshecho")
        else:
            self.estado.config(text="Nada que deshacer")

    def nuevo(self):
        if not HAS_PIL:
            messagebox.showinfo("Info", "Necesitas Pillow para lienzo nuevo.\napk add py3-pillow", parent=self.root)
            return
        w = simpledialog.askinteger("Ancho", "Ancho en píxeles:", initialvalue=400, parent=self.root)
        h = simpledialog.askinteger("Alto", "Alto en píxeles:", initialvalue=300, parent=self.root)
        if w and h:
            self._guardar_estado()
            self.imagen = Image.new("RGB", (w, h), "#1a1a2e")
            self.archivo = None
            self._mostrar()
            self.estado.config(text=f"Lienzo nuevo {w}x{h}")

    def abrir(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Todos", "*.*"),
            ]
        )
        if not path:
            return
        try:
            if HAS_PIL:
                self.imagen = Image.open(path).convert("RGB")
                self.archivo = path
                self.historial.clear()
                self._mostrar()
                self.estado.config(text=f"Abierta: {os.path.basename(path)} ({self.imagen.size[0]}x{self.imagen.size[1]})")
            else:
                # Solo PhotoImage (GIF/PNG básico)
                self.tk_img = tk.PhotoImage(file=path)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
                self.imagen = None
                self.archivo = path
                self.estado.config(text=f"Abierta (modo básico): {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir:\n{e}", parent=self.root)

    def guardar(self):
        if self.imagen is None and self.tk_img is None:
            messagebox.showinfo("Info", "No hay imagen para guardar", parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            if HAS_PIL and self.imagen is not None:
                self.imagen.save(path)
            else:
                messagebox.showinfo("Info", "Guardar completo requiere Pillow", parent=self.root)
                return
            self.archivo = path
            self.estado.config(text=f"Guardada: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def _mostrar(self):
        if self.imagen is None or not HAS_PIL:
            return
        # Ajustar al canvas
        cw = max(self.canvas.winfo_width(), 100)
        ch = max(self.canvas.winfo_height(), 100)
        img = self.imagen.copy()
        img.thumbnail((cw - 20, ch - 20))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.tk_img)

    def _coords_imagen(self, event):
        """Convierte coords del canvas a coords de la imagen (aproximado)."""
        if self.imagen is None:
            return None
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = self.imagen.size
        # thumbnail centrado
        scale = min((cw - 20) / iw, (ch - 20) / ih, 1.0)
        dw, dh = int(iw * scale), int(ih * scale)
        ox = (cw - dw) // 2
        oy = (ch - dh) // 2
        x = int((event.x - ox) / scale)
        y = int((event.y - oy) / scale)
        if 0 <= x < iw and 0 <= y < ih:
            return x, y
        return None

    def _click(self, event):
        self.ultimo = self._coords_imagen(event)
        if self.ultimo and HAS_PIL and self.imagen is not None:
            self._guardar_estado()
            self._pintar(self.ultimo[0], self.ultimo[1])

    def _arrastrar(self, event):
        pos = self._coords_imagen(event)
        if pos and self.ultimo and HAS_PIL and self.imagen is not None:
            self._linea(self.ultimo[0], self.ultimo[1], pos[0], pos[1])
            self.ultimo = pos
            self._mostrar()

    def _soltar(self, event):
        self.ultimo = None
        if HAS_PIL and self.imagen is not None:
            self._mostrar()

    def _pintar(self, x, y):
        draw = ImageDraw.Draw(self.imagen)
        r = self.grosor
        col = self.color if self.herramienta == "pincel" else "#1a1a2e"
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)
        self._mostrar()

    def _linea(self, x1, y1, x2, y2):
        draw = ImageDraw.Draw(self.imagen)
        col = self.color if self.herramienta == "pincel" else "#1a1a2e"
        draw.line([x1, y1, x2, y2], fill=col, width=self.grosor * 2)

    # ---- Filtros ----
    def filtro_grises(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = ImageOps.grayscale(self.imagen).convert("RGB")
        self._mostrar()
        self.estado.config(text="Filtro: escala de grises")

    def filtro_invertir(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = ImageOps.invert(self.imagen)
        self._mostrar()
        self.estado.config(text="Filtro: invertir")

    def filtro_blur(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = self.imagen.filter(ImageFilter.BLUR)
        self._mostrar()
        self.estado.config(text="Filtro: blur")

    def filtro_nitidez(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = self.imagen.filter(ImageFilter.SHARPEN)
        self._mostrar()
        self.estado.config(text="Filtro: nitidez")

    def filtro_brillo(self, factor):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = ImageEnhance.Brightness(self.imagen).enhance(factor)
        self._mostrar()
        self.estado.config(text=f"Brillo x{factor}")

    def filtro_espejo_h(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = ImageOps.mirror(self.imagen)
        self._mostrar()
        self.estado.config(text="Espejo horizontal")

    def filtro_rotar(self):
        if not self._check_pil(): return
        self._guardar_estado()
        self.imagen = self.imagen.rotate(-90, expand=True)
        self._mostrar()
        self.estado.config(text="Rotado 90°")

    def _check_pil(self):
        if not HAS_PIL or self.imagen is None:
            messagebox.showinfo("Info", "Abre una imagen primero (y ten Pillow instalado)", parent=self.root)
            return False
        return True

    def cerrar(self):
        self.root.destroy()


if __name__ == "__main__":
    PhotoEditor()
