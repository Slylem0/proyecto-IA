# pruebas/test_dominio.py
# Pruebas del dominio por clase y del orden de seleccion (issue 5).
# - dominio(estado, clase): combinaciones (dia, franja, salon) validas
# - siguiente_clase(estado): la primera clase pendiente (orden de entrada)

import unittest

from modelo.estado import Estado
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


class TestDominio(unittest.TestCase):

    def setUp(self):
        self.p = ProblemaHorario(CLASES, SALONES, DIAS, FRANJAS)

    # --- dominio por clase ------------------------------------------------

    def test_dominio_del_estado_inicial(self):
        # sin clases asignadas, todas las combinaciones son validas:
        # 5 dias * 3 franjas * 2 salones = 30
        dom = self.p.dominio(self.p.estado_inicial(), CLASES[0])
        self.assertEqual(len(dom), 30)
        self.assertEqual(len(set(dom)), 30)  # sin repeticiones
        for dia, franja, salon in dom:
            self.assertIn(dia, DIAS)
            self.assertIn(franja, FRANJAS)
            self.assertIn(salon, SALONES)

    def test_dominio_excluye_salon_ocupado(self):
        # Calculo (Prof_A, G1) esta en Lunes 07-09 S101.
        # Programacion (Prof_C, G2) no comparte profesor ni grupo,
        # entonces solo choca por salon en esa franja
        base = Estado({CLASES[0]: ("Lunes", "07-09", "S101")}, CLASES[1:])
        dom = self.p.dominio(base, CLASES[3])
        self.assertEqual(len(dom), 29)  # 30 - 1
        self.assertNotIn(("Lunes", "07-09", "S101"), dom)
        # el otro salon de esa franja sigue disponible
        self.assertIn(("Lunes", "07-09", "S102"), dom)

    def test_dominio_excluye_por_grupo(self):
        # Fisica (Prof_B, G1) comparte el grupo G1 con Calculo (Prof_A, G1):
        # en toda la franja Lunes 07-09 se bloquean los 2 salones
        base = Estado({CLASES[0]: ("Lunes", "07-09", "S101")}, CLASES[1:])
        dom = self.p.dominio(base, CLASES[2])
        self.assertEqual(len(dom), 28)
        self.assertNotIn(("Lunes", "07-09", "S101"), dom)
        self.assertNotIn(("Lunes", "07-09", "S102"), dom)

    def test_dominio_excluye_por_profesor(self):
        # Algebra (Prof_A) choca con Calculo (Prof_A) en toda esa franja
        base = Estado({CLASES[0]: ("Lunes", "07-09", "S101")}, CLASES[1:])
        dom = self.p.dominio(base, CLASES[1])
        self.assertEqual(len(dom), 28)  # 30 - 2 salones
        self.assertNotIn(("Lunes", "07-09", "S101"), dom)
        self.assertNotIn(("Lunes", "07-09", "S102"), dom)

    def test_dominio_coincide_con_sucesores(self):
        # las acciones de sucesores deben salir exactamente del dominio
        e0 = self.p.estado_inicial()
        combos_de_sucesores = set(
            (accion.dia, accion.franja, accion.salon)
            for accion, e in self.p.sucesores(e0))
        self.assertEqual(combos_de_sucesores,
                         set(self.p.dominio(e0, CLASES[0])))

    # --- orden de seleccion de clases --------------------------------------

    def test_siguiente_clase_es_la_primera_pendiente(self):
        self.assertEqual(self.p.siguiente_clase(self.p.estado_inicial()),
                         CLASES[0])
        parcial = Estado({}, CLASES[2:])
        self.assertEqual(self.p.siguiente_clase(parcial), CLASES[2])

    def test_siguiente_clase_de_una_meta_es_none(self):
        self.assertIsNone(self.p.siguiente_clase(Estado({}, [])))

    def test_orden_seleccion_sigue_orden_de_entrada(self):
        # avanzando siempre por el primer sucesor, las clases se asignan
        # en el mismo orden en que se declararon
        actual = self.p.estado_inicial()
        orden_asignadas = []
        while actual.pendientes:
            accion, actual = self.p.sucesores(actual)[0]
            orden_asignadas.append(accion.clase)
        self.assertEqual(orden_asignadas, CLASES)

    def test_sucesores_solo_asignan_la_siguiente_clase(self):
        e0 = self.p.estado_inicial()
        for accion, e in self.p.sucesores(e0):
            self.assertEqual(accion.clase, CLASES[0])
            self.assertEqual(e.pendientes, tuple(CLASES[1:]))


if __name__ == "__main__":
    unittest.main()
