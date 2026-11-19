"""Pruebas de la heuristica de A* (issue #12)."""

import unittest

from algoritmos.costo_uniforme import costo_uniforme
from modelo.estado import Estado
from modelo.problema import Problema, ProblemaHorario

CALCULO = ("Calculo", "Prof_A", "G1")
ALGEBRA = ("Algebra", "Prof_A", "G2")
FISICA = ("Fisica", "Prof_B", "G1")
PROGRA = ("Programacion", "Prof_C", "G2")

PROBLEMA = ProblemaHorario(
    [CALCULO, ALGEBRA, FISICA, PROGRA],
    ["S101", "S102"],
    ["Lunes", "Martes", "Miercoles"],
    ["07-09", "09-11", "11-13"],
)

# un solo dia: todo choca y la heuristica tiene que cobrarlo
UN_DIA = ProblemaHorario(
    [CALCULO, ALGEBRA, FISICA, PROGRA],
    ["S101", "S102"],
    ["Lunes"],
    ["07-09", "09-11", "11-13"],
)


def estados_hasta(problema, profundidad):
    """Todos los estados alcanzables con a lo sumo esa profundidad."""
    nivel = [problema.estado_inicial()]
    todos = list(nivel)
    for _ in range(profundidad):
        siguiente = []
        for estado in nivel:
            for accion, sucesor in problema.sucesores(estado):
                siguiente.append(sucesor)
        todos.extend(siguiente)
        nivel = siguiente
    return todos


class TestHeuristica(unittest.TestCase):

    def test_meta_vale_cero(self):
        meta = costo_uniforme(PROBLEMA).solucion
        self.assertEqual(PROBLEMA.heuristica(meta), 0)

    def test_inicial_es_clases_pendientes(self):
        # sin nada asignado ningun dia esta cargado
        self.assertEqual(PROBLEMA.heuristica(PROBLEMA.estado_inicial()), 4)

    def test_cobra_el_dia_ocupado(self):
        # con un solo dia, Calculo el lunes hace que Fisica (G1) y
        # Algebra (Prof_A) cuesten al menos 2
        estado = Estado({CALCULO: ("Lunes", "07-09", "S101")},
                        [ALGEBRA, FISICA, PROGRA])
        self.assertEqual(UN_DIA.heuristica(estado), 2 + 2 + 1)

    def test_admisible(self):
        # h del inicio nunca pasa del costo optimo real
        for problema in (PROBLEMA, UN_DIA):
            optimo = problema.costo_horario(costo_uniforme(problema).solucion)
            self.assertLessEqual(
                problema.heuristica(problema.estado_inicial()), optimo)

    def test_consistente(self):
        # h(n) <= costo(n, a) + h(n') en todos los pasos de los 2 primeros niveles
        for problema in (PROBLEMA, UN_DIA):
            for estado in estados_hasta(problema, 2):
                for accion, sucesor in problema.sucesores(estado):
                    self.assertLessEqual(
                        problema.heuristica(estado),
                        problema.costo(estado, accion)
                        + problema.heuristica(sucesor))

    def test_no_es_peor_que_contar_pendientes(self):
        for estado in estados_hasta(UN_DIA, 2):
            self.assertGreaterEqual(UN_DIA.heuristica(estado),
                                    UN_DIA.heuristica_pendientes(estado))

    def test_problema_base_vale_cero(self):
        self.assertEqual(Problema().heuristica(Estado()), 0)


if __name__ == "__main__":
    unittest.main()
