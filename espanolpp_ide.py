#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ IDE + Intérprete
Lenguaje de programación en español con toques NSFW light
IDE completo en Python (tkinter)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font as tkfont
import re
import sys
import traceback
from io import StringIO

# ============================================================
# INTÉRPRETE DE ESPAÑOL++
# ============================================================

class EspanolPPError(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(mensaje)

class InterpreteEspanolPP:
    def __init__(self, output_callback=None, input_callback=None):
        self.variables = {}
        self.funciones = {}
        self.output_callback = output_callback or (lambda x: print(x, end=""))
        self.input_callback = input_callback or input
        self.lineas = []
        self.pos = 0

    def imprimir(self, texto):
        self.output_callback(str(texto) + "\n")

    def error(self, msg):
        raise EspanolPPError(f"🔥 Error caliente: {msg}")

    def tokenizar_linea(self, linea):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            return None
        # Quitar comentarios al final
        if "#" in linea:
            linea = linea[:linea.index("#")].strip()
        return linea

    def evaluar_expresion(self, expr):
        expr = expr.strip()
        if not expr:
            return None

        # Booleanos
        if expr == "verdadero" or expr == "caliente":
            return True
        if expr == "falso" or expr == "frio":
            return False

        # Strings entre comillas
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Números
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Variables
        if expr in self.variables:
            return self.variables[expr]

        # Operaciones simples (muy básico)
        # Soporta +, -, *, /, ==, !=, <, >, <=, >=, and, or
        for op in ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/"]:
            if op in expr:
                partes = expr.split(op, 1)
                if len(partes) == 2:
                    izq = self.evaluar_expresion(partes[0].strip())
                    der = self.evaluar_expresion(partes[1].strip())
                    if op == "+":
                        # Concatenación o suma
                        if isinstance(izq, str) or isinstance(der, str):
                            return str(izq) + str(der)
                        return izq + der
                    if op == "-": return izq - der
                    if op == "*": return izq * der
                    if op == "/": return izq / der
                    if op == "==": return izq == der
                    if op == "!=": return izq != der
                    if op == "<": return izq < der
                    if op == ">": return izq > der
                    if op == "<=": return izq <= der
                    if op == ">=": return izq >= der

        # Si llegamos aquí y no es variable conocida
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
            self.error(f"La variable '{expr}' no existe. ¿Olvidaste hacerle un 'mete'?")
        self.error(f"No entiendo la expresión: {expr}")

    def ejecutar_bloque(self, inicio, fin):
        i = inicio
        while i < fin:
            linea = self.tokenizar_linea(self.lineas[i])
            if linea is None:
                i += 1
                continue

            # mete variable = valor
            if linea.startswith("mete "):
                resto = linea[5:].strip()
                if "=" not in resto:
                    self.error("Después de 'mete' necesitas algo como: mete x = 5")
                var, expr = resto.split("=", 1)
                var = var.strip()
                valor = self.evaluar_expresion(expr.strip())
                self.variables[var] = valor
                i += 1
                continue

            # chorrea / mostra / enseña / saca
            if linea.startswith(("chorrea ", "mostra ", "enseña ", "saca ")):
                for pref in ("chorrea ", "mostra ", "enseña ", "saca "):
                    if linea.startswith(pref):
                        expr = linea[len(pref):].strip()
                        valor = self.evaluar_expresion(expr)
                        self.imprimir(valor)
                        break
                i += 1
                continue

            # pide variable
            if linea.startswith("pide "):
                var = linea[5:].strip()
                try:
                    entrada = self.input_callback(f"👉 Ingresa valor para '{var}': ")
                    # Intentar convertir a número si es posible
                    try:
                        if "." in entrada:
                            self.variables[var] = float(entrada)
                        else:
                            self.variables[var] = int(entrada)
                    except ValueError:
                        self.variables[var] = entrada
                except Exception:
                    self.variables[var] = ""
                i += 1
                continue

            # fap (pass)
            if linea == "fap":
                i += 1
                continue

            # mientras condicion
            if linea.startswith("mientras "):
                condicion = linea[9:].strip()
                # Buscar el bloque (indentación simple por ahora: hasta línea vacía o menor indent... simplificado)
                # Versión simple: buscamos el final del bloque por líneas siguientes hasta que no empiecen con espacio o encontremos otro keyword de nivel superior
                bloque_inicio = i + 1
                bloque_fin = bloque_inicio
                while bloque_fin < len(self.lineas):
                    l = self.lineas[bloque_fin].strip()
                    if not l or l.startswith("#"):
                        bloque_fin += 1
                        continue
                    # Si encontramos otro keyword de control al mismo nivel, paramos
                    if l.startswith(("mete ", "chorrea ", "mostra ", "pide ", "si ", "mientras ", "funcion ", "regresa ")) and not self.lineas[bloque_fin].startswith((" ", "\t")):
                        break
                    if l in ("sino", "ven", "sigue") and not self.lineas[bloque_fin].startswith((" ", "\t")):
                        break
                    bloque_fin += 1

                # Ejecutar el while
                max_iter = 10000  # seguridad
                iters = 0
                while self.evaluar_expresion(condicion) and iters < max_iter:
                    self.ejecutar_bloque(bloque_inicio, bloque_fin)
                    iters += 1
                if iters >= max_iter:
                    self.error("Bucle infinito detectado. Tranquilo, respira...")
                i = bloque_fin
                continue

            # si condicion
            if linea.startswith("si "):
                condicion = linea[3:].strip()
                bloque_inicio = i + 1
                bloque_fin = bloque_inicio
                sino_inicio = None

                while bloque_fin < len(self.lineas):
                    l = self.lineas[bloque_fin].strip()
                    if l == "sino":
                        sino_inicio = bloque_fin + 1
                        bloque_fin += 1
                        continue
                    if not l or l.startswith("#"):
                        bloque_fin += 1
                        continue
                    if l.startswith(("mete ", "chorrea ", "mostra ", "pide ", "si ", "mientras ", "funcion ")) and not self.lineas[bloque_fin].startswith((" ", "\t")):
                        break
                    bloque_fin += 1

                if self.evaluar_expresion(condicion):
                    fin_si = sino_inicio - 1 if sino_inicio else bloque_fin
                    self.ejecutar_bloque(bloque_inicio, fin_si)
                elif sino_inicio:
                    self.ejecutar_bloque(sino_inicio, bloque_fin)
                i = bloque_fin
                continue

            # ven (break) - simplificado, solo funciona en contextos limitados
            if linea == "ven":
                raise StopIteration("ven")  # truco para salir

            # Si no reconoce
            self.error(f"No sé qué significa: '{linea}'. ¿Quisiste decir 'chorrea' o 'mete'?")

        return i

    def ejecutar(self, codigo):
        self.variables = {}
        self.lineas = codigo.splitlines()
        self.pos = 0
        try:
            self.ejecutar_bloque(0, len(self.lineas))
        except StopIteration:
            pass  # ven
        except EspanolPPError as e:
            self.imprimir(str(e))
        except Exception as e:
            self.imprimir(f"🔥 Error inesperado: {e}\n{traceback.format_exc()}")


# ============================================================
# IDE CON TKINTER (tema oscuro estilo Liquid Glass)
# ============================================================

class EspanolPPIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ IDE  —  Programa rico, en español")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)

        # Colores estilo Liquid Glass / dark
        self.bg = "#1a1a2e"
        self.panel = "#16213e"
        self.accent = "#e94560"          # rosado caliente
        self.text_bg = "#0f3460"
        self.fg = "#eaeaea"
        self.comment = "#7f8c8d"
        self.keyword = "#ff6b9d"
        self.string = "#a8e6cf"

        self.root.configure(bg=self.bg)

        self.archivo_actual = None
        self.crear_ui()
        self.cargar_ejemplo()

    def crear_ui(self):
        # Menú
        menubar = tk.Menu(self.root, bg=self.panel, fg=self.fg, activebackground=self.accent)
        self.root.config(menu=menubar)

        menu_archivo = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        menu_archivo.add_command(label="Abrir...", command=self.abrir, accelerator="Ctrl+O")
        menu_archivo.add_command(label="Guardar", command=self.guardar, accelerator="Ctrl+S")
        menu_archivo.add_command(label="Guardar como...", command=self.guardar_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)

        menu_ejecutar = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Ejecutar", menu=menu_ejecutar)
        menu_ejecutar.add_command(label="▶ Ejecutar código", command=self.ejecutar, accelerator="F5")
        menu_ejecutar.add_command(label="Limpiar consola", command=self.limpiar_consola)

        menu_ayuda = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Ejemplos", command=self.mostrar_ejemplos)
        menu_ayuda.add_command(label="Referencia rápida", command=self.mostrar_referencia)
        menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)

        # Frame principal
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Estilo ttk oscuro
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg)
        style.configure("TButton", background=self.accent, foreground="white", padding=6)
        style.map("TButton", background=[("active", "#ff6b9d")])

        # Toolbar
        toolbar = tk.Frame(main, bg=self.bg)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        btn_run = tk.Button(toolbar, text="▶  Ejecutar (F5)", command=self.ejecutar,
                            bg=self.accent, fg="white", relief=tk.FLAT, padx=12, pady=4,
                            font=("Segoe UI", 10, "bold"), cursor="hand2")
        btn_run.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = tk.Button(toolbar, text="Limpiar consola", command=self.limpiar_consola,
                              bg=self.panel, fg=self.fg, relief=tk.FLAT, padx=10, pady=4,
                              cursor="hand2")
        btn_clear.pack(side=tk.LEFT, padx=(0, 8))

        btn_ejemplo = tk.Button(toolbar, text="Cargar ejemplo", command=self.cargar_ejemplo,
                                bg=self.panel, fg=self.fg, relief=tk.FLAT, padx=10, pady=4,
                                cursor="hand2")
        btn_ejemplo.pack(side=tk.LEFT)

        # Paned window (editor + consola)
        paned = tk.PanedWindow(main, orient=tk.VERTICAL, bg=self.bg, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)

        # Editor
        editor_frame = tk.Frame(paned, bg=self.bg)
        paned.add(editor_frame, height=420)

        tk.Label(editor_frame, text="  Código Español++", bg=self.panel, fg=self.fg,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X)

        self.editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.NONE, bg=self.text_bg, fg=self.fg,
            insertbackground=self.accent, font=("Consolas", 12),
            relief=tk.FLAT, padx=10, pady=8, undo=True
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self.resaltar_sintaxis)

        # Consola
        consola_frame = tk.Frame(paned, bg=self.bg)
        paned.add(consola_frame, height=200)

        tk.Label(consola_frame, text="  Consola de salida", bg=self.panel, fg=self.fg,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X)

        self.consola = scrolledtext.ScrolledText(
            consola_frame, wrap=tk.WORD, bg="#0a0a12", fg="#a8e6cf",
            insertbackground=self.accent, font=("Consolas", 11),
            relief=tk.FLAT, padx=10, pady=8, state=tk.DISABLED
        )
        self.consola.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status = tk.Label(self.root, text="Listo para programar rico 🔥", bd=0,
                               bg=self.panel, fg=self.fg, anchor="w", padx=10)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        # Atajos
        self.root.bind("<F5>", lambda e: self.ejecutar())
        self.root.bind("<Control-s>", lambda e: self.guardar())
        self.root.bind("<Control-o>", lambda e: self.abrir())
        self.root.bind("<Control-n>", lambda e: self.nuevo())

    def resaltar_sintaxis(self, event=None):
        # Resaltado muy básico
        self.editor.tag_remove("keyword", "1.0", tk.END)
        self.editor.tag_remove("string", "1.0", tk.END)
        self.editor.tag_remove("comment", "1.0", tk.END)

        contenido = self.editor.get("1.0", tk.END)

        # Keywords
        keywords = r"\b(mete|chorrea|mostra|enseña|saca|pide|si|sino|mientras|funcion|regresa|fap|ven|sigue|verdadero|falso|caliente|frio)\b"
        for match in re.finditer(keywords, contenido):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("keyword", start, end)

        # Strings
        for match in re.finditer(r'"[^\"]*"|\'[^\']*\'', contenido):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("string", start, end)

        # Comentarios
        for match in re.finditer(r"#.*", contenido):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("comment", start, end)

        self.editor.tag_config("keyword", foreground=self.keyword)
        self.editor.tag_config("string", foreground=self.string)
        self.editor.tag_config("comment", foreground=self.comment)

    def escribir_consola(self, texto):
        self.consola.config(state=tk.NORMAL)
        self.consola.insert(tk.END, texto)
        self.consola.see(tk.END)
        self.consola.config(state=tk.DISABLED)

    def limpiar_consola(self):
        self.consola.config(state=tk.NORMAL)
        self.consola.delete("1.0", tk.END)
        self.consola.config(state=tk.DISABLED)

    def ejecutar(self):
        self.limpiar_consola()
        codigo = self.editor.get("1.0", tk.END)
        self.status.config(text="Ejecutando... 🔥")

        def output_cb(texto):
            self.escribir_consola(texto)
            self.root.update_idletasks()

        def input_cb(prompt):
            # Diálogo simple para input
            from tkinter.simpledialog import askstring
            return askstring("Entrada requerida", prompt) or ""

        interprete = InterpreteEspanolPP(output_callback=output_cb, input_callback=input_cb)
        try:
            interprete.ejecutar(codigo)
            self.status.config(text="Ejecución terminada ✨")
        except Exception as e:
            self.escribir_consola(f"\n🔥 Error fatal: {e}\n")
            self.status.config(text="Hubo un error")

    def nuevo(self):
        if messagebox.askyesno("Nuevo", "¿Borrar el código actual?"):
            self.editor.delete("1.0", tk.END)
            self.archivo_actual = None
            self.status.config(text="Nuevo archivo")

    def abrir(self):
        path = filedialog.askopenfilename(
            filetypes=[("Español++ files", "*.epp"), ("Todos", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())
            self.archivo_actual = path
            self.resaltar_sintaxis()
            self.status.config(text=f"Abierto: {path}")

    def guardar(self):
        if self.archivo_actual:
            with open(self.archivo_actual, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.status.config(text=f"Guardado: {self.archivo_actual}")
        else:
            self.guardar_como()

    def guardar_como(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".epp",
            filetypes=[("Español++ files", "*.epp"), ("Todos", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.archivo_actual = path
            self.status.config(text=f"Guardado: {path}")

    def cargar_ejemplo(self):
        ejemplo = '''# ========================================
#   Ejemplo de Español++
#   Programa rico y en español
# ========================================

mete nombre = "usuario"
chorrea "Hola " + nombre + " 🔥"
chorrea "Bienvenido a Español++"
chorrea ""

# Contador caliente
mete i = 1
mientras i <= 5
    chorrea "Vueltita número " + i + "... te estás calentando"
    mete i = i + 1

chorrea ""
chorrea "¿Quieres seguir? Escribe si o no:"
pide respuesta

si respuesta == "si"
    chorrea "¡Sigue programando rico!"
sino
    chorrea "Está bien, descansa... pero vuelve pronto 😈"

chorrea ""
chorrea "Fin del ejemplo. Ahora escribe tu propio código."
'''
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", ejemplo)
        self.resaltar_sintaxis()
        self.status.config(text="Ejemplo cargado")

    def mostrar_ejemplos(self):
        messagebox.showinfo("Ejemplos", 
            "Hay un ejemplo cargado por defecto.\n\n"
            "Prueba también:\n\n"
            "mete x = 10\n"
            "chorrea x * 2\n\n"
            "pide edad\n"
            "si edad >= 18\n"
            "    chorrea \"Eres mayor\"\n"
            "sino\n"
            "    chorrea \"Eres menor\"\n"
        )

    def mostrar_referencia(self):
        ref = """
REFERENCIA RÁPIDA DE ESPAÑOL++

mete x = 5          →  crea/asigna variable
chorrea "hola"      →  imprime (también: mostra, enseña, saca)
pide nombre         →  pide valor al usuario
si condicion        →  if
sino                →  else
mientras cond       →  while
fap                 →  no hace nada (pass)
ven                 →  break (sale del bucle)
verdadero / caliente → true
falso / frio        → false
# comentario        →  comentario

Operadores: + - * / == != < > <= >=
"""
        messagebox.showinfo("Referencia Español++", ref)

    def acerca_de(self):
        messagebox.showinfo("Acerca de Español++",
            "Español++ IDE v1.0\n\n"
            "Lenguaje de programación en español\n"
            "con un toque picante 🔥\n\n"
            "Hecho para que programar se sienta rico.\n\n"
            "GitHub: jesusxal777-boop/Espanol-PlusPlus"
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EspanolPPIDE()
    app.run()
