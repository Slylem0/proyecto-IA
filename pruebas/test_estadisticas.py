"""Pruebas del panel de estadisticas (issue #16)."""

import unittest

from gui.estadisticas import armar_fila
from modelo.estado import Estado
from modelo.problema import ProblemaHorario
from modelo.resultado import Resultado

CALCULO = ("Calculo", "Prof_A", "G1")
FISICA = ("Fisica", "Prof_B", "G1")

PROBLEMA = ProblemaHorario([CALCULO, FISICA], ["S101"], ["Lunes", "Martes"],
                           ["07-09", "09-11"])


class TestArmarFila(unittest.TestCase):

    def test_fila_con_solucion(self):
        # las dos clases son de G1 el lunes: 2 clases + 1 pareja = 3
        horario = Estado({CALCULO: ("Lunes", "07-09", "S101"),
                          FISICA: ("Lunes", "09-11", "S101")}, [])
        r = Resultado("BFS", horario, 12, 0.5)
        self.assertEqual(armar_fila(PROBLEMA, r),
                         ("BFS", 12, "0.5000", "Si", 3))

    def test_fila_sin_solucion(self):
        r = Resultado("IDDFS", None, 40, 0.01234)
        self.assertEqual(armar_fila(PROBLEMA, r),
                         ("IDDFS", 40, "0.0123", "No", "-"))


if __name__ == "__main__":
    unittest.main()
