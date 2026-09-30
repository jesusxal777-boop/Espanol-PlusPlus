# Español++ v2.0

Lenguaje de programación en **español** con toque picante + IDE profesional ligero.

## Novedades v2.0

- **Compilador** → Traduce Español++ a Python real (`.py`)
- **Autocompletado** básico en el IDE
- **Funciones** (`funcion nombre(params)`)
- **Listas** y acceso por índice
- **Bucle para** (`para i desde 1 hasta 10`)
- **Animaciones 2D** con canvas
- **E++ 3D Studio** (wireframe 3D muy básico para animaciones simples)
- Mejor resaltado de sintaxis y números de línea
- Más keywords y mejor manejo de errores

## Instalación rápida

```bash
git clone https://github.com/jesusxal777-boop/Espanol-PlusPlus.git
cd Espanol-PlusPlus
python3 espanolpp_ide.py
```

### En Alpine / iSH:

```bash
apk add python3 python3-tkinter ttf-dejavu
python3 espanolpp_ide.py
```

## Palabras clave principales

| Español++                    | Significado                  |
|-----------------------------|------------------------------|
| `mete x = 10`               | Variable                     |
| `chorrea / mostra / saca`   | Imprimir                     |
| `pide x`                    | Input                        |
| `si` / `sino`               | if / else                    |
| `mientras`                  | while                        |
| `para i desde 1 hasta 10`   | for                          |
| `funcion nombre(a, b)`      | Definir función              |
| `regresa valor`             | return                       |
| `lista = [1, 2, 3]`         | Listas                       |
| `fap`                       | pass                         |
| `ven` / `sigue`             | break / continue             |
| `compilar` (botón IDE)      | Genera archivo .py           |

## Ejemplo con función y lista

```espanolpp
funcion saludar(nombre)
    chorrea "Hola " + nombre + " 🔥"
    regresa verdadero

mete nombres = ["Ana", "Luis", "usuario"]
para i desde 0 hasta 2
    saludar(nombres[i])
```

## E++ 3D Studio (limitado)

Hay un módulo experimental de animación 3D wireframe dentro del IDE (botón **3D Studio**).
Es muy básico (solo para pruebas y animaciones simples de puntos/líneas), no es un motor 3D real.

## Compilar a Python

En el IDE pulsa el botón **Compilar a Python**. Se generará un archivo `.py` equivalente que puedes ejecutar con cualquier Python normal.

---

Hecho para que programar en español se sienta potente (y un poco caliente).
