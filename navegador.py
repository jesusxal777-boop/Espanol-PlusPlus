#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seafari v1.1 - Navegador ligero estilo Safari
- Botón de cerrar visible
- Interfaz más estable
- Menos bloqueos al cargar páginas
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import urllib.request
import re
import ssl
import threading

class Seafari:
    def __init__(self, url_inicial="https://github.com/jesusxal777-boop/Espanol-PlusPlus"):
        self.root = tk.Tk()
        self.root.title("Seafari")
        self.root.geometry("860x580")
        self.root.configure(bg="#1c1c1e")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)  # X de la ventana

        self.historial = []
        self.pos = -1
        self.cargando = False

        self._crear_barra(url_inicial)
        self._crear_contenido()
        self._crear_barra_estado()

        # Cargar página inicial en segundo plano
        self.root.after(300, lambda: self.navegar(url_inicial))

        self.root.mainloop()

    def _crear_barra(self, url_inicial):
        barra = tk.Frame(self.root, bg="#2c2c2e", height=44)
        barra.pack(fill=tk.X)
        barra.pack_propagate(False)

        # Semáforos (solo visuales) + botón cerrar real
        frame_izq = tk.Frame(barra, bg="#2c2c2e")
        frame_izq.pack(side=tk.LEFT, padx=8)

        # Botón CERRAR bien visible
        btn_cerrar = tk.Button(
            frame_izq, text="✕",
            command=self.cerrar,
            bg="#ff5f57", fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, width=3,
            activebackground="#ff3b30",
            cursor="hand2"
        )
        btn_cerrar.pack(side=tk.LEFT, padx=(0, 6))

        # Botones navegación
        for txt, cmd in [("←", self.atras), ("→", self.adelante), ("↻", self.recargar)]:
            tk.Button(
                frame_izq, text=txt, command=cmd,
                bg="#3a3a3c", fg="white", relief=tk.FLAT,
                width=3, font=("Segoe UI", 10),
                activebackground="#48484a"
            ).pack(side=tk.LEFT, padx=1)

        # Campo de URL
        self.url_var = tk.StringVar(value=url_inicial)
        self.entrada = tk.Entry(
            barra, textvariable=self.url_var,
            bg="#3a3a3c", fg="white", insertbackground="white",
            relief=tk.FLAT, font=("Segoe UI", 11)
        )
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        self.entrada.bind("<Return>", lambda e: self.navegar())

        # Botón Ir
        tk.Button(
            barra, text="Ir", command=self.navegar,
            bg="#0a84ff", fg="white", relief=tk.FLAT,
            padx=14, font=("Segoe UI", 10, "bold"),
            activebackground="#0071e3"
        ).pack(side=tk.LEFT, padx=(0, 10))

    def _crear_contenido(self):
        self.texto = scrolledtext.ScrolledText(
            self.root,
            bg="#000000",
            fg="#e5e5e7",
            font=("Menlo", 11),
            relief=tk.FLAT,
            wrap=tk.WORD,
            insertbackground="white"
        )
        self.texto.pack(fill=tk.BOTH, expand=True)

    def _crear_barra_estado(self):
        self.estado = tk.Label(
            self.root, text="Listo", anchor="w",
            bg="#1c1c1e", fg="#8e8e93",
            font=("Segoe UI", 9), padx=8
        )
        self.estado.pack(fill=tk.X, side=tk.BOTTOM)

    def cerrar(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def navegar(self, url=None):
        if self.cargando:
            return

        if url is None:
            url = self.url_var.get().strip()

        if not url:
            return

        if not url.startswith("http"):
            url = "https://" + url
            self.url_var.set(url)

        self.cargando = True
        self.estado.config(text=f"Cargando {url} ...")
        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, "Cargando...\nPor favor espera.\n")
        self.root.update_idletasks()

        # Cargar en hilo para no congelar la interfaz
        hilo = threading.Thread(target=self._cargar, args=(url,), daemon=True)
        hilo.start()

    def _cargar(self, url):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Seafari/1.1 (Español++ Desktop)"}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                raw = resp.read()
                try:
                    html = raw.decode("utf-8")
                except Exception:
                    html = raw.decode("latin-1", errors="ignore")

            texto = self._limpiar_html(html)

            # Actualizar UI desde el hilo principal
            self.root.after(0, lambda: self._mostrar(texto, url))

        except Exception as e:
            self.root.after(0, lambda: self._error(str(e)))

    def _mostrar(self, texto, url):
        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, texto)
        self.estado.config(text=f"Listo — {url}")
        self.cargando = False

        # Historial
        if not self.historial or self.historial[self.pos] != url:
            self.historial = self.historial[:self.pos + 1]
            self.historial.append(url)
            self.pos = len(self.historial) - 1

    def _error(self, msg):
        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, "No se pudo cargar la página.\n\n")
        self.texto.insert(tk.END, f"Error: {msg}\n\n")
        self.texto.insert(tk.END, "Prueba con:\n")
        self.texto.insert(tk.END, "https://github.com/jesusxal777-boop/Espanol-PlusPlus\n")
        self.estado.config(text="Error al cargar")
        self.cargando = False

    def _limpiar_html(self, html):
        html = re.sub(r"(?is)<script.*?>.*?</script>", "", html)
        html = re.sub(r"(?is)<style.*?>.*?</style>", "", html)
        html = re.sub(r"(?is)<!--.*?-->", "", html)
        html = re.sub(r"(?i)<br\s*/?>", "\n", html)
        html = re.sub(r"(?i)<p[^>]*>", "\n\n", html)
        html = re.sub(r"(?i)<h[1-6][^>]*>", "\n\n# ", html)
        html = re.sub(r"(?i)<li[^>]*>", "\n• ", html)
        html = re.sub(r"(?i)<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", r"\2 (\1)", html)
        html = re.sub(r"<[^>]+>", "", html)
        html = re.sub(r"&nbsp;", " ", html)
        html = re.sub(r"&amp;", "&", html)
        html = re.sub(r"&lt;", "<", html)
        html = re.sub(r"&gt;", ">", html)
        html = re.sub(r"&quot;", '"', html)
        html = re.sub(r"\n{3,}", "\n\n", html)
        return html.strip()[:35000]

    def atras(self):
        if self.pos > 0:
            self.pos -= 1
            url = self.historial[self.pos]
            self.url_var.set(url)
            self.navegar(url)

    def adelante(self):
        if self.pos < len(self.historial) - 1:
            self.pos += 1
            url = self.historial[self.pos]
            self.url_var.set(url)
            self.navegar(url)

    def recargar(self):
        self.navegar()


if __name__ == "__main__":
    Seafari()
