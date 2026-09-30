#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Español++ Terminal
Intérprete que funciona SOLO en consola (no necesita VNC ni interfaz gráfica).
Ideal para iSH cuando no hay display o no hay internet estable.
"""

import re
import sys
import traceback
import urllib.request
import ssl
import socket
from typing import Any, Dict, List

class ErrorEPP(Exception):
    pass

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Interprete:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.funciones: Dict[str, Any] = {}
        self.lineas: List[str] = []

    def out(self, *args):
        print(*args)

    def error(self, msg):
        raise ErrorEPP(f"🔥 Error: {msg}")

    def eval_expr(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return None

        if expr in ("verdadero", "caliente"): return True
        if expr in ("falso", "frio"): return False

        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        if expr.startswith("[") and expr.endswith("]"):
            contenido = expr[1:-1].strip()
            if not contenido:
                return []
            return [self.eval_expr(p.strip()) for p in self._split_args(contenido)]

        m = re.match(r'^(\w+)\[(.+)\]$', expr)
        if m:
            lista = self.variables.get(m.group(1))
            if lista is None:
                self.error(f"Lista '{m.group(1)}' no existe")
            return lista[int(self.eval_expr(m.group(2)))]

        try:
            return float(expr) if "." in expr else int(expr)
        except ValueError:
            pass

        if expr in self.variables:
            return self.variables[expr]

        # Llamadas a funciones integradas de internet
        m = re.match(r'^(\w+)\((.*)\)$', expr)
        if m:
            nombre, args_str = m.group(1), m.group(2)
            args = [self.eval_expr(a.strip()) for a in self._split_args(args_str)] if args_str.strip() else []

            if nombre == "hay_internet":
                return self._hay_internet()
            if nombre == "ping":
                host = args[0] if args else "8.8.8.8"
                return self._ping(str(host))
            if nombre == "obtener":
                if not args:
                    self.error("obtener(url) necesita una URL")
                return self._http_get(str(args[0]))
            if nombre == "mi_ip":
                return self._mi_ip()

            if nombre in self.funciones:
                return self._llamar(nombre, args)
            self.error(f"Función '{nombre}' no definida")

        for op in ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/"]:
            if op in expr:
                partes = expr.split(op, 1)
                if len(partes) == 2:
                    izq, der = self.eval_expr(partes[0]), self.eval_expr(partes[1])
                    if op == "+":
                        if isinstance(izq, str) or isinstance(der, str):
                            return str(izq) + str(der)
                        return izq + der
                    ops = {
                        "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b,
                        "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
                        "<": lambda a, b: a < b, ">": lambda a, b: a > b,
                        "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
                    }
                    return ops[op](izq, der)

        if re.match(r'^[a-zA-Z_]\w*$', expr):
            self.error(f"Variable '{expr}' no existe")
        self.error(f"No entiendo: {expr}")

    def _split_args(self, s: str) -> List[str]:
        args, actual, nivel = [], [], 0
        for c in s:
            if c == ',' and nivel == 0:
                args.append(''.join(actual))
                actual = []
            else:
                if c in '([': nivel += 1
                elif c in ')]': nivel -= 1
                actual.append(c)
        if actual:
            args.append(''.join(actual))
        return args

    # ---------- Internet legítimo ----------
    def _hay_internet(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _ping(self, host: str) -> str:
        try:
            socket.create_connection((host, 80), timeout=3)
            return f"OK — {host} responde"
        except OSError:
            try:
                socket.create_connection((host, 443), timeout=3)
                return f"OK — {host} responde (443)"
            except OSError:
                return f"Sin respuesta de {host}"

    def _http_get(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={"User-Agent": "Español++/terminal"})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
                data = r.read()[:5000]
                try:
                    return data.decode("utf-8")
                except Exception:
                    return data.decode("latin-1", errors="ignore")
        except Exception as e:
            return f"Error HTTP: {e}"

    def _mi_ip(self) -> str:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen("https://api.ipify.org", context=ctx, timeout=5) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            return f"No se pudo obtener IP: {e}"

    def _llamar(self, nombre, args):
        func = self.funciones[nombre]
        params, cuerpo = func["params"], func["cuerpo"]
        if len(args) != len(params):
            self.error(f"'{nombre}' espera {len(params)} argumentos")
        backup = {p: self.variables.get(p) for p in params}
        for p, a in zip(params, args):
            self.variables[p] = a
        resultado = None
        try:
            self._bloque(cuerpo[0], cuerpo[1])
        except ReturnValue as r:
            resultado = r.value
        for p in params:
            if backup[p] is None:
                self.variables.pop(p, None)
            else:
                self.variables[p] = backup[p]
        return resultado

    def _fin_bloque(self, inicio: int) -> int:
        i = inicio
        while i < len(self.lineas):
            l = self.lineas[i].strip()
            if not l or l.startswith("#"):
                i += 1
                continue
            if (l.startswith(("mete ", "chorrea ", "mostra ", "saca ", "pide ", "si ", "mientras ",
                              "para ", "funcion ", "regresa ")) or l in ("sino", "ven", "sigue")) \
               and not self.lineas[i].startswith((" ", "\t")):
                return i
            i += 1
        return i

    def _bloque(self, inicio: int, fin: int):
        i = inicio
        while i < fin:
            linea = self.lineas[i].strip()
            if not linea or linea.startswith("#"):
                i += 1
                continue
            if "#" in linea:
                linea = linea[:linea.index("#")].strip()

            m = re.match(r'funcion\s+(\w+)\s*\((.*)\)', linea)
            if m:
                nombre = m.group(1)
                params = [p.strip() for p in m.group(2).split(",") if p.strip()]
                ci, cf = i + 1, self._fin_bloque(i + 1)
                self.funciones[nombre] = {"params": params, "cuerpo": (ci, cf)}
                i = cf
                continue

            if linea.startswith("regresa "):
                raise ReturnValue(self.eval_expr(linea[8:].strip()))
            if linea == "regresa":
                raise ReturnValue(None)

            if linea.startswith("mete "):
                resto = linea[5:].strip()
                if "=" not in resto:
                    self.error("Usa: mete x = valor")
                var, expr = resto.split("=", 1)
                self.variables[var.strip()] = self.eval_expr(expr.strip())
                i += 1
                continue

            for pref in ("chorrea ", "mostra ", "enseña ", "saca "):
                if linea.startswith(pref):
                    self.out(self.eval_expr(linea[len(pref):].strip()))
                    break
            else:
                if linea.startswith("pide "):
                    var = linea[5:].strip()
                    entrada = input(f"👉 {var}: ")
                    try:
                        self.variables[var] = float(entrada) if "." in entrada else int(entrada)
                    except ValueError:
                        self.variables[var] = entrada
                    i += 1
                    continue

                m = re.match(r'para\s+(\w+)\s+desde\s+(.+)\s+hasta\s+(.+)', linea)
                if m:
                    var, a, b = m.group(1), m.group(2), m.group(3)
                    ci, cf = i + 1, self._fin_bloque(i + 1)
                    for val in range(int(self.eval_expr(a)), int(self.eval_expr(b)) + 1):
                        self.variables[var] = val
                        try:
                            self._bloque(ci, cf)
                        except StopIteration:
                            break
                    i = cf
                    continue

                if linea.startswith("mientras "):
                    cond = linea[9:].strip()
                    ci, cf = i + 1, self._fin_bloque(i + 1)
                    n = 0
                    while self.eval_expr(cond) and n < 50000:
                        try:
                            self._bloque(ci, cf)
                        except StopIteration:
                            break
                        n += 1
                    i = cf
                    continue

                if linea.startswith("si "):
                    cond = linea[3:].strip()
                    ci = i + 1
                    sino = None
                    j = ci
                    while j < len(self.lineas):
                        l = self.lineas[j].strip()
                        if l == "sino":
                            sino = j + 1
                            j += 1
                            continue
                        if (l.startswith(("mete ", "chorrea ", "mostra ", "si ", "mientras ", "para ", "funcion "))
                            or l in ("ven", "sigue")) and not self.lineas[j].startswith((" ", "\t")):
                            break
                        j += 1
                    cf = j
                    if self.eval_expr(cond):
                        self._bloque(ci, (sino - 1) if sino else cf)
                    elif sino:
                        self._bloque(sino, cf)
                    i = cf
                    continue

                if linea == "fap":
                    i += 1
                    continue
                if linea == "ven":
                    raise StopIteration()

                m = re.match(r'^(\w+)\((.*)\)$', linea)
                if m:
                    self.eval_expr(linea)  # ejecuta y descarta retorno
                    i += 1
                    continue

                self.error(f"No entiendo: '{linea}'")

            i += 1

    def ejecutar(self, codigo: str):
        self.variables.clear()
        self.funciones.clear()
        self.lineas = codigo.splitlines()
        try:
            self._bloque(0, len(self.lineas))
        except (ReturnValue, StopIteration):
            pass
        except ErrorEPP as e:
            print(e)
        except Exception as e:
            print(f"🔥 Error: {e}")
            traceback.print_exc()


def repl():
    print("=" * 50)
    print("  Español++ Terminal  (sin VNC)")
    print("  Escribe código. Línea vacía dos veces o 'salir' para terminar.")
    print("  Funciones internet: hay_internet()  ping(\"host\")  obtener(\"url\")  mi_ip()")
    print("=" * 50)
    print()

    interp = Interprete()
    buffer = []

    while True:
        try:
            linea = input("epp> " if not buffer else "...  ")
        except (EOFError, KeyboardInterrupt):
            print("\nAdiós.")
            break

        if linea.strip().lower() in ("salir", "exit", "quit") and not buffer:
            print("Adiós.")
            break

        if linea.strip() == "" and buffer:
            codigo = "\n".join(buffer)
            buffer = []
            interp.ejecutar(codigo)
            print()
            continue

        buffer.append(linea)


def main():
    if len(sys.argv) > 1:
        # Ejecutar archivo .epp
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                codigo = f.read()
            Interprete().ejecutar(codigo)
        except FileNotFoundError:
            print(f"No encontré: {path}")
    else:
        repl()


if __name__ == "__main__":
    main()
