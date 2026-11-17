# pruebas/test_restricciones.py
# Pruebas unitarias de las cuatro restricciones duras (issue 6).
# Una prueba por cada restriccion, mas la combinacion de las tres
# en es_valida y la comprobacion de solucion valida.

import unittest

from modelo.estado import Accion, Estado
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

CALCULO, ALGEBRA, FISICA, PROGRAMACION = CLASES


def problema():
    return ProblemaHorario(CLASES, SALONES, DIAS, FRANJAS)


class TestChoqueDeSalon(unittest.TestCase):
    """Restriccion 1: un salon no puede tener dos clases en la misma franja."""

    def setUp(self):
        self.p = problema()
        # Calculo ocupa S101 el Lunes 07-09
        self.base = Estado({CALCULO: ("Lunes", "07-09", "S101")}, CLASES[1:])

    def test_choque_mismo_salon_misma_franja(self):
        self.assertTrue(self.p.choca_salon(self.base, "Lunes", "07-09", "S101"))
        # y por lo tanto es_valida rechaza la accion
        accion = Accion(PROGRAMACION, "Lunes", "07-09", "S101")
        self.assertFalse(self.p.es_valida(self.base, accion))

    def test_sin_choque_otro_salon(self):
        # Programacion no comparte profesor ni grupo con Calculo
        self.assertFalse(self.p.choca_salon(self.base, "Lunes", "07-09", "S102"))
        accion = Accion(PROGRAMACION, "Lunes", "07-09", "S102")
        self.assertTrue(self.p.es_valida(self.base, accion))

    def test_sin_choque_otra_franja_u_otro_dia(self):
        self.assertFalse(self.p.choca_salon(self.base, "Lunes", "09-11", "S101"))
        self.assertFalse(self.p.choca_salon(self.base, "Martes", "07-09", "S101"))


class TestChoqueDeProfesor(unittest.TestCase):
    """Restriccion 2: un profesor no puede dictar dos clases en la misma franja."""

    def setUp(self):
        self.p = problema()
        # Calculo y Algebra son de Prof_A; Calculo esta en Lunes 07-09
        self.base = Estado({CALCULO: ("Lunes", "07-09", "S101")}, CLASES[1:])

    def test_choque_mismo_profesor_misma_franja(self):
        # el choque aplica aunque sea en otro salon
        self.assertTrue(self.p.choca_profesor(self.base, "Prof_A", "Lunes", "07-09"))
        accion = Accion(ALGEBRA, "Lunes", "07-09", "S102")
        self.assertFalse(self.p.es_valida(self.base, accion))

    def test_sin_choque_otro_profesor_misma_franja(self):
        self.assertFalse(self.p.choca_profesor(self.base, "Prof_C", "Lunes", "07-09"))
        accion = Accion(PROGRAMACION, "Lunes", "07-09", "S102")
        self.assertTrue(self.p.es_valida(self.base, accion))

    def test_sin_choque_otra_franja_u_otro_dia(self):
        self.assertFalse(self.p.choca_profesor(self.base, "Prof_A", "Lunes", "09-11"))
        self.assertFalse(self.p.choca_profesor(self.base, "Prof_A", "Martes", "07-09"))


class TestChoqueDeGrupo(unittest.TestCase):
    """Restriccion 3: un grupo no puede tener dos clases en la misma franja."""

    def setUp(self):
        self.p = problema()
        # Calculo es del grupo G1 y esta en Lunes 07-09
        self.base = Estado({CALCULO: ("Lunes", "07-09", "S101")}, CLASES[1:])

    def test_choque_mismo_grupo_misma_franja(self):
        self.assertTrue(self.p.choca_grupo(self.base, "G1", "Lunes", "07-09"))
        # Fisica es del grupo G1: choque aunque el profesor y el salon cambien
        accion = Accion(FISICA, "Lunes", "07-09", "S102")
        self.assertFalse(self.p.es_valida(self.base, accion))

    def test_sin_choque_otro_grupo_misma_franja(self):
        self.assertFalse(self.p.choca_grupo(self.base, "G2", "Lunes", "07-09"))
        # Programacion es del grupo G2 y de otro profesor:
        # no choca por grupo (ni por nada) en esa franja
        accion = Accion(PROGRAMACION, "Lunes", "07-09", "S102")
        self.assertTrue(self.p.es_valida(self.base, accion))

    def test_sin_choque_otra_franja_u_otro_dia(self):
        self.assertFalse(self.p.choca_grupo(self.base, "G1", "Lunes", "09-11"))
        self.assertFalse(self.p.choca_grupo(self.base, "G1", "Martes", "07-09"))


class TestClaseAsignadaUnaVez(unittest.TestCase):
    """Restriccion 4: cada clase debe asignarse exactamente una vez."""

    def setUp(self):
        self.p = problema()

    def test_pendiente_ya_asignada_no_cumple(self):
        # estado construido a mano con una clase en asignaciones y en pendientes
        malo = Estado({CALCULO: ("Lunes", "07-09", "S101")}, [CALCULO, ALGEBRA])
        self.assertFalse(self.p.restricciones_cumplidas(malo))

    def test_estado_normal_cumple(self):
        # en los estados que genera sucesores las pendientes nunca
        # incluyen clases ya asignadas
        base = Estado({CALCULO: ("Lunes", "07-09", "S101")}, CLASES[1:])
        self.assertTrue(self.p.restricciones_cumplidas(base))

    def test_todas_las_clases_aparecen_una_vez_en_la_solucion(self):
        actual = self.p.estado_inicial()
        while actual.pendientes:
            accion, actual = self.p.sucesores(actual)[0]
        asignadas = list(actual.asignaciones.keys())
        # sin repetidas y exactamente las mismas clases del problema
        self.assertEqual(len(asignadas), len(set(asignadas)))
        self.assertEqual(set(asignadas), set(CLASES))
        self.assertEqual(actual.pendientes, ())


class TestRestriccionesEnConjunto(unittest.TestCase):

    def setUp(self):
        self.p = problema()

    def test_es_valida_combina_las_tres_verificaciones(self):
        # Calculo: Prof_A y G1, en Lunes 07-09 S101
        base = Estado({CALCULO: ("Lunes", "07-09", "S101")}, CLASES[1:])
        # Algebra choca solo por profesor
        self.assertFalse(self.p.es_valida(
            base, Accion(ALGEBRA, "Lunes", "07-09", "S102")))
        # Fisica choca solo por grupo
        self.assertFalse(self.p.es_valida(
            base, Accion(FISICA, "Lunes", "07-09", "S102")))
        # Programacion no choca por nada en el otro salon
        self.assertTrue(self.p.es_valida(
            base, Accion(PROGRAMACION, "Lunes", "07-09", "S102")))

    def test_es_solucion_valida(self):
        # camino completo con sucesores: debe ser solucion valida
        actual = self.p.estado_inicial()
        while actual.pendientes:
            accion, actual = self.p.sucesores(actual)[0]
        self.assertTrue(self.p.es_solucion_valida(actual))
        # un estado incompleto no es solucion
        self.assertFalse(self.p.es_solucion_valida(self.p.estado_inicial()))
        # un estado con conflicto tampoco, aunque este completo
        malo = Estado({c: ("Lunes", "07-09", "S101") for c in CLASES}, [])
        self.assertFalse(self.p.es_solucion_valida(malo))


if __name__ == "__main__":
    unittest.main()
