"""Pruebas de la funcion de costo (issue #10)."""

import unittest

from modelo.estado import Accion, Estado
from modelo.problema import ProblemaHorario

CALCULO = ("Calculo", "Prof_A", "G1")
ALGEBRA = ("Algebra", "Prof_A", "G2")
FISICA = ("Fisica", "Prof_B", "G1")
PROGRA = ("Programacion", "Prof_C", "G2")

PROBLEMA = ProblemaHorario(
    [CALCULO, ALGEBRA, FISICA, PROGRA],
    ["S101", "S102"],
    ["Lunes", "Martes"],
    ["07-09", "09-11"],
)


class TestCosto(unittest.TestCase):

    def test_primera_clase_cuesta_1(self):
        estado = PROBLEMA.estado_inicial()
        accion = Accion(CALCULO, "Lunes", "07-09", "S101")
        self.assertEqual(PROBLEMA.costo(estado, accion), 1)

    def test_mismo_grupo_mismo_dia_suma_1(self):
        estado = Estado({CALCULO: ("Lunes", "07-09", "S101")}, [FISICA])
        accion = Accion(FISICA, "Lunes", "09-11", "S101")
        self.assertEqual(PROBLEMA.costo(estado, accion), 2)

    def test_otro_dia_no_suma(self):
        estado = Estado({CALCULO: ("Lunes", "07-09", "S101")}, [FISICA])
        accion = Accion(FISICA, "Martes", "07-09", "S101")
        self.assertEqual(PROBLEMA.costo(estado, accion), 1)

    def test_mismo_profesor_mismo_dia_suma_1(self):
        estado = Estado({CALCULO: ("Lunes", "07-09", "S101")}, [ALGEBRA])
        accion = Accion(ALGEBRA, "Lunes", "09-11", "S102")
        self.assertEqual(PROBLEMA.costo(estado, accion), 2)

    def test_costo_horario_es_la_suma_de_los_pasos(self):
        # las 4 clases el lunes, sumando costo() en cada paso
        lugares = [
            ("Lunes", "07-09", "S101"),
            ("Lunes", "07-09", "S102"),
            ("Lunes", "09-11", "S101"),
            ("Lunes", "09-11", "S102"),
        ]
        estado = PROBLEMA.estado_inicial()
        suma = 0
        for clase, (dia, franja, salon) in zip(PROBLEMA.clases, lugares):
            accion = Accion(clase, dia, franja, salon)
            suma += PROBLEMA.costo(estado, accion)
            asignadas = estado.asignaciones
            asignadas[clase] = (dia, franja, salon)
            estado = Estado(asignadas, estado.pendientes[1:])
        # 4 clases + Calculo/Fisica (G1) + Algebra/Programacion (G2)
        # + Calculo/Algebra (Prof_A) = 7
        self.assertEqual(suma, 7)
        self.assertEqual(suma, PROBLEMA.costo_horario(estado))


if __name__ == "__main__":
    unittest.main()
