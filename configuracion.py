#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del Español++ Desktop
Permite corregir fecha/hora (muy útil en iSH) y otras opciones.
"""

import tkinter as tk
from tkinter import messagebox
import os
import json
from datetime import datetime, timedelta

CONFIG_PATH = os.path.expanduser("~/.espanolpp_config.json")

def cargar_config():
    defaults = {
        "offset_horas": 0,
        "offset_minutos": 0,
        "offset_dias": 0,
        "formato_24h": True,
        "tema": "liquid_glass",
    }
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
    except Exception:
        pass
    return defaults

def guardar_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
        return False

def hora_ajustada(cfg=None):
    """Devuelve datetime actual + offsets de configuración."""
    if cfg is None:
        cfg = cargar_config()
    ahora = datetime.now()
    delta = timedelta(
        days=int(cfg.get("offset_dias", 0)),
        hours=int(cfg.get("offset_horas", 0)),
        minutes=int(cfg.get("offset_minutos", 0)),
    )
    return ahora + delta

class Configuracion:
    def __init__(self):
        self.cfg = cargar_config()

        self.root = tk.Tk()
        self.root.title("Configuración — Español++")
        self.root.geometry("420x480")
        self.root.configure(bg="#1a1a2e")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        # Barra superior con cerrar
        top = tk.Frame(self.root, bg="#16213e", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Button(top, text="✕ Cerrar", command=self.cerrar,
                  bg="#ff5f57", fg="white", relief=tk.FLAT,
                  font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Label(top, text="Configuración", bg="#16213e", fg="#eaeaea",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=8)

        # Contenido
        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(frame, text="Ajuste de fecha y hora", bg="#1a1a2e", fg="#ff2d55",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        tk.Label(frame, text="En iSH la hora del sistema suele estar mal.\nUsa estos offsets para corregirla.",
                 bg="#1a1a2e", fg="#aaa", font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(0, 12))

        # Offsets
        self.var_horas = tk.IntVar(value=self.cfg.get("offset_horas", 0))
        self.var_mins  = tk.IntVar(value=self.cfg.get("offset_minutos", 0))
        self.var_dias  = tk.IntVar(value=self.cfg.get("offset_dias", 0))

        self._fila(frame, "Offset horas (−12 a +14):", self.var_horas, -12, 14)
        self._fila(frame, "Offset minutos (−59 a +59):", self.var_mins, -59, 59)
        self._fila(frame, "Offset días (−30 a +30):", self.var_dias, -30, 30)

        # Vista previa
        tk.Label(frame, text="Hora actual ajustada:", bg="#1a1a2e", fg="#ccc",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(16, 4))

        self.preview = tk.Label(frame, text="", bg="#0f3460", fg="#a8e6cf",
                                font=("Consolas", 14, "bold"), padx=12, pady=8)
        self.preview.pack(fill=tk.X)
        self._actualizar_preview()

        # Botones
        btns = tk.Frame(frame, bg="#1a1a2e")
        btns.pack(pady=20)

        tk.Button(btns, text="💾 Guardar", command=self.guardar,
                  bg="#e94560", fg="white", relief=tk.FLAT,
                  font=("Segoe UI", 10, "bold"), padx=16, pady=6).pack(side=tk.LEFT, padx=6)

        tk.Button(btns, text="Restablecer", command=self.restablecer,
                  bg="#0f3460", fg="white", relief=tk.FLAT,
                  padx=12, pady=6).pack(side=tk.LEFT, padx=6)

        # Actualizar preview cada segundo
        self.root.after(1000, self._tick_preview)

        self.root.mainloop()

    def _fila(self, parent, texto, variable, desde, hasta):
        f = tk.Frame(parent, bg="#1a1a2e")
        f.pack(fill=tk.X, pady=4)
        tk.Label(f, text=texto, bg="#1a1a2e", fg="#ddd", width=28, anchor="w").pack(side=tk.LEFT)
        spin = tk.Spinbox(f, from_=desde, to=hasta, textvariable=variable, width=6,
                          bg="#0f3460", fg="white", buttonbackground="#16213e")
        spin.pack(side=tk.LEFT)
        spin.bind("<KeyRelease>", lambda e: self._actualizar_preview())
        spin.bind("<ButtonRelease-1>", lambda e: self._actualizar_preview())

    def _cfg_temp(self):
        return {
            "offset_horas": self.var_horas.get(),
            "offset_minutos": self.var_mins.get(),
            "offset_dias": self.var_dias.get(),
            "formato_24h": True,
            "tema": "liquid_glass",
        }

    def _actualizar_preview(self):
        try:
            h = hora_ajustada(self._cfg_temp())
            self.preview.config(text=h.strftime("%A %d/%m/%Y  %H:%M:%S"))
        except Exception:
            self.preview.config(text="(error en valores)")

    def _tick_preview(self):
        self._actualizar_preview()
        self.root.after(1000, self._tick_preview)

    def guardar(self):
        self.cfg = self._cfg_temp()
        if guardar_config(self.cfg):
            messagebox.showinfo("Guardado", "Configuración guardada.\nReinicia el escritorio para ver los cambios.", parent=self.root)

    def restablecer(self):
        self.var_horas.set(0)
        self.var_mins.set(0)
        self.var_dias.set(0)
        self._actualizar_preview()

    def cerrar(self):
        self.root.destroy()


if __name__ == "__main__":
    Configuracion()
