# Simulador de sumas de Riemann

Calcula, compara y dibuja sumas de Riemann en la terminal. Parte `[a, b]` en `n`
subintervalos, levanta una figura sobre cada uno y suma sus áreas; la idea es ver
cómo esa suma se acerca a la integral cuando los pedazos se achican.

Solo necesita **Python 3.8 o más nuevo**, sin instalar nada.
`matplotlib` es opcional y únicamente hace falta para `--png`.

## Empezar

```bash
python3 riemann.py --demo
```

Es un recorrido guiado con ∫ x² dx de 0 a 1 (que vale 1/3): muestra los rectángulos,
cómo la suma por izquierda se queda corta y la de derecha se pasa, y cómo cae el error
al duplicar n.

Con una función propia:

```bash
python3 riemann.py -f "x**2" -a 0 -b 1 -n 8 --dibujo --detalle
```

```
f(x) = x**2   en [0, 1]   n = 8   regla: izquierda   partición: uniforme

  suma de Riemann                0.2734375
  referencia                  0.3333333333
  error                         -0.0598958   (17.97 % del valor)
  norma ‖P‖                          0.125
```

## Cómo se escribe la función

En sintaxis de Python, entre comillas: `"x**2"`, `"sin(x)/x"`, `"exp(-x**2)"`.

- Los productos llevan `*`: `2*x`, no `2x`.
- `x^2` también sirve — se lee como `x**2`.
- Se pueden usar las funciones de `math` (`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`,
  `atan`, `erf`, …) y las constantes `pi`, `e`, `tau`.
- Los límites `-a`, `-b` y el valor `--exacta` aceptan expresiones: `pi`, `pi/2`,
  `-sqrt(2)`, `1/3`.

La expresión se revisa antes de ejecutarse: solo pasan números, la variable `x`, los
operadores aritméticos y las funciones de la lista. Cualquier otra cosa se rechaza con
un mensaje, no se ejecuta.

## Las reglas

Una suma de Riemann son dos decisiones: dónde se corta el intervalo y en qué punto de
cada pedazo se mide la altura. Lo segundo es lo que distingue a estas reglas (`-r`):

| Regla | Dónde mide la altura |
|---|---|
| `izquierda` | en el extremo izquierdo de cada pedazo |
| `derecha` | en el extremo derecho |
| `medio` | en el punto medio |
| `aleatoria` | en un punto al azar del pedazo — la definición lo permite |
| `inferior` | donde f es más baja (suma inferior de Darboux) |
| `superior` | donde f es más alta (suma superior de Darboux) |
| `trapecio` | * une los dos extremos con una recta |
| `simpson` | * ajusta parábolas en vez de rectángulos |

\* Trapecio y Simpson **no** son sumas de Riemann; están para contrastar. `inferior` y
`superior` encierran siempre a la integral: el valor exacto está entre esas dos.

`--aleatoria` corta además el intervalo en puntos al azar, para ver que la partición no
tiene que ser de pedazos iguales: lo que importa es que el pedazo más ancho (la norma
`‖P‖`) se achique.

## Qué muestra

| Opción | Qué hace |
|---|---|
| `--dibujo` | dibuja la figura y la curva en la terminal |
| `--detalle` | tabla subintervalo por subintervalo: de dónde sale cada sumando |
| `--comparar` | todas las reglas con la misma n, una al lado de la otra |
| `--tabla` | convergencia: duplica n y sigue la caída del error |
| `--animar` | redibuja mientras n crece, para ver el límite |
| `--png ARCHIVO` | guarda la gráfica como imagen (necesita `matplotlib`) |
| `--ascii` | dibuja solo con caracteres ASCII, para terminales viejas |

`python3 riemann.py --help` lista todas las opciones.

### Leer la tabla de convergencia

```bash
python3 riemann.py -f "exp(-x**2)" -a -2 -b 2 -n 4 -r medio --tabla --pasos 5
```

```
         n                 suma          error     razón
  ------------------------------------------------------
         4        1.76840001527     4.2372e-03         —
         8        1.76557789708     1.4151e-03      2.99
        16         1.7645373984     3.7462e-04      3.78
        32        1.76425774067     9.4959e-05      3.95
        64        1.76418660284     2.3821e-05      3.99
       128        1.76416874195     5.9604e-06      4.00
```

La columna **razón** es `error(n) / error(2n)`: cuántas veces mejora el resultado al
duplicar n. ≈2 significa orden 1 (`izquierda`, `derecha`); ≈4, orden 2 (`medio`,
`trapecio`); ≈16, orden 4 (`simpson`).

El **error** se mide contra una referencia. Si se conoce el valor exacto conviene darlo
con `--exacta` (`--exacta 1/3`); si no, el programa lo estima con Simpson adaptativo,
que acierta muchas más cifras que cualquiera de las sumas mostradas. Con
`--sin-referencia` no se calcula nada de esto.

## Usarlo desde otro programa

```python
from riemann import Funcion, suma_riemann, integral_referencia

f = Funcion.desde_texto("sin(x)")
aprox = suma_riemann(f, 0, 3.141592653589793, 100, "medio")

print(aprox.valor)                       # 2.0000822...
print(aprox.norma)                       # el pedazo más ancho
print(aprox.piezas[0].etiqueta)          # dónde se midió la altura del primero
print(integral_referencia(f, 0, 3.141592653589793))
```

`f` puede ser cualquier función de Python que reciba un número y devuelva otro; usar
`Funcion.desde_texto` solo hace falta cuando la fórmula viene escrita como texto.

## Pruebas

```bash
python3 -m unittest -v test_riemann
```

Las sumas se comparan contra fórmulas cerradas (la suma por izquierda de x² en [0, 1] es
`(n-1)(2n-1)/6n²`), contra casos donde una regla debe ser exacta (punto medio y trapecio
con rectas, Simpson con cúbicas) y contra el orden de convergencia esperado.
