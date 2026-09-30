#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ Desktop v2
Estilo macOS Golden Gate 27 / Liquid Glass
- Barra superior tipo menu bar
- Dock inferior
- Widgets de escritorio
- IDE y 3D Studio se abren independientes (no se cierran al salir del desktop)
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
import sys
from datetime import datetime
import math

# ============================================================
# COLORES ESTILO LIQUID GLASS / GOLDEN GATE 27
# ============================================================
BG          = "#0c0c14"       # Fondo casi negro
PANEL       = "#16162a"       # Paneles
GLASS       = "#1e1e32"       # "Vidrio" oscuro
ACCENT      = "#ff2d55"       # Rosa/rojo Liquid Glass
ACCENT2     = "#bf5af2"       # Morado
TEXT        = "#f5f5f7"       # Texto principal
TEXT_DIM    = "#98989d"       # Texto secundario
DOCK_BG     = "#1c1c2e"
WIDGET_BG   = "#1a1a2e"

class Desktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ Desktop · Golden Gate")
        self.root.configure(bg=BG)

        # Intentar maximizar / fullscreen
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            self.root.geometry("1024x768")

        self.root.bind("<Escape>", lambda e: self.confirmar_salida())

        self.procesos = []          # Para no matar el IDE al cerrar
        self.widgets = []

        self._crear_menu_bar()
        self._crear_area_principal()
        self._crear_widgets()
        self._crear_dock()
        self._actualizar_reloj()

    # ----------------------------------------------------------
    # BARRA SUPERIOR (tipo macOS)
    # ----------------------------------------------------------
    def _crear_menu_bar(self):
        self.menubar = tk.Frame(self.root, bg=GLASS, height=28)
        self.menubar.pack(side=tk.TOP, fill=tk.X)
        self.menubar.pack_propagate(False)

        # Logo / nombre
        tk.Label(self.menubar, text="  ●", fg=ACCENT, bg=GLASS,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(8, 2))
        tk.Label(self.menubar, text="Español++",
                 fg=TEXT, bg=GLASS, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        # Menús falsos (solo visuales)
        for nombre in ["Archivo", "Editar", "Ver", "Ventana", "Ayuda"]:
            lbl = tk.Label(self.menubar, text=nombre, fg=TEXT_DIM, bg=GLASS,
                           font=("Segoe UI", 9), padx=8)
            lbl.pack(side=tk.LEFT)

        # Reloj en la barra (derecha)
        self.reloj_barra = tk.Label(self.menubar, text="", fg=TEXT, bg=GLASS,
                                    font=("SF Pro", 10))
        self.reloj_barra.pack(side=tk.RIGHT, padx=12)

    # ----------------------------------------------------------
    # ÁREA PRINCIPAL + WIDGETS
    # ----------------------------------------------------------
    def _crear_area_principal(self):
        self.area = tk.Frame(self.root, bg=BG)
        self.area.pack(fill=tk.BOTH, expand=True)

    def _crear_widgets(self):
        # Widget: Reloj grande
        self.w_reloj = self._crear_widget(280, 160, 40, 40)
        self.lbl_hora = tk.Label(self.w_reloj, text="00:00", font=("Segoe UI", 36, "bold"),
                                 bg=WIDGET_BG, fg=TEXT)
        self.lbl_hora.pack(pady=(20, 0))
        self.lbl_fecha = tk.Label(self.w_reloj, text="", font=("Segoe UI", 11),
                                  bg=WIDGET_BG, fg=TEXT_DIM)
        self.lbl_fecha.pack()

        # Widget: Bienvenida
        self.w_info = self._crear_widget(280, 120, 40, 220)
        tk.Label(self.w_info, text="Bienvenido", font=("Segoe UI", 14, "bold"),
                 bg=WIDGET_BG, fg=ACCENT).pack(pady=(15, 2))
        tk.Label(self.w_info, text="Español++ Desktop\nLiquid Glass Edition",
                 font=("Segoe UI", 10), bg=WIDGET_BG, fg=TEXT_DIM,
                 justify=tk.CENTER).pack()

        # Widget: Atajos rápidos
        self.w_atajos = self._crear_widget(280, 180, 40, 360)
        tk.Label(self.w_atajos, text="Atajos", font=("Segoe UI", 12, "bold"),
                 bg=WIDGET_BG, fg=TEXT).pack(pady=(10, 6))

        for texto, cmd in [
            ("▶  Abrir Español++ IDE", self.abrir_ide),
            ("🎨  E++ 3D Studio", self.abrir_3d),
            ("📂  Explorador", self.explorador),
        ]:
            b = tk.Button(self.w_atajos, text=texto, command=cmd,
                          bg="#252540", fg=TEXT, relief=tk.FLAT,
                          activebackground=ACCENT, font=("Segoe UI", 9),
                          anchor="w", padx=10)
            b.pack(fill=tk.X, padx=12, pady=3)

        # Widget: Estado del sistema (simulado)
        self.w_sys = self._crear_widget(260, 140, 350, 40)
        tk.Label(self.w_sys, text="Sistema", font=("Segoe UI", 12, "bold"),
                 bg=WIDGET_BG, fg=TEXT).pack(pady=(12, 4))
        self.lbl_sys = tk.Label(self.w_sys, text="iSH · Alpine\nPython 3 · Tkinter\nVNC activo",
                                font=("Segoe UI", 9), bg=WIDGET_BG, fg=TEXT_DIM,
                                justify=tk.LEFT)
        self.lbl_sys.pack()

    def _crear_widget(self, w, h, x, y):
        """Crea un widget con estilo glass."""
        frame = tk.Frame(self.area, bg=WIDGET_BG, width=w, height=h,
                         highlightbackground="#2a2a45", highlightthickness=1)
        frame.place(x=x, y=y)
        frame.pack_propagate(False)
        # Título decorativo superior
        bar = tk.Frame(frame, bg=ACCENT, height=3)
        bar.pack(fill=tk.X)
        self.widgets.append(frame)
        return frame

    # ----------------------------------------------------------
    # DOCK INFERIOR (estilo macOS)
    # ----------------------------------------------------------
    def _crear_dock(self):
        dock_container = tk.Frame(self.root, bg=BG)
        dock_container.pack(side=tk.BOTTOM, fill=tk.X, pady=12)

        self.dock = tk.Frame(dock_container, bg=DOCK_BG, height=64,
                             highlightbackground="#333355", highlightthickness=1)
        self.dock.pack()
        self.dock.pack_propagate(False)

        apps = [
            ("🔥", "IDE", self.abrir_ide),
            ("🎨", "3D", self.abrir_3d),
            ("📂", "Files", self.explorador),
            ("💻", "Term", self.terminal),
            ("ℹ️", "Info", self.info),
            ("⏻", "Salir", self.confirmar_salida),
        ]

        for emoji, tip, cmd in apps:
            btn = tk.Button(
                self.dock, text=emoji, command=cmd,
                bg=DOCK_BG, fg=TEXT, font=("Segoe UI", 18),
                relief=tk.FLAT, width=3, height=1,
                activebackground=ACCENT, cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=6, pady=8)
            # Tooltip simple
            btn.bind("<Enter>", lambda e, t=tip: self.reloj_barra.config(text=t))
            btn.bind("<Leave>", lambda e: self._actualizar_reloj(forzar=True))

    # ----------------------------------------------------------
    # RELOJ
    # ----------------------------------------------------------
    def _actualizar_reloj(self, forzar=False):
        ahora = datetime.now()
        hora = ahora.strftime("%H:%M")
        seg = ahora.strftime("%H:%M:%S")
        fecha = ahora.strftime("%A, %d %B").capitalize()

        self.lbl_hora.config(text=hora)
        self.lbl_fecha.config(text=fecha)
        if not forzar:
            self.reloj_barra.config(text=seg)

        self.root.after(1000, self._actualizar_reloj)

    # ----------------------------------------------------------
    # ACCIONES (procesos independientes)
    # ----------------------------------------------------------
    def _lanzar_independiente(self, script):
        """Lanza un proceso separado para que no muera al cerrar el desktop."""
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":1")

        # Buscar el script
        candidatos = [
            os.path.expanduser(f"~/Espanol-PlusPlus/{script}"),
            os.path.join(os.getcwd(), script),
            script,
        ]
        ruta = None
        for c in candidatos:
            if os.path.exists(c):
                ruta = c
                break

        if not ruta:
            messagebox.showwarning("No encontrado", f"No encontré {script}")
            return

        try:
            # Usamos start_new_session=True para desligar el proceso
            proc = subprocess.Popen(
                [sys.executable, ruta],
                env=env,
                start_new_session=True,   # ← clave: no se cierra con el desktop
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.procesos.append(proc)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir:\n{e}")

    def abrir_ide(self):
        self._lanzar_independiente("espanolpp_ide.py")

    def abrir_3d(self):
        # El 3D Studio está dentro del IDE, así que abrimos el IDE
        # y mostramos un aviso
        self._lanzar_independiente("espanolpp_ide.py")
        self.root.after(1500, lambda: messagebox.showinfo(
            "3D Studio",
            "Se abrió el IDE.\n\nPulsa el botón «3D Studio»\nen la barra de herramientas del IDE."
        ))

    def explorador(self):
        win = tk.Toplevel(self.root)
        win.title("Archivos")
        win.geometry("520x400")
        win.configure(bg=BG)

        ruta = tk.StringVar(value=os.path.expanduser("~"))

        def listar():
            lista.delete(0, tk.END)
            try:
                for item in sorted(os.listdir(ruta.get())):
                    full = os.path.join(ruta.get(), item)
                    icon = "📁 " if os.path.isdir(full) else "📄 "
                    lista.insert(tk.END, icon + item)
            except Exception as e:
                lista.insert(tk.END, f"Error: {e}")

        def entrar(event):
            sel = lista.curselection()
            if not sel:
                return
            nombre = lista.get(sel[0])[2:]
            nueva = os.path.join(ruta.get(), nombre)
            if os.path.isdir(nueva):
                ruta.set(nueva)
                listar()

        def subir():
            ruta.set(os.path.dirname(ruta.get()) or "/")
            listar()

        tk.Label(win, textvariable=ruta, bg=GLASS, fg=TEXT, anchor="w",
                 padx=8, font=("Segoe UI", 9)).pack(fill=tk.X)

        bf = tk.Frame(win, bg=BG)
        bf.pack(fill=tk.X, pady=4)
        tk.Button(bf, text="⬆ Subir", command=subir, bg=PANEL, fg=TEXT,
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        lista = tk.Listbox(win, bg="#12121c", fg=TEXT, font=("Consolas", 11),
                           selectbackground=ACCENT, relief=tk.FLAT)
        lista.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        lista.bind("<Double-1>", entrar)
        listar()

    def terminal(self):
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":1")
            subprocess.Popen(["xterm", "-geometry", "100x30", "-bg", "#0c0c14", "-fg", "#00ff99"],
                             env=env, start_new_session=True)
        except FileNotFoundError:
            messagebox.showinfo("Terminal", "xterm no está instalado.\nUsa la terminal de iSH.")

    def info(self):
        messagebox.showinfo(
            "Español++ Desktop",
            "Versión 2 · Liquid Glass / Golden Gate 27\n\n"
            "· Barra superior estilo macOS\n"
            "· Dock inferior\n"
            "· Widgets de escritorio\n"
            "· IDE y 3D Studio se abren independientes\n\n"
            "Pulsa Escape o el botón ⏻ para salir."
        )

    def confirmar_salida(self):
        if messagebox.askyesno("Salir", "¿Cerrar el escritorio?\n\nLas ventanas del IDE y 3D Studio seguirán abiertas."):
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Desktop().run()
