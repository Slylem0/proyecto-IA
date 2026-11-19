"""Pruebas de la grilla del horario (issue #15)."""

import unittest

from gui.grilla import armar_celdas
from modelo.estado import Estado

CALCULO = ("Calculo", "Prof_A", "G1")
FISICA = ("Fisica", "Prof_B", "G1")
PROGRA = ("Programacion", "Prof_C", "G2")


class TestArmarCeldas(unittest.TestCase):

    def test_una_clase_por_celda(self):
        horario = Estado({CALCULO: ("Lunes", "07-09", "S101"),
                          FISICA: ("Martes", "09-11", "S102")}, [])
        celdas = armar_celdas(horario)
        self.assertEqual(celdas[("Lunes", "07-09")],
                         ["Calculo (G1)\nProf_A\nS101"])
        self.assertEqual(celdas[("Martes", "09-11")],
                         ["Fisica (G1)\nProf_B\nS102"])

    def test_dos_clases_en_la_misma_franja(self):
        # distinto salon, profesor y grupo: pueden ir a la misma hora
        horario = Estado({CALCULO: ("Lunes", "07-09", "S101"),
                          PROGRA: ("Lunes", "07-09", "S102")}, [])
        celdas = armar_celdas(horario)
        self.assertEqual(len(celdas[("Lunes", "07-09")]), 2)

    def test_celdas_libres_no_aparecen(self):
        horario = Estado({CALCULO: ("Lunes", "07-09", "S101")}, [])
        celdas = armar_celdas(horario)
        self.assertNotIn(("Martes", "07-09"), celdas)
        self.assertEqual(len(celdas), 1)


if __name__ == "__main__":
    unittest.main()
