#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seafari - Navegador ligero estilo Safari para Español++ Desktop
Permite ver repositorios y páginas de texto/HTML simple.
No es un motor real (WebKit), pero sirve para GitHub y docs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request
import re
import ssl

class Seafari(tk.Toplevel):
    def __init__(self, parent=None, url_inicial="https://github.com/jesusxal777-boop/Espanol-PlusPlus"):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()
            self.withdraw()  # si se lanza solo

        self.title("Seafari — Navegador Español++")
        self.geometry("900x600")
        self.configure(bg="#1c1c1e")

        # Barra superior estilo Safari
        barra = tk.Frame(self, bg="#2c2c2e", height=42)
        barra.pack(fill=tk.X)
        barra.pack_propagate(False)

        # Botones tráfico
        for color in ("#ff5f57", "#febc2e", "#28c840"):
            tk.Canvas(barra, width=12, height=12, bg="#2c2c2e", highlightthickness=0).create_oval(2, 2, 11, 11, fill=color, outline="")
            # simplificado
        tk.Label(barra, text="  ● ● ●", bg="#2c2c2e", fg="#888", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)

        tk.Button(barra, text="←", command=self.atras, bg="#3a3a3c", fg="white",
                  relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(barra, text="→", command=self.adelante, bg="#3a3a3c", fg="white",
                  relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(barra, text="↻", command=self.recargar, bg="#3a3a3c", fg="white",
                  relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)

        self.url_var = tk.StringVar(value=url_inicial)
        entrada = tk.Entry(barra, textvariable=self.url_var, bg="#3a3a3c", fg="white",
                           insertbackground="white", relief=tk.FLAT, font=("Segoe UI", 11))
        entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        entrada.bind("<Return>", lambda e: self.navegar())

        tk.Button(barra, text="Ir", command=self.navegar, bg="#0a84ff", fg="white",
                  relief=tk.FLAT, padx=12).pack(side=tk.LEFT, padx=6)

        # Área de contenido
        self.contenido = scrolledtext.ScrolledText(
            self, bg="#000000", fg="#e5e5e7", font=("Menlo", 11),
            relief=tk.FLAT, wrap=tk.WORD, insertbackground="white"
        )
        self.contenido.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.historial = []
        self.pos_hist = -1

        # Cargar página inicial
        self.after(200, self.navegar)

        if parent is None:
            self.deiconify()
            self.mainloop()

    def navegar(self):
        url = self.url_var.get().strip()
        if not url.startswith("http"):
            url = "https://" + url
            self.url_var.set(url)

        self.contenido.delete("1.0", tk.END)
        self.contenido.insert(tk.END, f"Cargando {url} ...\n")
        self.update()

        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(url, headers={"User-Agent": "Seafari/1.0 (Español++)"})
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                raw = resp.read()
                try:
                    html = raw.decode("utf-8")
                except Exception:
                    html = raw.decode("latin-1", errors="ignore")

            texto = self._html_a_texto(html)
            self.contenido.delete("1.0", tk.END)
            self.contenido.insert(tk.END, texto)

            # Historial
            if not self.historial or self.historial[self.pos_hist] != url:
                self.historial = self.historial[:self.pos_hist+1]
                self.historial.append(url)
                self.pos_hist = len(self.historial) - 1

        except Exception as e:
            self.contenido.delete("1.0", tk.END)
            self.contenido.insert(tk.END, f"No se pudo cargar la página.\n\nError: {e}\n\n")
            self.contenido.insert(tk.END, "Prueba con:\nhttps://github.com/jesusxal777-boop/Espanol-PlusPlus\n")

    def _html_a_texto(self, html):
        # Limpieza muy básica de HTML → texto legible
        html = re.sub(r"(?is)<script.*?>.*?</script>", "", html)
        html = re.sub(r"(?is)<style.*?>.*?</style>", "", html)
        html = re.sub(r"(?is)<!--.*?-->", "", html)
        html = re.sub(r"(?i)<br\s*/?>", "\n", html)
        html = re.sub(r"(?i)<p.*?>", "\n\n", html)
        html = re.sub(r"(?i)<h[1-6].?>", "\n\n### ", html)
        html = re.sub(r"(?i)<li.*?>", "\n• ", html)
        html = re.sub(r"(?i)<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", r"\2 [\1]", html)
        html = re.sub(r"<[^>]+>", "", html)
        html = re.sub(r"&nbsp;", " ", html)
        html = re.sub(r"&amp;", "&", html)
        html = re.sub(r"&lt;", "<", html)
        html = re.sub(r"&gt;", ">", html)
        html = re.sub(r"\n{3,}", "\n\n", html)
        return html.strip()[:30000]  # limitar tamaño

    def atras(self):
        if self.pos_hist > 0:
            self.pos_hist -= 1
            self.url_var.set(self.historial[self.pos_hist])
            self.navegar()

    def adelante(self):
        if self.pos_hist < len(self.historial) - 1:
            self.pos_hist += 1
            self.url_var.set(self.historial[self.pos_hist])
            self.navegar()

    def recargar(self):
        self.navegar()


if __name__ == "__main__":
    Seafari()
