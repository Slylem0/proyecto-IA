"""Pruebas de la busqueda A* (issue #13)."""

import unittest

from algoritmos.a_estrella import a_estrella
from algoritmos.costo_uniforme import costo_uniforme
from modelo.problema import ProblemaHorario
from modelo.resultado import Resultado

PROBLEMA = ProblemaHorario(
    [("Calculo", "Prof_A", "G1"), ("Algebra", "Prof_A", "G2"),
     ("Fisica", "Prof_B", "G1"), ("Programacion", "Prof_C", "G2")],
    ["S101", "S102"], ["Lunes", "Martes", "Miercoles"],
    ["07-09", "09-11", "11-13"])

# 6 clases en 2 dias: no se pueden repartir del todo y hay que elegir
DIFICIL = ProblemaHorario(
    [("Calculo", "Prof_A", "G1"), ("Algebra", "Prof_A", "G2"),
     ("Fisica", "Prof_B", "G1"), ("Programacion", "Prof_C", "G2"),
     ("Quimica", "Prof_B", "G2"), ("Ingles", "Prof_C", "G1")],
    ["S1", "S2"], ["Lunes", "Martes"], ["07-09", "09-11", "11-13"])

SIN_SOLUCION = ProblemaHorario(
    [("A", "P1", "G1"), ("B", "P1", "G1")], ["S1"], ["Lunes"], ["07-09"])


class TestAEstrella(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # costo uniforme en DIFICIL tarda un par de segundos: se corre
        # una sola vez para todas las pruebas
        cls.ucs_dificil = costo_uniforme(DIFICIL)

    def test_devuelve_resultado(self):
        r = a_estrella(PROBLEMA)
        self.assertIsInstance(r, Resultado)
        self.assertEqual(r.algoritmo, "A*")
        self.assertTrue(r.encontrada)

    def test_solucion_valida(self):
        r = a_estrella(PROBLEMA)
        self.assertTrue(PROBLEMA.es_solucion_valida(r.solucion))

    def test_mismo_costo_que_costo_uniforme(self):
        # las dos son optimas: tienen que dar el mismo costo
        a = a_estrella(PROBLEMA)
        u = costo_uniforme(PROBLEMA)
        self.assertEqual(PROBLEMA.costo_horario(a.solucion),
                         PROBLEMA.costo_horario(u.solucion))
        a = a_estrella(DIFICIL)
        self.assertEqual(DIFICIL.costo_horario(a.solucion),
                         DIFICIL.costo_horario(self.ucs_dificil.solucion))

    def test_explora_menos_que_costo_uniforme(self):
        a = a_estrella(DIFICIL)
        self.assertLess(a.nodos_explorados, self.ucs_dificil.nodos_explorados)

    def test_heuristica_buena_explora_menos(self):
        # la heuristica del #12 explora menos que solo contar pendientes
        buena = a_estrella(DIFICIL)
        simple = a_estrella(DIFICIL, DIFICIL.heuristica_pendientes)
        self.assertLess(buena.nodos_explorados, simple.nodos_explorados)
        self.assertEqual(DIFICIL.costo_horario(buena.solucion),
                         DIFICIL.costo_horario(simple.solucion))

    def test_sin_solucion(self):
        r = a_estrella(SIN_SOLUCION)
        self.assertFalse(r.encontrada)
        self.assertIsNone(r.solucion)


if __name__ == "__main__":
    unittest.main()
