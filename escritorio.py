#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ Desktop v2.7
Liquid Glass + reloj corregible con configuracion.py
"""

import tkinter as tk
from tkinter import messagebox
import os, sys, subprocess
from datetime import datetime, timedelta
import json

BG, GLASS, PANEL, ACCENT = "#0a0a12", "#141422", "#1c1c2e", "#ff2d55"
TEXT, TEXT_DIM, DOCK_BG = "#f5f5f7", "#8e8e93", "#1a1a28"
CONFIG_PATH = os.path.expanduser("~/.espanolpp_config.json")

def cargar_cfg():
    d = {"offset_horas": 0, "offset_minutos": 0, "offset_dias": 0}
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                d.update(json.load(f))
    except Exception:
        pass
    return d

def ahora_ajustada():
    cfg = cargar_cfg()
    return datetime.now() + timedelta(
        days=int(cfg.get("offset_dias", 0)),
        hours=int(cfg.get("offset_horas", 0)),
        minutes=int(cfg.get("offset_minutos", 0)),
    )

class Desktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ Desktop")
        self.root.configure(bg=BG)
        self.root.geometry("1000x680")
        self.root.protocol("WM_DELETE_WINDOW", self.salir)

        self._barra()
        self._area()
        self._widgets()
        self._dock()
        self._tick()
        self.root.mainloop()

    def _barra(self):
        bar = tk.Frame(self.root, bg=GLASS, height=32)
        bar.pack(side=tk.TOP, fill=tk.X)
        bar.pack_propagate(False)

        tk.Button(bar, text="✕", command=self.salir, bg="#ff5f57", fg="white",
                  relief=tk.FLAT, font=("Segoe UI", 9, "bold"), width=3).pack(side=tk.LEFT, padx=6, pady=4)

        tk.Label(bar, text="Español++ Desktop", fg=ACCENT, bg=GLASS,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        self.reloj = tk.Label(bar, text="", fg=TEXT, bg=GLASS, font=("Segoe UI", 10))
        self.reloj.pack(side=tk.RIGHT, padx=12)

    def _area(self):
        self.area = tk.Frame(self.root, bg=BG)
        self.area.pack(fill=tk.BOTH, expand=True)

    def _w(self, w, h, x, y):
        f = tk.Frame(self.area, bg=PANEL, width=w, height=h,
                     highlightbackground="#2c2c3e", highlightthickness=1)
        f.place(x=x, y=y)
        f.pack_propagate(False)
        tk.Frame(f, bg=ACCENT, height=2).pack(fill=tk.X)
        return f

    def _widgets(self):
        w = self._w(250, 130, 25, 25)
        self.hora = tk.Label(w, text="00:00", font=("Segoe UI", 32, "bold"), bg=PANEL, fg=TEXT)
        self.hora.pack(pady=(16,0))
        self.fecha = tk.Label(w, text="", font=("Segoe UI", 10), bg=PANEL, fg=TEXT_DIM)
        self.fecha.pack()

        w2 = self._w(250, 250, 25, 175)
        tk.Label(w2, text="Aplicaciones", font=("Segoe UI", 11, "bold"), bg=PANEL, fg=TEXT).pack(pady=(10,6))
        for t, c in [
            ("🔥  Español++ IDE", self.ide),
            ("🎨  Studio 3D", self.studio3d),
            ("✏️  Studio 2D", self.studio2d),
            ("🌐  Seafari", self.navegador),
            ("📂  Archivos", self.archivos),
            ("⚙️  Configuración", self.config),
        ]:
            tk.Button(w2, text=t, command=c, bg="#252538", fg=TEXT, relief=tk.FLAT,
                      anchor="w", padx=10, activebackground=ACCENT).pack(fill=tk.X, padx=10, pady=2)

    def _dock(self):
        cont = tk.Frame(self.root, bg=BG)
        cont.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        dock = tk.Frame(cont, bg=DOCK_BG, height=56, highlightbackground="#333", highlightthickness=1)
        dock.pack()
        dock.pack_propagate(False)

        for emoji, cmd in [("🔥", self.ide), ("🎨", self.studio3d), ("✏️", self.studio2d),
                           ("🌐", self.navegador), ("⚙️", self.config), ("⏻", self.salir)]:
            tk.Button(dock, text=emoji, command=cmd, bg=DOCK_BG, fg=TEXT,
                      font=("Segoe UI", 15), relief=tk.FLAT, width=3,
                      activebackground=ACCENT).pack(side=tk.LEFT, padx=4, pady=5)

    def _tick(self):
        n = ahora_ajustada()
        self.hora.config(text=n.strftime("%H:%M"))
        self.fecha.config(text=n.strftime("%A %d %B %Y").capitalize())
        self.reloj.config(text=n.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick)

    def _run(self, script):
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":1")
        for r in [os.path.expanduser(f"~/Espanol-PlusPlus/{script}"), os.path.join(os.getcwd(), script)]:
            if os.path.exists(r):
                subprocess.Popen([sys.executable, r], env=env, start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
        messagebox.showwarning("No encontrado", script, parent=self.root)

    def ide(self): self._run("espanolpp_ide.py")
    def studio3d(self):
        self._run("espanolpp_ide.py")
        self.root.after(1000, lambda: messagebox.showinfo("3D", "En el IDE pulsa el botón 3D Studio", parent=self.root))
    def studio2d(self): self._run("studio2d.py")
    def navegador(self): self._run("navegador.py")
    def config(self): self._run("configuracion.py")

    def archivos(self):
        win = tk.Toplevel(self.root)
        win.title("Archivos")
        win.geometry("480x360")
        win.configure(bg=BG)
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        top = tk.Frame(win, bg=GLASS, height=36)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Button(top, text="✕ Cerrar", command=win.destroy, bg="#ff5f57", fg="white",
                  relief=tk.FLAT, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=6, pady=4)

        ruta = tk.StringVar(value=os.path.expanduser("~"))
        tk.Label(win, textvariable=ruta, bg=GLASS, fg=TEXT, anchor="w").pack(fill=tk.X)

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

        tk.Button(win, text="⬆ Subir", command=lambda: (ruta.set(os.path.dirname(ruta.get()) or "/"), listar()),
                  bg=PANEL, fg=TEXT, relief=tk.FLAT).pack(anchor="w", padx=4, pady=2)

        lb = tk.Listbox(win, bg="#101018", fg=TEXT, font=("Consolas", 11), selectbackground=ACCENT)
        lb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        lb.bind("<Double-1>", entrar)
        listar()

    def salir(self):
        if messagebox.askyesno("Salir", "¿Cerrar el escritorio?\n(Las demás apps seguirán abiertas)", parent=self.root):
            self.root.destroy()

if __name__ == "__main__":
    Desktop()
