# pruebas/test_profundidad_iterativa.py
# Pruebas de la busqueda en profundidad iterativa IDDFS (issue 9).
# Se comprueba la solucion, el limite de profundidad, la acumulacion
# de nodos entre iteraciones y el caso sin solucion.

import unittest

from algoritmos.amplitud import bfs
from algoritmos.profundidad_iterativa import profundidad_iterativa
from modelo.resultado import Resultado
from modelo.problema import ProblemaHorario

CLASES = [
    ("Calculo", "Prof_A", "G1"),
    ("Algebra", "Prof_A", "G2"),
    ("Fisica", "Prof_B", "G1"),
    ("Programacion", "Prof_C", "G2"),
]
SALONES = ["S101", "S102"]
DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
FRANJAS = ["07-09", "09-11", "11-13"]

# problema sin solucion (mismo profesor y grupo, un salon y una franja)
PROBLEMA_SIN_SOLUCION = ProblemaHorario(
    [("A", "P1", "G1"), ("B", "P1", "G1")],
    ["S1"], ["Lunes"], ["07-09"])


class TestIddfs(unittest.TestCase):

    def setUp(self):
        self.p = ProblemaHorario(CLASES, SALONES, DIAS, FRANJAS)

    def test_devuelve_un_resultado(self):
        self.assertIsInstance(profundidad_iterativa(self.p), Resultado)

    def test_encuentra_solucion_valida(self):
        r = profundidad_iterativa(self.p)
        self.assertTrue(r.hay_solucion())
        self.assertTrue(self.p.es_meta(r.solucion))
        self.assertTrue(self.p.es_solucion_valida(r.solucion))
        self.assertEqual(len(r.solucion.asignaciones), len(CLASES))

    def test_cuenta_nodos_y_tiempo(self):
        r = profundidad_iterativa(self.p)
        self.assertIsInstance(r.nodos_explorados, int)
        self.assertGreater(r.nodos_explorados, 0)
        self.assertGreaterEqual(r.tiempo, 0.0)

    def test_busqueda_reproducible(self):
        r1 = profundidad_iterativa(self.p)
        r2 = profundidad_iterativa(self.p)
        self.assertEqual(r1.solucion, r2.solucion)
        self.assertEqual(r1.nodos_explorados, r2.nodos_explorados)

    # --- limite de profundidad creciente ---------------------------------

    def test_limite_menor_que_la_solucion_no_encuentra(self):
        # la solucion necesita 4 asignaciones; con limite 3 no hay meta
        r = profundidad_iterativa(self.p, limite_max=3)
        self.assertFalse(r.hay_solucion())
        self.assertIsNone(r.solucion)
        self.assertGreater(r.nodos_explorados, 0)

    def test_limite_exacto_si_encuentra(self):
        r = profundidad_iterativa(self.p, limite_max=4)
        self.assertTrue(r.hay_solucion())

    def test_nodos_se_acumulan_entre_iteraciones(self):
        # con limite_max=2 se completan las iteraciones de limite 0, 1 y 2.
        # El arbol es determinista (siempre se asigna la primera pendiente):
        #   limite 0: 1 nodo (solo el inicial)
        #   limite 1: 1 + 30 sucesores (todas las combinaciones son validas)
        #   limite 2: 1 + 30*(1 + 28) por clase, porque a Algebra
        #             (mismo profesor que Calculo) le bloquean los 2 salones
        #             en la franja de Calculo: 1 + 30 + 30*29 = 871
        # total acumulado = 1 + 31 + 871 = 903
        r = profundidad_iterativa(self.p, limite_max=2)
        self.assertEqual(r.nodos_explorados, 903)
        self.assertFalse(r.hay_solucion())

    def test_nodos_explorados_mayores_que_bfs(self):
        # IDDFS re-explora los niveles de cada iteracion, entonces sobre
        # este problema expande mas nodos que BFS (que no repite niveles)
        r_bfs = bfs(self.p)
        r_iddfs = profundidad_iterativa(self.p)
        self.assertGreater(r_iddfs.nodos_explorados, r_bfs.nodos_explorados)

    def test_sin_solucion_termina_y_devuelve_none(self):
        # sin limite explicito se llega hasta el numero de clases
        # (2 en este problema) y se termina sin colgarse
        r = profundidad_iterativa(PROBLEMA_SIN_SOLUCION)
        self.assertFalse(r.hay_solucion())
        self.assertIsNone(r.solucion)
        self.assertGreater(r.nodos_explorados, 0)


if __name__ == "__main__":
    unittest.main()
