#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ Mini Desktop
Escritorio simple hecho 100% en Python + Tkinter
Pensado para funcionar dentro de iSH + VNC
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import subprocess
import time
from datetime import datetime

class MiniDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ Desktop")
        self.root.attributes("-fullscreen", True)  # Intentar pantalla completa
        self.root.configure(bg="#0f0f1a")

        # Colores
        self.bg = "#0f0f1a"
        self.panel = "#1a1a2e"
        self.accent = "#e94560"
        self.fg = "#eaeaea"
        self.button_bg = "#16213e"

        self.root.bind("<Escape>", lambda e: self.salir())

        self.crear_interfaz()
        self.actualizar_reloj()

    def crear_interfaz(self):
        # === Fondo / área principal ===
        self.area = tk.Frame(self.root, bg=self.bg)
        self.area.pack(fill=tk.BOTH, expand=True)

        # Título grande
        titulo = tk.Label(
            self.area,
            text="Español++ Desktop",
            font=("Segoe UI", 28, "bold"),
            bg=self.bg,
            fg=self.accent
        )
        titulo.pack(pady=(40, 5))

        sub = tk.Label(
            self.area,
            text="Mini escritorio para iSH · Hecho en Python",
            font=("Segoe UI", 11),
            bg=self.bg,
            fg="#888"
        )
        sub.pack()

        # Reloj grande
        self.reloj = tk.Label(
            self.area,
            text="",
            font=("Consolas", 42, "bold"),
            bg=self.bg,
            fg=self.fg
        )
        self.reloj.pack(pady=30)

        self.fecha = tk.Label(
            self.area,
            text="",
            font=("Segoe UI", 14),
            bg=self.bg,
            fg="#aaa"
        )
        self.fecha.pack()

        # === Dock inferior ===
        dock = tk.Frame(self.root, bg=self.panel, height=70)
        dock.pack(side=tk.BOTTOM, fill=tk.X)
        dock.pack_propagate(False)

        # Botones del dock
        botones = [
            ("🔥  Español++ IDE", self.abrir_ide),
            ("📂  Archivos", self.explorador),
            ("💻  Terminal", self.terminal),
            ("🎨  3D Studio", self.abrir_3d),
            ("ℹ️  Info", self.info),
            ("⏻  Salir", self.salir),
        ]

        for texto, comando in botones:
            btn = tk.Button(
                dock,
                text=texto,
                command=comando,
                bg=self.button_bg,
                fg=self.fg,
                activebackground=self.accent,
                activeforeground="white",
                relief=tk.FLAT,
                font=("Segoe UI", 10),
                padx=14,
                pady=8,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=6, pady=12)

    def actualizar_reloj(self):
        ahora = datetime.now()
        self.reloj.config(text=ahora.strftime("%H:%M:%S"))
        self.fecha.config(text=ahora.strftime("%A %d de %B %Y").capitalize())
        self.root.after(1000, self.actualizar_reloj)

    def abrir_ide(self):
        ruta = os.path.expanduser("~/Espanol-PlusPlus/espanolpp_ide.py")
        if not os.path.exists(ruta):
            # Buscar en el directorio actual
            ruta = os.path.join(os.getcwd(), "espanolpp_ide.py")

        if os.path.exists(ruta):
            try:
                subprocess.Popen(["python3", ruta], env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")})
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el IDE:\n{e}")
        else:
            messagebox.showwarning("No encontrado", "No encontré espanolpp_ide.py\nAsegúrate de estar en la carpeta correcta.")

    def abrir_3d(self):
        # Abrimos el IDE y el usuario puede pulsar el botón 3D Studio
        # O lanzamos directamente si queremos
        messagebox.showinfo("3D Studio", "Abre el Español++ IDE y pulsa el botón\n«3D Studio» en la barra de herramientas.")
        self.abrir_ide()

    def explorador(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Explorador de archivos")
        ventana.geometry("600x450")
        ventana.configure(bg=self.bg)

        ruta_actual = tk.StringVar(value=os.path.expanduser("~"))

        def listar():
            lista.delete(0, tk.END)
            path = ruta_actual.get()
            try:
                for item in sorted(os.listdir(path)):
                    full = os.path.join(path, item)
                    prefijo = "📁 " if os.path.isdir(full) else "📄 "
                    lista.insert(tk.END, prefijo + item)
            except Exception as e:
                lista.insert(tk.END, f"Error: {e}")

        def entrar(event=None):
            sel = lista.curselection()
            if not sel:
                return
            nombre = lista.get(sel[0])[2:]  # quitar emoji
            nueva = os.path.join(ruta_actual.get(), nombre)
            if os.path.isdir(nueva):
                ruta_actual.set(nueva)
                listar()

        def subir():
            padre = os.path.dirname(ruta_actual.get())
            ruta_actual.set(padre)
            listar()

        tk.Label(ventana, textvariable=ruta_actual, bg=self.panel, fg=self.fg,
                 anchor="w", padx=8).pack(fill=tk.X)

        frame_btn = tk.Frame(ventana, bg=self.bg)
        frame_btn.pack(fill=tk.X, pady=4)
        tk.Button(frame_btn, text="⬆ Subir", command=subir, bg=self.button_bg,
                  fg=self.fg, relief=tk.FLAT).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Actualizar", command=listar, bg=self.button_bg,
                  fg=self.fg, relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        lista = tk.Listbox(ventana, bg="#0a0a12", fg=self.fg, font=("Consolas", 11),
                           selectbackground=self.accent)
        lista.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        lista.bind("<Double-1>", entrar)

        listar()

    def terminal(self):
        # Intentamos abrir xterm si existe, si no mostramos una terminal simulada
        try:
            subprocess.Popen(["xterm", "-geometry", "100x30"],
                             env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")})
        except FileNotFoundError:
            self.terminal_simulada()

    def terminal_simulada(self):
        win = tk.Toplevel(self.root)
        win.title("Terminal (simulada)")
        win.geometry("700x400")
        win.configure(bg="#0a0a12")

        output = tk.Text(win, bg="#0a0a12", fg="#00ff99", font=("Consolas", 11),
                         insertbackground="#00ff99")
        output.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        output.insert(tk.END, "Terminal simulada de Español++ Desktop\n")
        output.insert(tk.END, "Escribe comandos simples (ls, pwd, echo...)\n\n")
        output.insert(tk.END, "$ ")

        def ejecutar(event):
            linea = output.get("end-1c linestart", "end-1c").replace("$ ", "").strip()
            output.insert(tk.END, "\n")
            if linea in ("exit", "salir", "quit"):
                win.destroy()
                return
            try:
                if linea.startswith("cd "):
                    os.chdir(linea[3:].strip() or os.path.expanduser("~"))
                    res = ""
                else:
                    res = subprocess.check_output(linea, shell=True, stderr=subprocess.STDOUT, text=True)
                output.insert(tk.END, res)
            except Exception as e:
                output.insert(tk.END, str(e) + "\n")
            output.insert(tk.END, "$ ")
            output.see(tk.END)
            return "break"

        output.bind("<Return>", ejecutar)

    def info(self):
        messagebox.showinfo(
            "Español++ Desktop",
            "Mini escritorio hecho en Python\n\n"
            "· Diseñado para iSH + VNC\n"
            "· No necesita Openbox ni Tint2\n"
            "· Todo corre sobre Tkinter\n\n"
            "Botones:\n"
            "🔥 IDE de Español++\n"
            "📂 Explorador de archivos\n"
            "💻 Terminal\n"
            "🎨 3D Studio (desde el IDE)\n\n"
            "Pulsa Escape o el botón Salir para cerrar."
        )

    def salir(self):
        if messagebox.askyesno("Salir", "¿Cerrar el escritorio?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MiniDesktop()
    app.run()
