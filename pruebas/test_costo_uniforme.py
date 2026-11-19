"""Pruebas de la cola de prioridad y de costo uniforme (issue #11)."""

import unittest

from algoritmos.amplitud import bfs
from algoritmos.cola_prioridad import ColaPrioridad
from algoritmos.costo_uniforme import costo_uniforme
from modelo.problema import ProblemaHorario
from modelo.resultado import Resultado

PROBLEMA = ProblemaHorario(
    [("Calculo", "Prof_A", "G1"), ("Algebra", "Prof_A", "G2"),
     ("Fisica", "Prof_B", "G1"), ("Programacion", "Prof_C", "G2")],
    ["S101", "S102"], ["Lunes", "Martes", "Miercoles"],
    ["07-09", "09-11", "11-13"])

SIN_SOLUCION = ProblemaHorario(
    [("A", "P1", "G1"), ("B", "P1", "G1")], ["S1"], ["Lunes"], ["07-09"])


class TestColaPrioridad(unittest.TestCase):

    def test_sale_el_menor(self):
        c = ColaPrioridad()
        for p in [5, 1, 4, 2, 3]:
            c.insertar(p, "x%d" % p)
        salida = [c.extraer()[0] for _ in range(5)]
        self.assertEqual(salida, [1, 2, 3, 4, 5])
        self.assertTrue(c.vacia())

    def test_empate_sale_el_primero_que_entro(self):
        c = ColaPrioridad()
        c.insertar(1, "primero")
        c.insertar(1, "segundo")
        self.assertEqual(c.extraer()[1], "primero")


class TestCostoUniforme(unittest.TestCase):

    def test_devuelve_resultado(self):
        r = costo_uniforme(PROBLEMA)
        self.assertIsInstance(r, Resultado)
        self.assertEqual(r.algoritmo, "Costo uniforme")
        self.assertTrue(r.encontrada)

    def test_solucion_valida(self):
        r = costo_uniforme(PROBLEMA)
        self.assertTrue(PROBLEMA.es_solucion_valida(r.solucion))

    def test_encuentra_el_horario_mas_barato(self):
        # 4 clases sin repetir grupo ni profesor el mismo dia: costo 4
        r = costo_uniforme(PROBLEMA)
        self.assertEqual(PROBLEMA.costo_horario(r.solucion), 4)

    def test_no_es_peor_que_bfs(self):
        ucs = costo_uniforme(PROBLEMA)
        amplitud = bfs(PROBLEMA)
        self.assertLessEqual(PROBLEMA.costo_horario(ucs.solucion),
                             PROBLEMA.costo_horario(amplitud.solucion))

    def test_sin_solucion(self):
        r = costo_uniforme(SIN_SOLUCION)
        self.assertFalse(r.encontrada)
        self.assertIsNone(r.solucion)


if __name__ == "__main__":
    unittest.main()
