#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ Desktop v2.5
Estilo macOS Golden Gate 27 / Liquid Glass
+ Widgets
+ Seafari (navegador ligero)
+ IDE y 3D independientes
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
from datetime import datetime

BG       = "#0a0a12"
GLASS    = "#141422"
PANEL    = "#1c1c2e"
ACCENT   = "#ff2d55"
TEXT     = "#f5f5f7"
TEXT_DIM = "#8e8e93"
DOCK_BG  = "#1a1a28"

class Desktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ · Golden Gate")
        self.root.configure(bg=BG)
        try:
            self.root.geometry("1024x700")
        except Exception:
            pass

        self.root.bind("<Escape>", lambda e: self.salir())

        self._barra_superior()
        self._area()
        self._widgets()
        self._dock()
        self._tick()

    def _barra_superior(self):
        bar = tk.Frame(self.root, bg=GLASS, height=30)
        bar.pack(side=tk.TOP, fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="  ●  Español++", fg=ACCENT, bg=GLASS,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=6)

        for m in ("Archivo", "Editar", "Ver", "Ir", "Ventana", "Ayuda"):
            tk.Label(bar, text=m, fg=TEXT_DIM, bg=GLASS,
                     font=("Segoe UI", 9), padx=7).pack(side=tk.LEFT)

        self.reloj_top = tk.Label(bar, text="", fg=TEXT, bg=GLASS, font=("Segoe UI", 10))
        self.reloj_top.pack(side=tk.RIGHT, padx=12)

    def _area(self):
        self.area = tk.Frame(self.root, bg=BG)
        self.area.pack(fill=tk.BOTH, expand=True)

    def _widget(self, w, h, x, y):
        f = tk.Frame(self.area, bg=PANEL, width=w, height=h,
                     highlightbackground="#2c2c3e", highlightthickness=1)
        f.place(x=x, y=y)
        f.pack_propagate(False)
        tk.Frame(f, bg=ACCENT, height=2).pack(fill=tk.X)
        return f

    def _widgets(self):
        # Reloj
        w = self._widget(260, 140, 30, 30)
        self.lbl_hora = tk.Label(w, text="00:00", font=("Segoe UI", 34, "bold"),
                                 bg=PANEL, fg=TEXT)
        self.lbl_hora.pack(pady=(18, 0))
        self.lbl_fecha = tk.Label(w, text="", font=("Segoe UI", 10), bg=PANEL, fg=TEXT_DIM)
        self.lbl_fecha.pack()

        # Bienvenida
        w2 = self._widget(260, 100, 30, 190)
        tk.Label(w2, text="Liquid Glass", font=("Segoe UI", 13, "bold"),
                 bg=PANEL, fg=ACCENT).pack(pady=(16, 2))
        tk.Label(w2, text="Golden Gate 27 style", font=("Segoe UI", 9),
                 bg=PANEL, fg=TEXT_DIM).pack()

        # Atajos
        w3 = self._widget(260, 210, 30, 310)
        tk.Label(w3, text="Atajos", font=("Segoe UI", 11, "bold"),
                 bg=PANEL, fg=TEXT).pack(pady=(10, 6))
        for txt, cmd in [
            ("🔥  Español++ IDE", self.abrir_ide),
            ("🎨  3D Studio", self.abrir_3d),
            ("🌐  Seafari", self.abrir_navegador),
            ("📂  Archivos", self.explorador),
        ]:
            tk.Button(w3, text=txt, command=cmd, bg="#252538", fg=TEXT,
                      relief=tk.FLAT, anchor="w", padx=10,
                      activebackground=ACCENT).pack(fill=tk.X, padx=10, pady=2)

        # Sistema
        w4 = self._widget(240, 120, 320, 30)
        tk.Label(w4, text="Sistema", font=("Segoe UI", 11, "bold"),
                 bg=PANEL, fg=TEXT).pack(pady=(12, 4))
        tk.Label(w4, text="iSH · Alpine Linux\nPython + Tkinter\nVNC Session", 
                 font=("Segoe UI", 9), bg=PANEL, fg=TEXT_DIM, justify="left").pack()

    def _dock(self):
        cont = tk.Frame(self.root, bg=BG)
        cont.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        dock = tk.Frame(cont, bg=DOCK_BG, height=60,
                        highlightbackground="#33334a", highlightthickness=1)
        dock.pack()
        dock.pack_propagate(False)

        items = [
            ("🔥", self.abrir_ide),
            ("🎨", self.abrir_3d),
            ("🌐", self.abrir_navegador),
            ("📂", self.explorador),
            ("💻", self.terminal),
            ("⏻", self.salir),
        ]
        for emoji, cmd in items:
            tk.Button(dock, text=emoji, command=cmd, bg=DOCK_BG, fg=TEXT,
                      font=("Segoe UI", 16), relief=tk.FLAT, width=3,
                      activebackground=ACCENT, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=6)

    def _tick(self):
        now = datetime.now()
        self.lbl_hora.config(text=now.strftime("%H:%M"))
        self.lbl_fecha.config(text=now.strftime("%A %d %B").capitalize())
        self.reloj_top.config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick)

    def _lanzar(self, script):
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":1")
        rutas = [
            os.path.expanduser(f"~/Espanol-PlusPlus/{script}"),
            os.path.join(os.getcwd(), script),
        ]
        for r in rutas:
            if os.path.exists(r):
                subprocess.Popen([sys.executable, r], env=env, start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
        messagebox.showwarning("No encontrado", f"No está {script}")

    def abrir_ide(self):
        self._lanzar("espanolpp_ide.py")

    def abrir_3d(self):
        self._lanzar("espanolpp_ide.py")
        self.root.after(1200, lambda: messagebox.showinfo("3D", "Abre el IDE y pulsa el botón 3D Studio"))

    def abrir_navegador(self):
        self._lanzar("navegador.py")

    def explorador(self):
        win = tk.Toplevel(self.root)
        win.title("Archivos")
        win.geometry("500x380")
        win.configure(bg=BG)
        ruta = tk.StringVar(value=os.path.expanduser("~"))

        def listar():
            lb.delete(0, tk.END)
            try:
                for i in sorted(os.listdir(ruta.get())):
                    icon = "📁 " if os.path.isdir(os.path.join(ruta.get(), i)) else "📄 "
                    lb.insert(tk.END, icon + i)
            except Exception as e:
                lb.insert(tk.END, str(e))

        def entrar(_):
            sel = lb.curselection()
            if not sel: return
            nom = lb.get(sel[0])[2:]
            nueva = os.path.join(ruta.get(), nom)
            if os.path.isdir(nueva):
                ruta.set(nueva)
                listar()

        tk.Label(win, textvariable=ruta, bg=GLASS, fg=TEXT, anchor="w").pack(fill=tk.X)
        tk.Button(win, text="⬆ Subir", command=lambda: (ruta.set(os.path.dirname(ruta.get()) or "/"), listar()),
                  bg=PANEL, fg=TEXT, relief=tk.FLAT).pack(anchor="w", padx=4, pady=2)
        lb = tk.Listbox(win, bg="#101018", fg=TEXT, font=("Consolas", 11), selectbackground=ACCENT)
        lb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        lb.bind("<Double-1>", entrar)
        listar()

    def terminal(self):
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":1")
            subprocess.Popen(["xterm", "-bg", "#0a0a12", "-fg", "#00ff9d"], env=env, start_new_session=True)
        except Exception:
            messagebox.showinfo("Terminal", "Usa la terminal de iSH")

    def salir(self):
        if messagebox.askyesno("Salir", "¿Cerrar escritorio?\n(IDE, 3D y Seafari seguirán abiertos)"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    Desktop().run()
