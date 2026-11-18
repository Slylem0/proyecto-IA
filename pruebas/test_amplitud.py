# pruebas/test_amplitud.py
# Pruebas de la busqueda en amplitud (issue 8).
# Se comprueba la cola FIFO propia, el Resultado devuelto, la validez
# de la solucion, las estadisticas y el caso sin solucion.

import unittest

from algoritmos.amplitud import bfs, Cola
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

# problema sin solucion: las dos clases comparten profesor y grupo, y
# solo hay un salon y una franja, asi que la segunda clase se queda sin
# combinaciones posibles
PROBLEMA_SIN_SOLUCION = ProblemaHorario(
    [("A", "P1", "G1"), ("B", "P1", "G1")],
    ["S1"], ["Lunes"], ["07-09"])


class TestColaPropia(unittest.TestCase):

    def test_cola_fifo(self):
        c = Cola()
        self.assertTrue(c.vacia())
        # desencolar en cola vacia devuelve None
        self.assertIsNone(c.desencolar())
        for x in [1, 2, 3]:
            c.encolar(x)
        self.assertFalse(c.vacia())
        # sale en el mismo orden en que entro
        self.assertEqual(c.desencolar(), 1)
        self.assertEqual(c.desencolar(), 2)
        self.assertEqual(c.desencolar(), 3)
        self.assertTrue(c.vacia())


class TestBfs(unittest.TestCase):

    def setUp(self):
        self.p = ProblemaHorario(CLASES, SALONES, DIAS, FRANJAS)

    def test_devuelve_un_resultado(self):
        self.assertIsInstance(bfs(self.p), Resultado)

    def test_encuentra_solucion_valida(self):
        r = bfs(self.p)
        self.assertTrue(r.encontrada)
        self.assertTrue(self.p.es_meta(r.solucion))
        # comprobacion extra con la interfaz de la issue 6
        self.assertTrue(self.p.es_solucion_valida(r.solucion))
        self.assertEqual(len(r.solucion.asignaciones), len(CLASES))

    def test_cuenta_nodos_y_tiempo(self):
        r = bfs(self.p)
        self.assertIsInstance(r.nodos_explorados, int)
        self.assertGreater(r.nodos_explorados, 0)
        self.assertGreaterEqual(r.tiempo, 0.0)

    def test_busqueda_reproducible(self):
        # con sucesores y cola deterministas, dos corridas deben dar
        # exactamente la misma solucion y el mismo conteo de nodos
        r1 = bfs(self.p)
        r2 = bfs(self.p)
        self.assertEqual(r1.solucion, r2.solucion)
        self.assertEqual(r1.nodos_explorados, r2.nodos_explorados)

    def test_sin_solucion_termina_y_devuelve_none(self):
        # debe terminar (la cola se vacia) y reportar que no hay solucion
        r = bfs(PROBLEMA_SIN_SOLUCION)
        self.assertFalse(r.encontrada)
        self.assertIsNone(r.solucion)
        # igual expandio el estado inicial antes de quedarse sin cola
        self.assertGreater(r.nodos_explorados, 0)


if __name__ == "__main__":
    unittest.main()
