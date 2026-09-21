#!/usr/bin/env python3
"""Pruebas de riemann.py.

    python3 -m unittest -v test_riemann

Las fórmulas cerradas de las sumas de x² están puestas a mano a propósito: si
alguien toca el cálculo, la prueba falla contra la fórmula del libro, no
contra otra versión del mismo código.
"""

import contextlib
import io
import math
import unittest

import riemann as r


class ReglasBasicas(unittest.TestCase):
    """Sumas con valor conocido de antemano."""

    def setUp(self):
        self.cuadrado = r.Funcion.desde_texto("x**2")

    def test_izquierda_coincide_con_la_formula(self):
        # Σ (i/n)² · (1/n) para i = 0..n-1  =  (n-1)(2n-1) / 6n²
        for n in (1, 2, 5, 40, 337):
            esperado = (n - 1) * (2 * n - 1) / (6 * n * n)
            suma = r.suma_riemann(self.cuadrado, 0, 1, n, "izquierda")
            self.assertAlmostEqual(suma.valor, esperado, places=12, msg=f"n = {n}")

    def test_derecha_coincide_con_la_formula(self):
        # Σ (i/n)² · (1/n) para i = 1..n  =  (n+1)(2n+1) / 6n²
        for n in (1, 2, 5, 40, 337):
            esperado = (n + 1) * (2 * n + 1) / (6 * n * n)
            suma = r.suma_riemann(self.cuadrado, 0, 1, n, "derecha")
            self.assertAlmostEqual(suma.valor, esperado, places=12, msg=f"n = {n}")

    def test_creciente_queda_encerrada_entre_izquierda_y_derecha(self):
        izquierda = r.suma_riemann(self.cuadrado, 0, 1, 20, "izquierda").valor
        derecha = r.suma_riemann(self.cuadrado, 0, 1, 20, "derecha").valor
        self.assertLess(izquierda, 1 / 3)
        self.assertLess(1 / 3, derecha)

    def test_punto_medio_es_exacto_con_una_recta(self):
        # El error del punto medio depende de f''; para una recta es cero.
        recta = r.Funcion.desde_texto("3*x + 2")
        exacto = 3 / 2 * (4 - 1) + 2 * (2 - 1)  # ∫(3x+2) de 1 a 2
        for n in (1, 3, 17):
            suma = r.suma_riemann(recta, 1, 2, n, "medio")
            self.assertAlmostEqual(suma.valor, exacto, places=12)

    def test_trapecio_es_exacto_con_una_recta(self):
        recta = r.Funcion.desde_texto("3*x + 2")
        exacto = 3 / 2 * (4 - 1) + 2 * (2 - 1)
        self.assertAlmostEqual(r.trapecio(recta, 1, 2, 7).valor, exacto, places=12)

    def test_trapecio_es_el_promedio_de_izquierda_y_derecha(self):
        izquierda = r.suma_riemann(self.cuadrado, 0, 1, 9, "izquierda").valor
        derecha = r.suma_riemann(self.cuadrado, 0, 1, 9, "derecha").valor
        self.assertAlmostEqual(r.trapecio(self.cuadrado, 0, 1, 9).valor,
                               (izquierda + derecha) / 2, places=12)

    def test_simpson_es_exacto_con_una_cubica(self):
        cubica = r.Funcion.desde_texto("x**3")
        self.assertAlmostEqual(r.simpson(cubica, 0, 2, 4).valor, 4.0, places=12)

    def test_simpson_sube_n_impar_al_siguiente_par(self):
        self.assertEqual(r.simpson(self.cuadrado, 0, 1, 5).n, 6)

    def test_inferior_y_superior_encierran_la_integral(self):
        onda = r.Funcion.desde_texto("sin(x) + 2")
        exacto = r.integral_referencia(onda, 0, 3)
        inferior = r.suma_riemann(onda, 0, 3, 24, "inferior").valor
        superior = r.suma_riemann(onda, 0, 3, 24, "superior").valor
        self.assertLessEqual(inferior, exacto)
        self.assertLessEqual(exacto, superior)

    def test_area_bajo_el_eje_resta(self):
        seno = r.Funcion.desde_texto("sin(x)")
        suma = r.suma_riemann(seno, 0, 2 * math.pi, 500, "medio")
        self.assertAlmostEqual(suma.valor, 0.0, places=9)

    def test_suma_con_n_grande_no_arrastra_error(self):
        suma = r.suma_riemann(self.cuadrado, 0, 1, 200_000, "medio")
        self.assertAlmostEqual(suma.valor, 1 / 3, places=11)


class Particiones(unittest.TestCase):

    def test_la_particion_empieza_y_termina_donde_debe(self):
        puntos = r.particion(-2, 5, 14)
        self.assertEqual(len(puntos), 15)
        self.assertEqual(puntos[0], -2)
        self.assertEqual(puntos[-1], 5)
        self.assertEqual(puntos, sorted(puntos))

    def test_particion_aleatoria_sigue_siendo_una_particion(self):
        puntos = r.particion(0, 1, 30, aleatoria=True, rng=__import__("random").Random(7))
        self.assertEqual(len(puntos), 31)
        self.assertEqual(puntos, sorted(puntos))
        self.assertEqual((puntos[0], puntos[-1]), (0, 1))

    def test_con_cortes_al_azar_la_suma_igual_converge(self):
        # La definición no pide pedazos iguales: pide que el más ancho se achique.
        cuadrado = r.Funcion.desde_texto("x**2")
        suma = r.suma_riemann(cuadrado, 0, 1, 4000, "aleatoria", aleatoria=True, semilla=3)
        self.assertAlmostEqual(suma.valor, 1 / 3, places=3)

    def test_la_norma_es_el_pedazo_mas_ancho(self):
        suma = r.suma_riemann(r.Funcion.desde_texto("x"), 0, 1, 8, "medio")
        self.assertAlmostEqual(suma.norma, 0.125, places=12)

    def test_la_semilla_hace_repetible_el_azar(self):
        cuadrado = r.Funcion.desde_texto("x**2")
        primera = r.suma_riemann(cuadrado, 0, 1, 12, "aleatoria", semilla=42).valor
        segunda = r.suma_riemann(cuadrado, 0, 1, 12, "aleatoria", semilla=42).valor
        otra = r.suma_riemann(cuadrado, 0, 1, 12, "aleatoria", semilla=43).valor
        self.assertEqual(primera, segunda)
        self.assertNotEqual(primera, otra)

    def test_intervalo_al_reves_o_vacio(self):
        with self.assertRaises(ValueError):
            r.particion(1, 1, 5)
        with self.assertRaises(ValueError):
            r.particion(2, 1, 5)
        with self.assertRaises(ValueError):
            r.particion(0, 1, 0)


class Convergencia(unittest.TestCase):

    def setUp(self):
        self.cuadrado = r.Funcion.desde_texto("x**2")

    def test_izquierda_es_de_orden_1(self):
        filas = r.tabla_convergencia(self.cuadrado, 0, 1, "izquierda",
                                     n_inicial=8, pasos=5, referencia=1 / 3)
        self.assertAlmostEqual(filas[-1].razon, 2.0, places=1)

    def test_punto_medio_es_de_orden_2(self):
        filas = r.tabla_convergencia(self.cuadrado, 0, 1, "medio",
                                     n_inicial=8, pasos=5, referencia=1 / 3)
        self.assertAlmostEqual(filas[-1].razon, 4.0, places=1)

    def test_el_error_no_aparece_sin_referencia(self):
        filas = r.tabla_convergencia(self.cuadrado, 0, 1, "medio", pasos=2)
        self.assertTrue(all(fila.error is None and fila.razon is None for fila in filas))

    def test_la_referencia_acierta_varias_cifras(self):
        casos = [
            ("x**2", 0, 1, 1 / 3),
            ("sin(x)", 0, math.pi, 2.0),
            ("1/x", 1, math.e, 1.0),
            ("exp(-x**2)", -3, 3, math.sqrt(math.pi) * math.erf(3)),
            ("sqrt(1-x**2)", -1, 1, math.pi / 2),  # semicírculo: derivada infinita en los bordes
        ]
        for expresion, a, b, exacto in casos:
            valor = r.integral_referencia(r.Funcion.desde_texto(expresion), a, b)
            self.assertAlmostEqual(valor, exacto, places=6, msg=expresion)


class LecturaDeExpresiones(unittest.TestCase):

    def test_rechaza_lo_que_no_es_aritmetica(self):
        peligrosas = [
            '__import__("os").system("ls")',
            'open("/etc/passwd").read()',
            "(1).__class__.__mro__",
            "x.real",
            "[1, 2, 3][0]",
            "lambda x: x",
            "x if x > 0 else 0",
            "{1: 2}",
            "'texto'",
            "globals()",
            "eval('1')",
            "os.system('ls')",
        ]
        for expresion in peligrosas:
            with self.assertRaises(r.ErrorDeExpresion, msg=expresion):
                r.Funcion.desde_texto(expresion)

    def test_rechaza_lo_que_no_se_entiende(self):
        for expresion in ("2x", "x +", "", "   ", "sen(x)", "y**2"):
            with self.assertRaises(r.ErrorDeExpresion, msg=expresion):
                r.Funcion.desde_texto(expresion)

    def test_acepta_la_notacion_de_clase(self):
        self.assertAlmostEqual(r.Funcion.desde_texto("x^2")(3), 9.0)
        self.assertAlmostEqual(r.Funcion.desde_texto("2*x + 1")(4), 9.0)
        self.assertAlmostEqual(r.Funcion.desde_texto("sqrt(x)/log(e)")(9), 3.0)
        self.assertAlmostEqual(r.Funcion.desde_texto("max(x, 1-x)")(0.25), 0.75)

    def test_los_limites_aceptan_expresiones(self):
        self.assertAlmostEqual(r.numero("pi/2"), math.pi / 2)
        self.assertAlmostEqual(r.numero("-sqrt(2)"), -math.sqrt(2))
        self.assertAlmostEqual(r.numero("1/3"), 1 / 3)
        with self.assertRaises(r.ErrorDeExpresion):
            r.numero("x")  # sin función no hay variable que valga

    def test_avisa_donde_no_esta_definida(self):
        for expresion, punto in (("1/x", 0.0), ("sqrt(x)", -1.0), ("log(x)", 0.0)):
            with self.assertRaises(r.ErrorDeDominio, msg=expresion):
                r.Funcion.desde_texto(expresion)(punto)


class Dibujo(unittest.TestCase):

    def test_el_lienzo_tiene_el_tamano_pedido(self):
        f = r.Funcion.desde_texto("x**2")
        texto = r.dibujar(f, r.suma_riemann(f, 0, 1, 6), ancho=40, alto=10)
        lineas = texto.splitlines()
        self.assertEqual(len(lineas), 13)  # 10 filas + eje + números + leyenda
        self.assertIn("▓", texto)
        self.assertIn("•", texto)

    def test_ascii_puro_no_deja_caracteres_raros(self):
        f = r.Funcion.desde_texto("sin(x)")
        texto = r.dibujar(f, r.suma_riemann(f, 0, 6, 8, "medio"), ancho=30, alto=8,
                          ascii_puro=True)
        self.assertTrue(texto.isascii())

    def test_dibuja_aunque_f_falle_en_alguna_columna(self):
        f = r.Funcion.desde_texto("1/x")
        texto = r.dibujar(f, r.suma_riemann(f, -1, 1, 3, "izquierda"), ancho=20, alto=6)
        self.assertEqual(len(texto.splitlines()), 9)

    def test_una_regla_sin_rectangulos_avisa(self):
        f = r.Funcion.desde_texto("x**2")
        texto = r.dibujar(f, r.simpson(f, 0, 1, 4), ancho=20, alto=6)
        self.assertIn("no dibuja figura", texto)


class LineaDeComandos(unittest.TestCase):

    def _correr(self, *argumentos):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = r.main(list(argumentos))
        return codigo, salida.getvalue()

    def test_corrida_completa(self):
        codigo, salida = self._correr("-f", "x**2", "-a", "0", "-b", "1", "-n", "8",
                                      "--detalle", "--comparar", "--tabla", "--dibujo",
                                      "--pasos", "2")
        self.assertEqual(codigo, 0)
        self.assertIn("suma de Riemann", salida)
        self.assertIn("0.2734375", salida)
        self.assertIn("razón", salida)

    def test_limites_escritos_como_expresion(self):
        codigo, salida = self._correr("-f", "sin(x)", "-a", "0", "-b", "pi", "-n", "50")
        self.assertEqual(codigo, 0)
        self.assertIn("1.99", salida)

    def test_valor_exacto_a_mano(self):
        codigo, salida = self._correr("-f", "x**2", "--exacta", "1/3", "-n", "4")
        self.assertEqual(codigo, 0)
        self.assertIn("referencia", salida)

    def test_sin_referencia_no_muestra_error(self):
        codigo, salida = self._correr("-f", "x**2", "--sin-referencia")
        self.assertEqual(codigo, 0)
        self.assertNotIn("referencia", salida)

    def test_expresion_invalida_devuelve_codigo_2(self):
        # Dos rechazos distintos: por nombre desconocido y por nodo prohibido.
        codigo, salida = self._correr("-f", "__import__('os')", "-n", "4")
        self.assertEqual(codigo, 2)
        self.assertIn("no es una variable", salida)

        codigo, salida = self._correr("-f", "open('/etc/passwd').read()", "-n", "4")
        self.assertEqual(codigo, 2)
        self.assertIn("no está permitido", salida)

    def test_intervalo_al_reves_devuelve_codigo_2(self):
        codigo, salida = self._correr("-f", "x", "-a", "3", "-b", "1")
        self.assertEqual(codigo, 2)
        self.assertIn("a < b", salida)

    def test_la_demo_corre_sola(self):
        codigo, salida = self._correr("--demo")
        self.assertEqual(codigo, 0)
        self.assertIn("1/3", salida)


if __name__ == "__main__":
    unittest.main()
