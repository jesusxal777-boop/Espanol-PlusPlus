#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ IDE v2.0
- Intérprete mejorado
- Compilador (transpiler a Python)
- Autocompletado básico
- Funciones, listas, para
- E++ 3D Studio (wireframe muy limitado)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import re
import math
import traceback
from typing import Any, Dict, List, Optional, Callable

# ============================================================
# TRANSPILER (Compilador Español++ → Python)
# ============================================================

class CompiladorEspanolPP:
    """Traduce código Español++ a Python ejecutable."""

    KEYWORD_MAP = {
        r'\bmete\b': '',
        r'\bchorrea\b': 'print',
        r'\bmostra\b': 'print',
        r'\benseña\b': 'print',
        r'\bsaca\b': 'print',
        r'\bpide\b': 'input',
        r'\bsi\b': 'if',
        r'\bsino\b': 'else:',
        r'\bmientras\b': 'while',
        r'\bfuncion\b': 'def',
        r'\bregresa\b': 'return',
        r'\bfap\b': 'pass',
        r'\bven\b': 'break',
        r'\bsigue\b': 'continue',
        r'\bverdadero\b': 'True',
        r'\bcaliente\b': 'True',
        r'\bfalso\b': 'False',
        r'\bfrio\b': 'False',
    }

    def compilar(self, codigo: str) -> str:
        lineas = codigo.splitlines()
        resultado = [
            "# Código generado automáticamente por Español++ v2.0",
            "# Puedes ejecutarlo con: python3 archivo.py",
            "",
        ]
        indent = 0
        i = 0

        while i < len(lineas):
            original = lineas[i]
            linea = original.strip()

            if not linea or linea.startswith("#"):
                resultado.append("    " * indent + original.strip())
                i += 1
                continue

            # para i desde X hasta Y
            m = re.match(r'para\s+(\w+)\s+desde\s+(.+)\s+hasta\s+(.+)', linea)
            if m:
                var, inicio, fin = m.group(1), m.group(2), m.group(3)
                resultado.append("    " * indent + f"for {var} in range(int({inicio}), int({fin})+1):")
                indent += 1
                i += 1
                continue

            # funcion nombre(params)
            m = re.match(r'funcion\s+(\w+)\s*\((.*)\)', linea)
            if m:
                nombre, params = m.group(1), m.group(2)
                resultado.append("    " * indent + f"def {nombre}({params}):")
                indent += 1
                i += 1
                continue

            # mete x = expr  →  x = expr
            if linea.startswith("mete "):
                resto = linea[5:].strip()
                resultado.append("    " * indent + resto)
                i += 1
                continue

            # pide x  →  x = input(...)
            if linea.startswith("pide "):
                var = linea[5:].strip()
                resultado.append("    " * indent + f'{var} = input("👉 {var}: ")')
                i += 1
                continue

            # chorrea / mostra etc → print
            for pref in ("chorrea ", "mostra ", "enseña ", "saca "):
                if linea.startswith(pref):
                    expr = linea[len(pref):].strip()
                    resultado.append("    " * indent + f"print({expr})")
                    break
            else:
                # Reemplazos generales
                nueva = linea
                for pat, rep in self.KEYWORD_MAP.items():
                    nueva = re.sub(pat, rep, nueva)

                # si condicion  → if condicion:
                if nueva.startswith("if ") and not nueva.endswith(":"):
                    nueva = nueva + ":"
                if nueva.startswith("while ") and not nueva.endswith(":"):
                    nueva = nueva + ":"
                if nueva.strip() == "else:":
                    indent = max(0, indent - 1)
                    resultado.append("    " * indent + "else:")
                    indent += 1
                    i += 1
                    continue

                resultado.append("    " * indent + nueva)

            i += 1

        return "\n".join(resultado)


# ============================================================
# INTÉRPRETE MEJORADO
# ============================================================

class EspanolPPError(Exception):
    def __init__(self, msg: str):
        super().__init__(f"🔥 Error caliente: {msg}")

class InterpreteEspanolPP:
    def __init__(self, output_cb: Optional[Callable] = None, input_cb: Optional[Callable] = None):
        self.variables: Dict[str, Any] = {}
        self.funciones: Dict[str, Any] = {}
        self.output = output_cb or (lambda x: print(x, end=""))
        self.input_fn = input_cb or input
        self.lineas: List[str] = []

    def out(self, *args):
        self.output(" ".join(str(a) for a in args) + "\n")

    def error(self, msg: str):
        raise EspanolPPError(msg)

    def eval_expr(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return None

        if expr in ("verdadero", "caliente"): return True
        if expr in ("falso", "frio"): return False

        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Lista literal [1, 2, 3]
        if expr.startswith("[") and expr.endswith("]"):
            contenido = expr[1:-1].strip()
            if not contenido:
                return []
            return [self.eval_expr(p.strip()) for p in self._split_args(contenido)]

        # Acceso a lista: nombre[indice]
        m = re.match(r'^(\w+)\[(.+)\]$', expr)
        if m:
            lista = self.variables.get(m.group(1))
            if lista is None:
                self.error(f"La lista '{m.group(1)}' no existe")
            idx = self.eval_expr(m.group(2))
            return lista[int(idx)]

        # Número
        try:
            return float(expr) if "." in expr else int(expr)
        except ValueError:
            pass

        # Variable
        if expr in self.variables:
            return self.variables[expr]

        # Llamada a función: nombre(args)
        m = re.match(r'^(\w+)\((.*)\)$', expr)
        if m:
            nombre, args_str = m.group(1), m.group(2)
            if nombre in self.funciones:
                args = [self.eval_expr(a.strip()) for a in self._split_args(args_str)] if args_str.strip() else []
                return self._llamar_funcion(nombre, args)
            self.error(f"Función '{nombre}' no definida")

        # Operadores (orden de precedencia simplificado)
        for op in ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/"]:
            if op in expr:
                # Buscar el operador fuera de strings y paréntesis (simplificado)
                partes = expr.split(op, 1)
                if len(partes) == 2:
                    izq = self.eval_expr(partes[0])
                    der = self.eval_expr(partes[1])
                    if op == "+":
                        if isinstance(izq, str) or isinstance(der, str):
                            return str(izq) + str(der)
                        return izq + der
                    ops = {"-": lambda a,b: a-b, "*": lambda a,b: a*b, "/": lambda a,b: a/b,
                           "==": lambda a,b: a==b, "!=": lambda a,b: a!=b,
                           "<": lambda a,b: a<b, ">": lambda a,b: a>b,
                           "<=": lambda a,b: a<=b, ">=": lambda a,b: a>=b}
                    return ops[op](izq, der)

        if re.match(r'^[a-zA-Z_]\w*$', expr):
            self.error(f"Variable '{expr}' no existe. Usa 'mete {expr} = ...'")
        self.error(f"No entiendo: {expr}")

    def _split_args(self, s: str) -> List[str]:
        args, actual, nivel = [], [], 0
        for c in s:
            if c == ',' and nivel == 0:
                args.append(''.join(actual))
                actual = []
            else:
                if c == '[': nivel += 1
                elif c == ']': nivel -= 1
                actual.append(c)
        if actual:
            args.append(''.join(actual))
        return args

    def _llamar_funcion(self, nombre: str, args: List[Any]) -> Any:
        func = self.funciones[nombre]
        params, cuerpo = func["params"], func["cuerpo"]
        if len(args) != len(params):
            self.error(f"Función '{nombre}' espera {len(params)} argumentos")
        # Guardar variables anteriores
        backup = {p: self.variables.get(p) for p in params}
        for p, a in zip(params, args):
            self.variables[p] = a
        resultado = None
        try:
            self._ejecutar_bloque(cuerpo[0], cuerpo[1])
        except ReturnValue as r:
            resultado = r.value
        # Restaurar
        for p in params:
            if backup[p] is None:
                self.variables.pop(p, None)
            else:
                self.variables[p] = backup[p]
        return resultado

    def _encontrar_bloque(self, inicio: int) -> int:
        i = inicio
        while i < len(self.lineas):
            l = self.lineas[i].strip()
            if not l or l.startswith("#"):
                i += 1
                continue
            # Heurística simple de fin de bloque
            if (l.startswith(("mete ", "chorrea ", "mostra ", "saca ", "pide ", "si ", "mientras ",
                              "para ", "funcion ", "regresa ")) or l in ("sino", "ven", "sigue")) \
               and not self.lineas[i].startswith((" ", "\t")):
                return i
            i += 1
        return i

    def _ejecutar_bloque(self, inicio: int, fin: int):
        i = inicio
        while i < fin:
            raw = self.lineas[i]
            linea = raw.strip()
            if not linea or linea.startswith("#"):
                i += 1
                continue
            if "#" in linea:
                linea = linea[:linea.index("#")].strip()

            # funcion
            m = re.match(r'funcion\s+(\w+)\s*\((.*)\)', linea)
            if m:
                nombre = m.group(1)
                params = [p.strip() for p in m.group(2).split(",") if p.strip()]
                cuerpo_inicio = i + 1
                cuerpo_fin = self._encontrar_bloque(cuerpo_inicio)
                self.funciones[nombre] = {"params": params, "cuerpo": (cuerpo_inicio, cuerpo_fin)}
                i = cuerpo_fin
                continue

            # regresa
            if linea.startswith("regresa "):
                valor = self.eval_expr(linea[8:].strip()) if len(linea) > 8 else None
                raise ReturnValue(valor)
            if linea == "regresa":
                raise ReturnValue(None)

            # mete
            if linea.startswith("mete "):
                resto = linea[5:].strip()
                if "=" not in resto:
                    self.error("Usa: mete variable = valor")
                var, expr = resto.split("=", 1)
                self.variables[var.strip()] = self.eval_expr(expr.strip())
                i += 1
                continue

            # print variants
            for pref in ("chorrea ", "mostra ", "enseña ", "saca "):
                if linea.startswith(pref):
                    self.out(self.eval_expr(linea[len(pref):].strip()))
                    break
            else:
                # pide
                if linea.startswith("pide "):
                    var = linea[5:].strip()
                    entrada = self.input_fn(f"👉 {var}: ") or ""
                    try:
                        self.variables[var] = float(entrada) if "." in entrada else int(entrada)
                    except ValueError:
                        self.variables[var] = entrada
                    i += 1
                    continue

                # para i desde X hasta Y
                m = re.match(r'para\s+(\w+)\s+desde\s+(.+)\s+hasta\s+(.+)', linea)
                if m:
                    var, inicio_e, fin_e = m.group(1), m.group(2), m.group(3)
                    inicio_v = int(self.eval_expr(inicio_e))
                    fin_v = int(self.eval_expr(fin_e))
                    bloque_ini = i + 1
                    bloque_fin = self._encontrar_bloque(bloque_ini)
                    for val in range(inicio_v, fin_v + 1):
                        self.variables[var] = val
                        try:
                            self._ejecutar_bloque(bloque_ini, bloque_fin)
                        except StopIteration:
                            break
                    i = bloque_fin
                    continue

                # mientras
                if linea.startswith("mientras "):
                    cond = linea[9:].strip()
                    bloque_ini = i + 1
                    bloque_fin = self._encontrar_bloque(bloque_ini)
                    max_iter = 50000
                    n = 0
                    while self.eval_expr(cond) and n < max_iter:
                        try:
                            self._ejecutar_bloque(bloque_ini, bloque_fin)
                        except StopIteration:
                            break
                        n += 1
                    if n >= max_iter:
                        self.error("Bucle infinito. Respira y revisa la condición.")
                    i = bloque_fin
                    continue

                # si / sino
                if linea.startswith("si "):
                    cond = linea[3:].strip()
                    bloque_ini = i + 1
                    sino_ini = None
                    j = bloque_ini
                    while j < len(self.lineas):
                        l = self.lineas[j].strip()
                        if l == "sino":
                            sino_ini = j + 1
                            j += 1
                            continue
                        if (l.startswith(("mete ", "chorrea ", "mostra ", "si ", "mientras ", "para ", "funcion "))
                            or l in ("ven", "sigue")) and not self.lineas[j].startswith((" ", "\t")):
                            break
                        j += 1
                    bloque_fin = j
                    if self.eval_expr(cond):
                        fin = (sino_ini - 1) if sino_ini else bloque_fin
                        self._ejecutar_bloque(bloque_ini, fin)
                    elif sino_ini:
                        self._ejecutar_bloque(sino_ini, bloque_fin)
                    i = bloque_fin
                    continue

                if linea == "fap":
                    i += 1
                    continue
                if linea == "ven":
                    raise StopIteration()
                if linea == "sigue":
                    i += 1
                    continue

                # Posible llamada a función como statement
                m = re.match(r'^(\w+)\((.*)\)$', linea)
                if m and m.group(1) in self.funciones:
                    args = [self.eval_expr(a.strip()) for a in self._split_args(m.group(2))] if m.group(2).strip() else []
                    self._llamar_funcion(m.group(1), args)
                    i += 1
                    continue

                self.error(f"No entiendo la instrucción: '{linea}'")

            i += 1

    def ejecutar(self, codigo: str):
        self.variables.clear()
        self.funciones.clear()
        self.lineas = codigo.splitlines()
        try:
            self._ejecutar_bloque(0, len(self.lineas))
        except ReturnValue:
            pass
        except StopIteration:
            pass
        except EspanolPPError as e:
            self.out(str(e))
        except Exception as e:
            self.out(f"🔥 Error inesperado: {e}\n{traceback.format_exc()}")

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


# ============================================================
# E++ 3D STUDIO (wireframe muy básico)
# ============================================================

class E3DStudio(tk.Toplevel):
    """Ventana simple de animación 3D wireframe."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("E++ 3D Studio (limitado)")
        self.geometry("700x550")
        self.configure(bg="#1a1a2e")

        self.canvas = tk.Canvas(self, bg="#0a0a12", width=680, height=420)
        self.canvas.pack(pady=10)

        ctrl = tk.Frame(self, bg="#1a1a2e")
        ctrl.pack()

        tk.Button(ctrl, text="▶ Animar cubo", command=self.animar_cubo,
                  bg="#e94560", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl, text="Limpiar", command=lambda: self.canvas.delete("all"),
                  bg="#16213e", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        self.angulo = 0
        self.after_id = None

        tk.Label(self, text="Versión muy limitada · Solo para pruebas y animaciones simples",
                 bg="#1a1a2e", fg="#888").pack(pady=5)

    def proyectar(self, x, y, z, ang):
        # Rotación simple alrededor de Y + perspectiva básica
        rad = math.radians(ang)
        xz = x * math.cos(rad) - z * math.sin(rad)
        zz = x * math.sin(rad) + z * math.cos(rad)
        factor = 200 / (200 + zz)
        sx = 340 + xz * factor * 80
        sy = 210 + y * factor * 80
        return sx, sy

    def dibujar_cubo(self, ang):
        self.canvas.delete("all")
        verts = [
            (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
            (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)
        ]
        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        puntos = [self.proyectar(*v, ang) for v in verts]
        for a, b in edges:
            self.canvas.create_line(*puntos[a], *puntos[b], fill="#ff6b9d", width=2)

    def animar_cubo(self):
        self.angulo = (self.angulo + 3) % 360
        self.dibujar_cubo(self.angulo)
        self.after_id = self.after(40, self.animar_cubo)


# ============================================================
# IDE PRINCIPAL
# ============================================================

class EspanolPPIDE:
    KEYWORDS = [
        "mete", "chorrea", "mostra", "enseña", "saca", "pide",
        "si", "sino", "mientras", "para", "desde", "hasta",
        "funcion", "regresa", "fap", "ven", "sigue",
        "verdadero", "falso", "caliente", "frio"
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Español++ IDE v2.0  ·  Compilador + Autocomplete + 3D")
        self.root.geometry("1150x780")
        self.root.minsize(850, 620)

        self.bg = "#1a1a2e"
        self.panel = "#16213e"
        self.accent = "#e94560"
        self.text_bg = "#0f3460"
        self.fg = "#eaeaea"
        self.keyword_c = "#ff6b9d"
        self.string_c = "#a8e6cf"
        self.comment_c = "#7f8c8d"

        self.root.configure(bg=self.bg)
        self.archivo_actual = None
        self.compilador = CompiladorEspanolPP()

        self._crear_ui()
        self.cargar_ejemplo()

    def _crear_ui(self):
        # Menú
        menubar = tk.Menu(self.root, bg=self.panel, fg=self.fg)
        self.root.config(menu=menubar)

        m_arch = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Archivo", menu=m_arch)
        m_arch.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        m_arch.add_command(label="Abrir...", command=self.abrir, accelerator="Ctrl+O")
        m_arch.add_command(label="Guardar", command=self.guardar, accelerator="Ctrl+S")
        m_arch.add_command(label="Guardar como...", command=self.guardar_como)
        m_arch.add_separator()
        m_arch.add_command(label="Salir", command=self.root.quit)

        m_ejec = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Ejecutar", menu=m_ejec)
        m_ejec.add_command(label="▶ Ejecutar (F5)", command=self.ejecutar)
        m_ejec.add_command(label="Compilar a Python", command=self.compilar)
        m_ejec.add_command(label="Limpiar consola", command=self.limpiar_consola)

        m_herr = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Herramientas", menu=m_herr)
        m_herr.add_command(label="E++ 3D Studio", command=self.abrir_3d)

        m_ayuda = tk.Menu(menubar, tearoff=0, bg=self.panel, fg=self.fg)
        menubar.add_cascade(label="Ayuda", menu=m_ayuda)
        m_ayuda.add_command(label="Referencia", command=self.mostrar_referencia)
        m_ayuda.add_command(label="Acerca de", command=self.acerca_de)

        # Toolbar
        toolbar = tk.Frame(self.root, bg=self.bg)
        toolbar.pack(fill=tk.X, padx=8, pady=6)

        for text, cmd, color in [
            ("▶ Ejecutar (F5)", self.ejecutar, self.accent),
            ("Compilar a Python", self.compilar, "#0f3460"),
            ("3D Studio", self.abrir_3d, "#16213e"),
            ("Ejemplo", self.cargar_ejemplo, "#16213e"),
        ]:
            tk.Button(toolbar, text=text, command=cmd, bg=color, fg="white",
                      relief=tk.FLAT, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=3)

        # Editor + números de línea
        editor_frame = tk.Frame(self.root, bg=self.bg)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=8)

        self.linenumbers = tk.Text(editor_frame, width=4, bg="#16213e", fg="#888",
                                   font=("Consolas", 12), state=tk.DISABLED,
                                   relief=tk.FLAT, padx=4)
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.NONE, bg=self.text_bg, fg=self.fg,
            insertbackground=self.accent, font=("Consolas", 12),
            relief=tk.FLAT, padx=8, pady=6, undo=True
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self._on_key)
        self.editor.bind("<Tab>", self._autocomplete)

        # Consola
        tk.Label(self.root, text="  Consola", bg=self.panel, fg=self.fg,
                 anchor="w", font=("Segoe UI", 9, "bold")).pack(fill=tk.X, padx=8, pady=(6,0))

        self.consola = scrolledtext.ScrolledText(
            self.root, height=10, wrap=tk.WORD, bg="#0a0a12", fg="#a8e6cf",
            font=("Consolas", 11), relief=tk.FLAT, state=tk.DISABLED
        )
        self.consola.pack(fill=tk.X, padx=8, pady=(0,6))

        self.status = tk.Label(self.root, text="Español++ v2.0 listo 🔥", bg=self.panel,
                               fg=self.fg, anchor="w", padx=10)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        self.root.bind("<F5>", lambda e: self.ejecutar())
        self.root.bind("<Control-s>", lambda e: self.guardar())
        self.root.bind("<Control-o>", lambda e: self.abrir())
        self.root.bind("<Control-n>", lambda e: self.nuevo())

    def _on_key(self, event=None):
        self._actualizar_lineas()
        self._resaltar()

    def _actualizar_lineas(self):
        self.linenumbers.config(state=tk.NORMAL)
        self.linenumbers.delete("1.0", tk.END)
        lineas = self.editor.get("1.0", tk.END).count("\n")
        self.linenumbers.insert("1.0", "\n".join(str(i) for i in range(1, lineas+1)))
        self.linenumbers.config(state=tk.DISABLED)

    def _resaltar(self):
        for tag in ("kw", "str", "com"):
            self.editor.tag_remove(tag, "1.0", tk.END)
        contenido = self.editor.get("1.0", tk.END)
        for m in re.finditer(r'\b(' + '|'.join(self.KEYWORDS) + r')\b', contenido):
            self.editor.tag_add("kw", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'"[^\"]*"|\'[^\']*\'', contenido):
            self.editor.tag_add("str", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'#.*', contenido):
            self.editor.tag_add("com", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        self.editor.tag_config("kw", foreground=self.keyword_c)
        self.editor.tag_config("str", foreground=self.string_c)
        self.editor.tag_config("com", foreground=self.comment_c)

    def _autocomplete(self, event):
        # Autocompletado muy básico al presionar Tab
        pos = self.editor.index(tk.INSERT)
        linea = self.editor.get(f"{pos} linestart", pos)
        palabra = re.search(r'(\w+)$', linea)
        if palabra:
            pref = palabra.group(1)
            candidatos = [k for k in self.KEYWORDS if k.startswith(pref) and k != pref]
            if len(candidatos) == 1:
                self.editor.insert(tk.INSERT, candidatos[0][len(pref):])
                return "break"
            elif candidatos:
                self.status.config(text="Sugerencias: " + ", ".join(candidatos[:8]))
        return "break"

    def escribir(self, texto):
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
        self.status.config(text="Ejecutando...")

        def out_cb(t):
            self.escribir(t)
            self.root.update_idletasks()

        def in_cb(prompt):
            return simpledialog.askstring("Entrada", prompt) or ""

        interp = InterpreteEspanolPP(out_cb, in_cb)
        interp.ejecutar(codigo)
        self.status.config(text="Ejecución terminada ✨")

    def compilar(self):
        codigo = self.editor.get("1.0", tk.END)
        py = self.compilador.compilar(codigo)
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py")],
            title="Guardar código Python compilado"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(py)
            self.status.config(text=f"Compilado → {path}")
            messagebox.showinfo("Compilado", f"Se generó:\n{path}\n\nPuedes ejecutarlo con:\npython3 {path}")

    def abrir_3d(self):
        E3DStudio(self.root)

    def nuevo(self):
        if messagebox.askyesno("Nuevo", "¿Borrar el código actual?"):
            self.editor.delete("1.0", tk.END)
            self.archivo_actual = None
            self._actualizar_lineas()

    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[("Español++", "*.epp"), ("Todos", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())
            self.archivo_actual = path
            self._on_key()
            self.status.config(text=f"Abierto: {path}")

    def guardar(self):
        if self.archivo_actual:
            with open(self.archivo_actual, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.status.config(text=f"Guardado: {self.archivo_actual}")
        else:
            self.guardar_como()

    def guardar_como(self):
        path = filedialog.asksaveasfilename(defaultextension=".epp",
                                            filetypes=[("Español++", "*.epp")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.archivo_actual = path
            self.status.config(text=f"Guardado: {path}")

    def cargar_ejemplo(self):
        ejemplo = '''# Español++ v2.0 - Ejemplo profesional
# Funciones + listas + bucle para

funcion saludar(nombre)
    chorrea "Hola " + nombre + " 🔥"
    regresa verdadero

mete lista = ["Ana", "Carlos", "usuario"]

chorrea "=== Saludando a todos ==="
para i desde 0 hasta 2
    saludar(lista[i])

chorrea ""
chorrea "Ahora un contador:"
mete n = 1
mientras n <= 5
    chorrea "Paso " + n
    mete n = n + 1

chorrea ""
chorrea "Listo. Prueba el botón Compilar a Python o 3D Studio."
'''
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", ejemplo)
        self._on_key()
        self.status.config(text="Ejemplo cargado")

    def mostrar_referencia(self):
        ref = """ESPANOL++ v2.0 - Referencia rápida

mete x = 10
chorrea "texto" / mostra / saca
pide variable
si condicion ... sino ...
mientras condicion ...
para i desde 1 hasta 10 ...
funcion nombre(a, b) ... regresa valor
lista = [1, 2, 3]    acceso: lista[0]
fap / ven / sigue
verdadero-caliente / falso-frio

Tab = autocompletar palabra clave
F5  = ejecutar
Compilar a Python = genera .py real
3D Studio = animación wireframe básica
"""
        messagebox.showinfo("Referencia", ref)

    def acerca_de(self):
        messagebox.showinfo("Acerca de",
            "Español++ IDE v2.0\n\n"
            "Compilador · Autocomplete · Funciones\n"
            "Listas · Animación 3D limitada\n\n"
            "github.com/jesusxal777-boop/Espanol-PlusPlus")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EspanolPPIDE()
    app.run()
