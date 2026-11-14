"""Pruebas del contrato de Estado, Accion y Problema (issue #1)."""

import dataclasses
import unittest

from modelo.estado import Accion, Estado
from modelo.problema import Problema

ASIG = (("c1", ("Lun", "07-09", "S101")),)


class PruebasAccion(unittest.TestCase):
    def test_campos_por_nombre_y_posicion(self):
        a = Accion("c1", "Lun", "07-09", "S101")
        self.assertEqual((a.clase, a.dia, a.franja, a.salon), tuple(a))
        self.assertEqual(a.salon, "S101")

    def test_igualdad(self):
        self.assertEqual(Accion("c1", "Lun", "07-09", "S101"), Accion("c1", "Lun", "07-09", "S101"))
        self.assertNotEqual(Accion("c1", "Lun", "07-09", "S101"), Accion("c1", "Mar", "07-09", "S101"))


class PruebasEstado(unittest.TestCase):
    def test_creacion_estado_inicial(self):
        e = Estado((), ("c1", "c2"))
        self.assertEqual(e.asignaciones, ())
        self.assertEqual(e.pendientes, ("c1", "c2"))

    def test_creacion_con_asignaciones(self):
        e = Estado(ASIG, ("c2",))
        self.assertEqual(e.asignaciones[0][0], "c1")
        self.assertEqual(e.asignaciones[0][1], ("Lun", "07-09", "S101"))

    def test_igualdad_y_hash(self):
        self.assertEqual(Estado(ASIG, ("c2",)), Estado(ASIG, ("c2",)))
        self.assertEqual(hash(Estado(ASIG, ("c2",))), hash(Estado(ASIG, ("c2",))))

    def test_desigualdad(self):
        self.assertNotEqual(Estado((), ("c1", "c2")), Estado(ASIG, ("c2",)))
        self.assertNotEqual(Estado(ASIG, ("c2",)), Estado(ASIG, ("c3",)))

    def test_usable_en_conjuntos_y_diccionarios(self):
        visitados = {Estado((), ("c1",)), Estado((), ("c1",)), Estado(ASIG, ())}
        self.assertEqual(len(visitados), 2)

    def test_inmutable(self):
        e = Estado((), ("c1",))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            e.pendientes = ()

    def test_sucesor_no_modifica_el_anterior(self):
        e = Estado((), ("c1", "c2"))
        hijo = Estado(e.asignaciones + (("c1", ("Lun", "07-09", "S101")),), e.pendientes[1:])
        self.assertEqual(e.pendientes, ("c1", "c2"))
        self.assertEqual(e.asignaciones, ())
        self.assertEqual(hijo.pendientes, ("c2",))


class PruebasProblema(unittest.TestCase):
    def test_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            Problema()

    def test_metodos_abstractos_del_contrato(self):
        self.assertEqual(
            Problema.__abstractmethods__,
            frozenset({"estado_inicial", "sucesores", "es_meta", "costo"}),
        )

    def test_subclase_incompleta_falla(self):
        class Incompleta(Problema):
            def estado_inicial(self):
                return Estado((), ())

        with self.assertRaises(TypeError):
            Incompleta()

    def test_subclase_completa_cumple_el_contrato(self):
        class Minimo(Problema):
            def estado_inicial(self):
                return Estado((), ("c1",))

            def sucesores(self, estado):
                if self.es_meta(estado):
                    return []
                a = Accion(estado.pendientes[0], "Lun", "07-09", "S101")
                return [(a, Estado(estado.asignaciones + ((a.clase, (a.dia, a.franja, a.salon)),),
                                   estado.pendientes[1:]))]

            def es_meta(self, estado):
                return not estado.pendientes

            def costo(self, estado, accion):
                return 1.0

        p = Minimo()
        e0 = p.estado_inicial()
        self.assertFalse(p.es_meta(e0))
        (accion, e1), = p.sucesores(e0)
        self.assertEqual(accion.clase, "c1")
        self.assertTrue(p.es_meta(e1))
        self.assertEqual(p.sucesores(e1), [])
        self.assertGreaterEqual(p.costo(e0, accion), 0)


if __name__ == "__main__":
    unittest.main()
