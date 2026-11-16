
import unittest

from modelo.estado import Accion, Estado
from modelo.problema import Problema, ProblemaHorario

CLASES = [
    ("Calculo", "Prof_A", "G1"),
    ("Algebra", "Prof_A", "G2"),
    ("Fisica", "Prof_B", "G1"),
    ("Programacion", "Prof_C", "G2"),
]
SALONES = ["S101", "S102"]
DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
FRANJAS = ["07-09", "09-11", "11-13"]


class TestContrato(unittest.TestCase):

    def setUp(self):
        self.p = ProblemaHorario(CLASES, SALONES, DIAS, FRANJAS)

    # --- estado inicial -------------------------------------------------

    def test_estado_inicial(self):
        e0 = self.p.estado_inicial()
        self.assertEqual(e0.asignaciones, {})
        self.assertEqual(e0.pendientes, tuple(CLASES))

    def test_estado_inicial_no_es_meta(self):
        self.assertFalse(self.p.es_meta(self.p.estado_inicial()))

    # --- Estado inmutable y hashable ------------------------------------

    def test_estado_es_hashable(self):
        e1 = self.p.estado_inicial()
        e2 = self.p.estado_inicial()
        # dos estados iguales deben caer en la misma casilla de un set
        self.assertEqual(len({e1, e2}), 1)
        self.assertEqual(hash(e1), hash(e2))
        # y uno distinto no debe colisionar con ellos como "igual"
        asignadas = {CLASES[0]: ("Lunes", "07-09", "S101")}
        e3 = Estado(asignadas, CLASES[1:])
        self.assertEqual(len({e1, e2, e3}), 2)
        self.assertNotEqual(e1, e3)

    def test_estado_original_no_se_modifica(self):
        e0 = self.p.estado_inicial()
        sucs = self.p.sucesores(e0)
        sucs[0][1].asignaciones[CLASES[0]] = ("Lunes", "07-09", "S101")
        # e0 debe seguir igual aunque se cambie el sucesor
        self.assertEqual(e0.asignaciones, {})
        self.assertEqual(e0.pendientes, tuple(CLASES))

    # --- interfaz abstracta ---------------------------------------------

    def test_problema_abstracto(self):
        p = Problema()
        e = Estado()
        with self.assertRaises(NotImplementedError):
            p.estado_inicial()
        with self.assertRaises(NotImplementedError):
            p.sucesores(e)
        with self.assertRaises(NotImplementedError):
            p.es_meta(e)
        with self.assertRaises(NotImplementedError):
            p.costo(e, None)

    # --- sucesores ------------------------------------------------------

    def test_sucesores_del_inicial(self):
        sucs = self.p.sucesores(self.p.estado_inicial())
        # nada esta ocupado: 5 dias * 3 franjas * 2 salones = 30
        self.assertEqual(len(sucs), 30)

    def test_sucesores_asignan_la_primera_pendiente(self):
        e0 = self.p.estado_inicial()
        for accion, e in self.p.sucesores(e0):
            self.assertEqual(accion.clase, CLASES[0])
            self.assertEqual(e.asignaciones[CLASES[0]],
                             (accion.dia, accion.franja, accion.salon))
            self.assertEqual(e.pendientes, tuple(CLASES[1:]))

    def test_sucesores_son_validos(self):
        e0 = self.p.estado_inicial()
        for accion, e in self.p.sucesores(e0):
            self.assertTrue(self.p.restricciones_cumplidas(e))

    def test_bloqueo_por_profesor(self):
        # Calculo (Prof_A, G1) queda en Lunes 07-09 S101;
        # Algebra (Prof_A) no puede ir esa franja en ningun salon
        asignadas = {CLASES[0]: ("Lunes", "07-09", "S101")}
        e1 = Estado(asignadas, CLASES[1:])
        sucs = self.p.sucesores(e1)
        self.assertEqual(len(sucs), 28)  # 30 - 2 salones bloqueados
        for accion, e in sucs:
            self.assertFalse(accion.dia == "Lunes" and accion.franja == "07-09")

    # --- camino hasta la meta -------------------------------------------

    def test_camino_hasta_meta(self):
        actual = self.p.estado_inicial()
        pasos = 0
        while actual.pendientes:
            accion, actual = self.p.sucesores(actual)[0]
            pasos += 1
            self.assertTrue(self.p.restricciones_cumplidas(actual))
        self.assertEqual(pasos, len(CLASES))
        self.assertTrue(self.p.es_meta(actual))
        self.assertEqual(len(actual.asignaciones), len(CLASES))

    def test_meta_sin_sucesores(self):
        meta = Estado({c: ("Lunes", "07-09", "S101") for c in CLASES}, [])
        self.assertTrue(self.p.es_meta(meta))
        self.assertEqual(self.p.sucesores(meta), [])

    def test_costo_por_accion(self):
        e0 = self.p.estado_inicial()
        accion = self.p.sucesores(e0)[0][0]
        self.assertEqual(self.p.costo(e0, accion), 1)
        accion2 = Accion(CLASES[1], "Martes", "09-11", "S102")
        self.assertEqual(self.p.costo(e0, accion2), 1)

    # --- deteccion de conflictos -----------------------------------------

    def test_deteccion_de_conflictos(self):
        base = Estado({CLASES[0]: ("Lunes", "07-09", "S101")}, CLASES[1:])
        # mismo salon, misma franja -> conflicto
        self.assertFalse(self.p.es_valida(
            base, Accion(CLASES[1], "Lunes", "07-09", "S101")))
        # mismo profesor, misma franja, otro salon -> conflicto
        self.assertFalse(self.p.es_valida(
            base, Accion(CLASES[1], "Lunes", "07-09", "S102")))
        # mismo grupo, misma franja, otro salon -> conflicto
        self.assertFalse(self.p.es_valida(
            base, Accion(CLASES[2], "Lunes", "07-09", "S102")))
        # distinta franja o distinto dia -> sin conflicto
        self.assertTrue(self.p.es_valida(
            base, Accion(CLASES[1], "Lunes", "09-11", "S101")))
        self.assertTrue(self.p.es_valida(
            base, Accion(CLASES[1], "Martes", "07-09", "S101")))
        # restricciones_cumplidas tambien detecta el conflicto
        malo = Estado({
            CLASES[0]: ("Lunes", "07-09", "S101"),
            CLASES[1]: ("Lunes", "07-09", "S102"),
        })
        self.assertFalse(self.p.restricciones_cumplidas(malo))


if __name__ == "__main__":
    unittest.main()
