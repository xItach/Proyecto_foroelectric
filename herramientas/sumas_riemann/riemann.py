#!/usr/bin/env python3
"""Simulador de sumas de Riemann.

Parte el intervalo [a, b] en n subintervalos, levanta un rectángulo sobre cada
uno y suma sus áreas. Esa suma se acerca a la integral definida de f a medida
que la norma de la partición tiende a cero; el programa deja ver ese proceso:
el valor de cada regla, el error contra un valor de referencia, cómo cae ese
error al duplicar n, y el dibujo de los rectángulos en la terminal.

Solo usa la biblioteca estándar. matplotlib es opcional y únicamente hace
falta para exportar la gráfica a PNG (--png).

    python3 riemann.py -f "x**2" -a 0 -b 1 -n 8 --dibujo
    python3 riemann.py -f "sin(x)" -a 0 -b pi --tabla
    python3 riemann.py --demo
"""

from __future__ import annotations

import argparse
import ast
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from types import CodeType
from typing import Callable, Sequence

# ---------------------------------------------------------------------------
# 1. Lectura de la función
#
# La expresión llega desde la línea de comandos, así que no se pasa a eval()
# tal cual: primero se revisa el árbol de sintaxis y solo sobreviven números,
# la variable x, los operadores aritméticos y las funciones de math que estén
# en la lista de abajo. Todo lo demás —atributos, índices, nombres extraños—
# se rechaza antes de ejecutar nada.
# ---------------------------------------------------------------------------


class ErrorDeExpresion(ValueError):
    """La expresión no se entiende o usa algo que no está permitido."""


class ErrorDeDominio(ValueError):
    """f existe, pero no está definida en el punto donde se quiso evaluar."""


_NODOS_PERMITIDOS = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name, ast.Load,
    ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
    ast.Pow, ast.USub, ast.UAdd,
)

_FUNCIONES = {nombre: getattr(math, nombre) for nombre in """
    sin cos tan asin acos atan atan2 sinh cosh tanh asinh acosh atanh
    exp expm1 log log1p log2 log10 sqrt fabs floor ceil copysign hypot
    degrees radians erf erfc gamma lgamma
""".split()}

_CONSTANTES = {"pi": math.pi, "e": math.e, "tau": math.tau}

_UTILES = {"abs": abs, "min": min, "max": max, "round": round}

_NOMBRES: dict[str, object] = {**_FUNCIONES, **_CONSTANTES, **_UTILES}

# eval() necesita un espacio global; se le entrega este, vaciado de builtins,
# para que la expresión no alcance nada más que los nombres de arriba.
_GLOBALES: dict[str, object] = {**_NOMBRES, "__builtins__": {}}


def _compilar(expresion: str, variables: Sequence[str] = ()) -> CodeType:
    """Valida la expresión y la compila. Lanza ErrorDeExpresion si algo sobra."""
    texto = expresion.strip().replace("^", "**")  # atajo: x^2 se lee como x**2
    if not texto:
        raise ErrorDeExpresion("la expresión está vacía")

    try:
        arbol = ast.parse(texto, mode="eval")
    except SyntaxError as exc:
        raise ErrorDeExpresion(f"no se entiende «{expresion}»: {exc.msg}") from None

    permitidos = ", ".join(variables) if variables else "constantes"
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, _NODOS_PERMITIDOS):
            raise ErrorDeExpresion(
                f"«{expresion}» usa {type(nodo).__name__}, que no está permitido; "
                f"solo números, {permitidos}, operadores y funciones de math"
            )
        if isinstance(nodo, ast.Constant) and not isinstance(nodo.value, (int, float)):
            raise ErrorDeExpresion("dentro de la expresión solo se aceptan números")
        if isinstance(nodo, ast.Name) and nodo.id not in variables and nodo.id not in _NOMBRES:
            raise ErrorDeExpresion(
                f"«{nodo.id}» no es una variable, función ni constante conocida; "
                "las funciones disponibles son las de math (sin, cos, tan, exp, log, "
                "sqrt, ...) y los productos se escriben con *: 2*x"
            )

    return compile(arbol, "<expresión>", "eval")


def numero(expresion: str) -> float:
    """Lee un número escrito como expresión: «2», «pi/2», «-sqrt(2)», «1/3»."""
    return float(eval(_compilar(expresion), _GLOBALES, {}))


@dataclass(frozen=True)
class Funcion:
    """f(x) tal como se escribió en la línea de comandos, ya validada."""

    expresion: str
    codigo: CodeType = field(repr=False, compare=False)

    @classmethod
    def desde_texto(cls, expresion: str) -> "Funcion":
        return cls(expresion.strip(), _compilar(expresion, ("x",)))

    def __call__(self, x: float) -> float:
        try:
            y = eval(self.codigo, _GLOBALES, {"x": x})
        except ZeroDivisionError:
            raise ErrorDeDominio(f"f({x:g}) divide entre cero") from None
        except ValueError as exc:  # sqrt(-1), log(0), asin(2)...
            raise ErrorDeDominio(f"f({x:g}) no está definida ({exc})") from None
        except OverflowError:
            raise ErrorDeDominio(f"f({x:g}) se desborda") from None

        valor = float(y)
        if math.isnan(valor):
            raise ErrorDeDominio(f"f({x:g}) no es un número")
        if math.isinf(valor):
            raise ErrorDeDominio(f"f({x:g}) es infinito")
        return valor

    def __str__(self) -> str:
        return f"f(x) = {self.expresion}"


# ---------------------------------------------------------------------------
# 2. Partición, etiquetas y reglas
#
# Una suma de Riemann son dos decisiones: dónde se corta el intervalo (la
# partición) y en qué punto de cada pedazo se mide la altura (la etiqueta).
# Cambiar la etiqueta es lo único que separa la suma por izquierda de la del
# punto medio; por eso las reglas viven en una sola función.
# ---------------------------------------------------------------------------

REGLAS_RIEMANN = ("izquierda", "derecha", "medio", "aleatoria", "inferior", "superior")
REGLAS_CONTRASTE = ("trapecio", "simpson")  # no son sumas de Riemann; sirven de comparación
REGLAS = REGLAS_RIEMANN + REGLAS_CONTRASTE

# Ínfimo y supremo de f en cada subintervalo se estiman muestreando: para las
# funciones de un curso alcanza, pero es una aproximación, no el valor exacto.
_MUESTRAS_EXTREMOS = 33


@dataclass(frozen=True)
class Subintervalo:
    """Un pedazo de la partición y la figura que se levanta sobre él."""

    izq: float
    der: float
    etiqueta: float                    # punto donde se evalúa f
    altura: float                      # f(etiqueta)
    altura_der: float | None = None    # solo trapecio: el lado derecho es otro

    @property
    def ancho(self) -> float:
        return self.der - self.izq

    @property
    def area(self) -> float:
        if self.altura_der is None:
            return self.altura * self.ancho
        return (self.altura + self.altura_der) / 2 * self.ancho

    def alto_en(self, x: float) -> float:
        """Altura de la figura (no de f) en x. Se usa para dibujarla."""
        if self.altura_der is None or self.ancho == 0:
            return self.altura
        t = (x - self.izq) / self.ancho
        return self.altura + t * (self.altura_der - self.altura)


@dataclass(frozen=True)
class Aproximacion:
    """Resultado de aplicar una regla: el número y de dónde salió."""

    regla: str
    a: float
    b: float
    n: int
    valor: float
    piezas: tuple[Subintervalo, ...] = ()

    @property
    def norma(self) -> float:
        """‖P‖, el subintervalo más ancho. La suma tiende a la integral cuando
        esto tiende a cero — que la n crezca es solo la forma más común."""
        return max((p.ancho for p in self.piezas), default=(self.b - self.a) / self.n)


def particion(a: float, b: float, n: int, *, aleatoria: bool = False,
              rng: random.Random | None = None) -> list[float]:
    """Puntos a = x0 < x1 < ... < xn = b.

    Con aleatoria=True los cortes caen al azar: la definición de la integral no
    pide pedazos iguales, solo que el más ancho se achique.
    """
    if n < 1:
        raise ValueError("n debe ser al menos 1")
    if b <= a:
        raise ValueError(f"el intervalo [{a:g}, {b:g}] está vacío o al revés: se necesita a < b")

    if aleatoria:
        rng = rng or random.Random()
        interiores = sorted(rng.uniform(a, b) for _ in range(n - 1))
        return [a, *interiores, b]

    paso = (b - a) / n
    # El último punto se fija en b y no se calcula, para que el redondeo no
    # deje la partición corta o larga por un epsilon.
    return [a + i * paso for i in range(n)] + [b]


def _etiqueta(f: Callable[[float], float], izq: float, der: float,
              regla: str, rng: random.Random) -> float:
    """El punto del subintervalo donde se mide la altura."""
    if regla == "izquierda":
        return izq
    if regla == "derecha":
        return der
    if regla == "medio":
        return (izq + der) / 2
    if regla == "aleatoria":
        return rng.uniform(izq, der)
    if regla in ("inferior", "superior"):
        paso = (der - izq) / (_MUESTRAS_EXTREMOS - 1)
        muestras = [izq + k * paso for k in range(_MUESTRAS_EXTREMOS)]
        elegir = min if regla == "inferior" else max
        return elegir(muestras, key=f)
    raise ValueError(f"regla desconocida: {regla}")


def suma_riemann(f: Callable[[float], float], a: float, b: float, n: int,
                 regla: str = "izquierda", *, aleatoria: bool = False,
                 semilla: int | None = None) -> Aproximacion:
    """Suma de Riemann de f en [a, b] con n subintervalos."""
    if regla not in REGLAS_RIEMANN:
        raise ValueError(f"«{regla}» no es una regla de suma de Riemann: {REGLAS_RIEMANN}")

    rng = random.Random(semilla)
    puntos = particion(a, b, n, aleatoria=aleatoria, rng=rng)

    piezas = []
    for izq, der in zip(puntos, puntos[1:]):
        t = _etiqueta(f, izq, der, regla, rng)
        piezas.append(Subintervalo(izq, der, t, f(t)))

    # fsum en vez de sum: con n grande la suma ingenua arrastra error de
    # redondeo y ensucia justo las cifras que se quieren mirar.
    valor = math.fsum(p.area for p in piezas)
    return Aproximacion(regla, a, b, n, valor, tuple(piezas))


def trapecio(f: Callable[[float], float], a: float, b: float, n: int, *,
             aleatoria: bool = False, semilla: int | None = None) -> Aproximacion:
    """Regla del trapecio: une los extremos con una recta en vez de una tapa
    plana. Es el promedio de la suma por izquierda y la de derecha."""
    puntos = particion(a, b, n, aleatoria=aleatoria, rng=random.Random(semilla))
    alturas = [f(x) for x in puntos]
    piezas = tuple(
        Subintervalo(izq, der, izq, alt_izq, alt_der)
        for izq, der, alt_izq, alt_der in zip(puntos, puntos[1:], alturas, alturas[1:])
    )
    return Aproximacion("trapecio", a, b, n, math.fsum(p.area for p in piezas), piezas)


def simpson(f: Callable[[float], float], a: float, b: float, n: int) -> Aproximacion:
    """Regla de Simpson: ajusta parábolas, no rectángulos, así que no es una
    suma de Riemann. Está para contrastar — con la misma n suele acertar varias
    cifras más. Necesita n par; si llega impar se usa n+1."""
    if n % 2:
        n += 1
    puntos = particion(a, b, n)
    alturas = [f(x) for x in puntos]
    paso = (b - a) / n
    impares = math.fsum(alturas[1:-1:2])
    pares = math.fsum(alturas[2:-1:2])
    valor = paso / 3 * (alturas[0] + alturas[-1] + 4 * impares + 2 * pares)
    return Aproximacion("simpson", a, b, n, valor)


def aproximar(f: Callable[[float], float], a: float, b: float, n: int,
              regla: str = "izquierda", *, aleatoria: bool = False,
              semilla: int | None = None) -> Aproximacion:
    """Aplica la regla que se pida, sea de Riemann o de contraste."""
    if regla in REGLAS_RIEMANN:
        return suma_riemann(f, a, b, n, regla, aleatoria=aleatoria, semilla=semilla)
    if regla == "trapecio":
        return trapecio(f, a, b, n, aleatoria=aleatoria, semilla=semilla)
    if regla == "simpson":
        return simpson(f, a, b, n)
    raise ValueError(f"regla desconocida: {regla}; las válidas son {REGLAS}")


# ---------------------------------------------------------------------------
# 3. Valor de referencia y convergencia
#
# Para hablar de error hace falta contra qué medirlo. Si se conoce el valor
# exacto se pasa con --exacta; si no, se estima con Simpson adaptativo, que
# parte el intervalo donde la curva lo pide y llega mucho más lejos que
# cualquiera de las sumas que el programa muestra.
# ---------------------------------------------------------------------------


def _simpson_simple(a: float, b: float, fa: float, fm: float, fb: float) -> float:
    return (b - a) / 6 * (fa + 4 * fm + fb)


def _refinar(f: Callable[[float], float], a: float, b: float, fa: float, fm: float,
             fb: float, entero: float, tolerancia: float, profundidad: int) -> float:
    m = (a + b) / 2
    m_izq, m_der = (a + m) / 2, (m + b) / 2
    f_izq, f_der = f(m_izq), f(m_der)
    izquierda = _simpson_simple(a, m, fa, f_izq, fm)
    derecha = _simpson_simple(m, b, fm, f_der, fb)
    diferencia = izquierda + derecha - entero

    # Si partir en dos casi no cambió el resultado, ya se llegó: el término
    # extra es la corrección de Richardson, gratis a estas alturas.
    if profundidad <= 0 or abs(diferencia) <= 15 * tolerancia:
        return izquierda + derecha + diferencia / 15

    return (_refinar(f, a, m, fa, f_izq, fm, izquierda, tolerancia / 2, profundidad - 1)
            + _refinar(f, m, b, fm, f_der, fb, derecha, tolerancia / 2, profundidad - 1))


def integral_referencia(f: Callable[[float], float], a: float, b: float,
                        tolerancia: float = 1e-12, profundidad: int = 45) -> float:
    """Aproximación fina de la integral, para medir el error de las sumas.

    No es "el valor exacto": es una aproximación mucho mejor que las del
    programa, suficiente para leer el error hasta varias cifras.
    """
    m = (a + b) / 2
    fa, fm, fb = f(a), f(m), f(b)
    entero = _simpson_simple(a, b, fa, fm, fb)
    return _refinar(f, a, b, fa, fm, fb, entero, tolerancia, profundidad)


@dataclass(frozen=True)
class FilaConvergencia:
    n: int
    valor: float
    error: float | None       # valor - referencia
    razon: float | None       # error anterior / error actual


def tabla_convergencia(f: Callable[[float], float], a: float, b: float,
                       regla: str = "izquierda", *, n_inicial: int = 4, pasos: int = 6,
                       referencia: float | None = None, aleatoria: bool = False,
                       semilla: int | None = None) -> list[FilaConvergencia]:
    """Aplica la regla duplicando n en cada paso y sigue la caída del error."""
    filas: list[FilaConvergencia] = []
    error_previo: float | None = None

    for paso in range(pasos + 1):
        n = n_inicial * 2 ** paso
        valor = aproximar(f, a, b, n, regla, aleatoria=aleatoria, semilla=semilla).valor
        error = None if referencia is None else valor - referencia

        razon = None
        if error not in (None, 0.0) and error_previo not in (None, 0.0):
            razon = abs(error_previo / error)

        filas.append(FilaConvergencia(n, valor, error, razon))
        error_previo = error

    return filas


# ---------------------------------------------------------------------------
# 4. Dibujo en la terminal
#
# Una columna de texto por cada tajada del ancho: se mira la altura de la
# figura y la de f en el centro de esa columna, y se pinta de ahí al eje.
# ---------------------------------------------------------------------------


def _alturas_figura(aprox: Aproximacion, columnas: Sequence[float]) -> list[float | None]:
    """Altura de la figura de la regla en cada columna (None si no dibuja)."""
    if not aprox.piezas:
        return [None] * len(columnas)

    alturas: list[float | None] = []
    i = 0
    for x in columnas:  # las columnas van de izquierda a derecha: un solo barrido
        while i + 1 < len(aprox.piezas) and x > aprox.piezas[i].der:
            i += 1
        alturas.append(aprox.piezas[i].alto_en(x))
    return alturas


def _poner(linea: list[str], pos: int, texto: str) -> None:
    pos = max(0, min(pos, len(linea) - len(texto)))
    hueco = linea[max(0, pos - 1):pos + len(texto) + 1]
    if all(c == " " for c in hueco):
        linea[pos:pos + len(texto)] = list(texto)


def _linea_x(a: float, b: float, ancho: int) -> str:
    izq, centro, der = f"{a:g}", f"{(a + b) / 2:g}", f"{b:g}"
    linea = [" "] * max(ancho, len(izq) + len(centro) + len(der) + 2)
    _poner(linea, 0, izq)
    _poner(linea, (ancho - len(centro)) // 2, centro)
    _poner(linea, ancho - len(der), der)
    return "".join(linea).rstrip()


def dibujar(f: Callable[[float], float], aprox: Aproximacion, *, ancho: int = 72,
            alto: int = 18, ascii_puro: bool = False) -> str:
    """Devuelve el dibujo de la figura de la regla y de f, como texto."""
    figura, curva, eje, borde, marco, esquina = (
        ("#", "*", "-", "|", "|", "+") if ascii_puro else ("▓", "•", "─", "│", "│", "└")
    )
    a, b = aprox.a, aprox.b
    paso = (b - a) / ancho
    columnas = [a + (j + 0.5) * paso for j in range(ancho)]

    # Si f no está definida en alguna columna, esa columna queda vacía en vez
    # de tumbar el dibujo completo.
    curvas: list[float | None] = []
    for x in columnas:
        try:
            curvas.append(f(x))
        except ErrorDeDominio:
            curvas.append(None)

    alturas = _alturas_figura(aprox, columnas)

    visibles = [v for v in curvas + alturas if v is not None]
    dato_max, dato_min = max(visibles + [0.0]), min(visibles + [0.0])
    margen = (dato_max - dato_min) * 0.06

    # El rango arranca en cero por el lado donde la función no llega: así una
    # curva positiva se apoya en el eje y no flota sobre un número que sobra.
    ymax = dato_max + margen if dato_max > 0 else 0.0
    ymin = dato_min - margen if dato_min < 0 else 0.0
    if ymax == ymin:
        ymax, ymin = 1.0, -1.0

    def fila(y: float) -> int:
        t = (ymax - y) / (ymax - ymin)
        return min(alto - 1, max(0, round(t * (alto - 1))))

    fila_cero = fila(0.0)
    lienzo = [[" "] * ancho for _ in range(alto)]

    # La figura se rellena entre el eje y su tapa; donde f es negativa el
    # relleno baja, que es exactamente lo que dice el área con signo.
    for j, h in enumerate(alturas):
        if h is None:
            continue
        desde, hasta = sorted((fila_cero, fila(h)))
        for i in range(desde, hasta + 1):
            lienzo[i][j] = figura

    # Separadores entre subintervalos, solo cuando caben sin volverse ruido.
    if aprox.piezas and len(aprox.piezas) <= ancho // 3:
        for pieza in aprox.piezas[:-1]:
            j = min(ancho - 1, max(0, int((pieza.der - a) / (b - a) * ancho)))
            for i in range(alto):
                if lienzo[i][j] == figura:
                    lienzo[i][j] = borde

    for j in range(ancho):
        if lienzo[fila_cero][j] == " ":
            lienzo[fila_cero][j] = eje

    for j, y in enumerate(curvas):
        if y is not None:
            lienzo[fila(y)][j] = curva

    lineas = []
    for i, celdas in enumerate(lienzo):
        if i == 0:
            etiqueta = f"{ymax:.3g}"
        elif i == fila_cero:
            etiqueta = "0"
        elif i == alto - 1:
            etiqueta = f"{ymin:.3g}"
        else:
            etiqueta = ""
        lineas.append(f"{etiqueta:>10} {marco}{''.join(celdas)}")

    lineas.append(" " * 10 + " " + esquina + eje * (ancho - 1))
    lineas.append(" " * 11 + _linea_x(a, b, ancho))
    figura_nombre = "figura de la regla" if aprox.piezas else "(esta regla no dibuja figura)"
    lineas.append(" " * 11 + f"{figura} {figura_nombre}    {curva} f(x)")
    return "\n".join(lineas)


def exportar_png(f: Callable[[float], float], aprox: Aproximacion, archivo: str) -> None:
    """Guarda el mismo dibujo como imagen. Requiere matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # sin ventana: solo escribe el archivo
        import matplotlib.pyplot as plt
    except ImportError:
        raise RuntimeError(
            "matplotlib no está instalado y --png lo necesita: pip install matplotlib"
        ) from None

    a, b = aprox.a, aprox.b
    xs, ys = [], []
    for k in range(801):
        x = a + (b - a) * k / 800
        try:
            ys.append(f(x))
            xs.append(x)
        except ErrorDeDominio:
            continue

    figura, ejes = plt.subplots(figsize=(9, 5.5))
    for pieza in aprox.piezas:
        alto_der = pieza.altura if pieza.altura_der is None else pieza.altura_der
        ejes.fill([pieza.izq, pieza.der, pieza.der, pieza.izq],
                  [0, 0, alto_der, pieza.altura],
                  facecolor="#2f7fd1", edgecolor="#12314f", alpha=0.35, linewidth=0.8)

    ejes.plot(xs, ys, color="#c2410c", linewidth=2, label="f(x)")
    ejes.axhline(0, color="#333333", linewidth=1)
    ejes.set_title(f"{aprox.regla} · n = {aprox.n} · suma = {aprox.valor:.8g}")
    ejes.set_xlabel("x")
    ejes.set_ylabel("f(x)")
    ejes.grid(alpha=0.25)
    ejes.legend(loc="best")
    figura.tight_layout()
    figura.savefig(archivo, dpi=140)
    plt.close(figura)


# ---------------------------------------------------------------------------
# 5. Presentación
# ---------------------------------------------------------------------------


def encabezado(funcion: Funcion, aprox: Aproximacion, aleatoria: bool = False) -> str:
    particion_txt = "aleatoria" if aleatoria else "uniforme"
    return (f"{funcion}   en [{aprox.a:g}, {aprox.b:g}]   n = {aprox.n}   "
            f"regla: {aprox.regla}   partición: {particion_txt}")


def resumen(aprox: Aproximacion, referencia: float | None) -> str:
    etiqueta = "suma de Riemann" if aprox.regla in REGLAS_RIEMANN else f"regla {aprox.regla}"
    lineas = [f"  {etiqueta:<22}{aprox.valor:>18.10g}"]

    if referencia is not None:
        error = aprox.valor - referencia
        lineas.append(f"  {'referencia':<22}{referencia:>18.10g}")
        # Con una integral que vale casi cero el porcentaje es ruido de
        # redondeo disfrazado de dato: mejor no mostrarlo.
        relativo = ""
        if abs(referencia) > 1e-12:
            relativo = f"   ({abs(error / referencia) * 100:.4g} % del valor)"
        lineas.append(f"  {'error':<22}{error:>18.6g}{relativo}")

    lineas.append(f"  {'norma ‖P‖':<22}{aprox.norma:>18.6g}")
    return "\n".join(lineas)


def tabla_detalle(aprox: Aproximacion, maximo: int = 25) -> str:
    """Subintervalo por subintervalo: de dónde sale cada sumando."""
    if not aprox.piezas:
        return f"  (la regla {aprox.regla} no arma rectángulos: no hay detalle que mostrar)"

    lineas = [f"  {'i':>4} {'x_i':>12} {'x_i+1':>12} {'etiqueta':>12} "
              f"{'f(etiqueta)':>14} {'área':>14}",
              "  " + "-" * 72]

    for i, p in enumerate(aprox.piezas[:maximo], start=1):
        lineas.append(f"  {i:>4} {p.izq:>12.6g} {p.der:>12.6g} {p.etiqueta:>12.6g} "
                      f"{p.altura:>14.6g} {p.area:>14.6g}")

    if len(aprox.piezas) > maximo:
        lineas.append(f"  {'...':>4}   ({len(aprox.piezas) - maximo} subintervalos más; "
                      f"súbelo con --filas)")

    lineas.append("  " + "-" * 72)
    lineas.append(f"  {'total':>4} {'':>12} {'':>12} {'':>12} {'':>14} {aprox.valor:>14.6g}")
    return "\n".join(lineas)


def tabla_comparacion(f: Callable[[float], float], a: float, b: float, n: int,
                      referencia: float | None = None, *, aleatoria: bool = False,
                      semilla: int | None = None) -> str:
    """Todas las reglas sobre la misma partición, una al lado de la otra."""
    lineas = [f"  {'regla':<12} {'n':>6} {'valor':>18} {'error':>14}", "  " + "-" * 54]

    for regla in REGLAS:
        try:
            aprox = aproximar(f, a, b, n, regla, aleatoria=aleatoria, semilla=semilla)
        except (ErrorDeDominio, ValueError) as exc:
            lineas.append(f"  {regla:<12} {'—':>6} {'—':>18}   ({exc})")
            continue

        error = "—" if referencia is None else f"{aprox.valor - referencia:.6g}"
        marca = " " if regla in REGLAS_RIEMANN else "*"
        lineas.append(f"  {regla:<12} {aprox.n:>6} {aprox.valor:>18.10g} {error:>14}{marca}")

    lineas.append("  " + "-" * 54)
    lineas.append("  * trapecio y simpson no son sumas de Riemann; están para contrastar.")
    lineas.append("  inferior y superior encierran a la integral: entre esas dos está el valor.")
    return "\n".join(lineas)


def texto_tabla_convergencia(filas: Sequence[FilaConvergencia], regla: str) -> str:
    """La tabla que muestra el límite: qué pasa con el error al duplicar n."""
    lineas = [f"  {'n':>8} {'suma':>20} {'error':>14} {'razón':>9}", "  " + "-" * 54]

    for fila in filas:
        error = "—" if fila.error is None else f"{fila.error:.4e}"
        razon = "—" if fila.razon is None else f"{fila.razon:.2f}"
        lineas.append(f"  {fila.n:>8} {fila.valor:>20.12g} {error:>14} {razon:>9}")

    lineas.append("  " + "-" * 54)
    lineas.append(f"  razón = error(n) / error(2n) para la regla {regla}.")
    lineas.append("  ≈2 significa que el error se parte a la mitad al duplicar n (orden 1:")
    lineas.append("  izquierda, derecha); ≈4, orden 2 (medio, trapecio); ≈16, orden 4 (simpson).")
    return "\n".join(lineas)


def animar(f: Callable[[float], float], a: float, b: float, regla: str, *,
           n_inicial: int = 2, pasos: int = 6, pausa: float = 0.7, ancho: int = 72,
           alto: int = 18, ascii_puro: bool = False, referencia: float | None = None,
           aleatoria: bool = False, semilla: int | None = None) -> None:
    """Redibuja la misma integral con n cada vez mayor: el límite, a ojo."""
    for paso in range(pasos + 1):
        n = n_inicial * 2 ** paso
        aprox = aproximar(f, a, b, n, regla, aleatoria=aleatoria, semilla=semilla)

        sys.stdout.write("\033[H\033[2J")  # limpia la pantalla antes de cada cuadro
        print(dibujar(f, aprox, ancho=ancho, alto=alto, ascii_puro=ascii_puro))

        linea = (f"\n  n = {n:<8} ‖P‖ = {aprox.norma:<12.6g} "
                 f"{regla} = {aprox.valor:.10g}")
        if referencia is not None:
            linea += f"   error = {aprox.valor - referencia:+.3e}"
        print(linea)

        if paso < pasos:
            time.sleep(pausa)


def demo() -> int:
    """Recorrido guiado con la integral de x² entre 0 y 1, que vale 1/3."""
    f = Funcion.desde_texto("x**2")
    a, b, exacto = 0.0, 1.0, 1 / 3

    print("\n" + "=" * 78)
    print("  Sumas de Riemann — ejemplo guiado:  ∫ x² dx  de 0 a 1  =  1/3  =  0.333...")
    print("=" * 78)

    print("\n1) Con solo 4 rectángulos por la izquierda, la figura se queda corta:\n")
    izq4 = suma_riemann(f, a, b, 4, "izquierda")
    print(dibujar(f, izq4, ancho=64, alto=12))
    print(f"\n{resumen(izq4, exacto)}")

    print("\n2) Por la derecha, con la misma partición, se pasa —el valor exacto queda")
    print("   atrapado entre las dos:\n")
    der4 = suma_riemann(f, a, b, 4, "derecha")
    print(dibujar(f, der4, ancho=64, alto=12))
    print(f"\n{resumen(der4, exacto)}")
    print(f"\n   {izq4.valor:.6f}  <  {exacto:.6f}  <  {der4.valor:.6f}")

    print("\n3) Al duplicar n, el error de la suma por izquierda se parte a la mitad:\n")
    print(texto_tabla_convergencia(
        tabla_convergencia(f, a, b, "izquierda", n_inicial=4, pasos=6, referencia=exacto),
        "izquierda"))

    print("\n4) Con el punto medio, en cambio, se divide entre cuatro:\n")
    print(texto_tabla_convergencia(
        tabla_convergencia(f, a, b, "medio", n_inicial=4, pasos=6, referencia=exacto),
        "medio"))

    print("\n5) Todas las reglas sobre la misma partición de n = 10:\n")
    print(tabla_comparacion(f, a, b, 10, exacto))

    print("\nPruébalo con tu propia función, por ejemplo:")
    print('  python3 riemann.py -f "sin(x)" -a 0 -b pi -n 12 --dibujo --tabla\n')
    return 0


# ---------------------------------------------------------------------------
# 6. Línea de comandos
# ---------------------------------------------------------------------------

_EJEMPLOS = """
ejemplos:
  python3 riemann.py -f "x**2" -a 0 -b 1 -n 8 --dibujo --detalle
  python3 riemann.py -f "sin(x)" -a 0 -b pi -n 12 --comparar
  python3 riemann.py -f "exp(-x**2)" -a -2 -b 2 --tabla --pasos 8
  python3 riemann.py -f "1/x" -a 1 -b e -r medio --exacta 1
  python3 riemann.py -f "sqrt(1-x**2)" -a -1 -b 1 --animar
  python3 riemann.py --demo

notas:
  - la función se escribe en sintaxis de Python: 2*x, no 2x; x**2 o x^2 sirven.
  - a, b y --exacta aceptan expresiones: pi, pi/2, -sqrt(2), 1/3.
  - los límites deben cumplir a < b (∫ de b a a es el mismo número con signo
    contrario).
"""


def _arg_numero(texto: str) -> float:
    try:
        return numero(texto)
    except ErrorDeExpresion as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def _arg_positivo(texto: str) -> int:
    try:
        valor = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"«{texto}» no es un número entero") from None
    if valor < 1:
        raise argparse.ArgumentTypeError("tiene que ser 1 o más")
    return valor


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="riemann.py",
        description="Simula sumas de Riemann: las calcula, las compara y las dibuja.",
        epilog=_EJEMPLOS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-f", "--funcion", help='f(x), entre comillas: "x**2", "sin(x)/x"')
    parser.add_argument("-a", "--desde", type=_arg_numero, default=0.0,
                        help="límite inferior (por defecto 0)")
    parser.add_argument("-b", "--hasta", type=_arg_numero, default=1.0,
                        help="límite superior (por defecto 1)")
    parser.add_argument("-n", type=_arg_positivo, default=10, dest="n",
                        help="cantidad de subintervalos (por defecto 10)")
    parser.add_argument("-r", "--regla", choices=REGLAS, default="izquierda",
                        help="dónde se mide la altura de cada pedazo (por defecto izquierda)")
    parser.add_argument("--aleatoria", action="store_true",
                        help="cortar el intervalo en puntos al azar, no en pedazos iguales")
    parser.add_argument("--semilla", type=int, default=None,
                        help="semilla del azar, para repetir el mismo resultado")
    parser.add_argument("--exacta", type=_arg_numero, default=None,
                        help="valor exacto de la integral, si se conoce")
    parser.add_argument("--sin-referencia", action="store_true",
                        help="no estimar el valor de referencia ni el error")
    parser.add_argument("--detalle", action="store_true",
                        help="tabla subintervalo por subintervalo")
    parser.add_argument("--filas", type=_arg_positivo, default=25,
                        help="filas máximas del detalle (por defecto 25)")
    parser.add_argument("--comparar", action="store_true",
                        help="todas las reglas con la misma n")
    parser.add_argument("--tabla", action="store_true",
                        help="tabla de convergencia duplicando n")
    parser.add_argument("--pasos", type=_arg_positivo, default=6,
                        help="cuántas veces duplicar n en la tabla o la animación")
    parser.add_argument("--dibujo", action="store_true", help="dibujar en la terminal")
    parser.add_argument("--animar", action="store_true",
                        help="redibujar mientras n crece (Ctrl-C para cortar)")
    parser.add_argument("--pausa", type=float, default=0.7,
                        help="segundos entre cuadros de --animar (por defecto 0.7)")
    parser.add_argument("--ancho", type=_arg_positivo, default=72, help="ancho del dibujo")
    parser.add_argument("--alto", type=_arg_positivo, default=18, help="alto del dibujo")
    parser.add_argument("--ascii", action="store_true", dest="ascii_puro",
                        help="dibujar solo con caracteres ASCII")
    parser.add_argument("--png", metavar="ARCHIVO",
                        help="guardar la gráfica como imagen (necesita matplotlib)")
    parser.add_argument("--demo", action="store_true",
                        help="recorrido guiado con ∫ x² dx de 0 a 1")
    return parser


def _correr(args: argparse.Namespace) -> int:
    f = Funcion.desde_texto(args.funcion)
    a, b = args.desde, args.hasta
    if b <= a:
        raise ValueError(f"se necesita a < b, y llegó [{a:g}, {b:g}]")

    referencia = args.exacta
    if referencia is None and not args.sin_referencia:
        try:
            referencia = integral_referencia(f, a, b)
        except (ErrorDeDominio, RecursionError) as exc:
            print(f"aviso: sin valor de referencia ({exc}); no se muestra el error",
                  file=sys.stderr)

    aprox = aproximar(f, a, b, args.n, args.regla,
                      aleatoria=args.aleatoria, semilla=args.semilla)

    print()
    print(encabezado(f, aprox, args.aleatoria))
    print()
    print(resumen(aprox, referencia))

    if args.detalle:
        print(f"\n  Detalle de los {aprox.n} subintervalos:\n")
        print(tabla_detalle(aprox, args.filas))

    if args.comparar:
        print(f"\n  Las reglas con n = {args.n}:\n")
        print(tabla_comparacion(f, a, b, args.n, referencia,
                                aleatoria=args.aleatoria, semilla=args.semilla))

    if args.tabla:
        print(f"\n  Convergencia de la regla {args.regla}:\n")
        filas = tabla_convergencia(f, a, b, args.regla, n_inicial=args.n, pasos=args.pasos,
                                   referencia=referencia, aleatoria=args.aleatoria,
                                   semilla=args.semilla)
        print(texto_tabla_convergencia(filas, args.regla))

    if args.dibujo:
        print()
        print(dibujar(f, aprox, ancho=args.ancho, alto=args.alto, ascii_puro=args.ascii_puro))

    if args.animar:
        animar(f, a, b, args.regla, n_inicial=args.n, pasos=args.pasos, pausa=args.pausa,
               ancho=args.ancho, alto=args.alto, ascii_puro=args.ascii_puro,
               referencia=referencia, aleatoria=args.aleatoria, semilla=args.semilla)

    if args.png:
        exportar_png(f, aprox, args.png)
        print(f"\n  gráfica guardada en {args.png}")

    print()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _construir_parser()
    args = parser.parse_args(argv)

    if args.demo:
        return demo()
    if not args.funcion:
        parser.error("falta -f/--funcion (o usa --demo para ver un ejemplo completo)")

    try:
        return _correr(args)
    except ErrorDeDominio as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("  si el punto que falla es un extremo del intervalo, prueba otra regla "
              "(-r medio, -r derecha)\n  o corre el límite un poco (-a 1e-9).",
              file=sys.stderr)
        return 2
    except (ErrorDeExpresion, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        # Pasa al canalizar la salida a head o less. Se apunta stdout a
        # /dev/null para que Python no vuelva a quejarse al cerrar.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    except KeyboardInterrupt:
        print("\ncortado por el usuario", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
