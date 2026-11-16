import unittest
from modelo.estado import Estado
from modelo.resultado import Resultado


class TestResultado(unittest.TestCase):
    def test_sin_solucion_encontrada(self):
        r = Resultado("BFS", None, 10, 0.5)
        self.assertFalse(r.encontrada)

    def test_con_solucion_encontrada(self):
        clase = ("calculo", "Prof_1", "G1")
        meta = Estado({clase: ("Lunes", "07:00-09:00", "S101")}, [])
        r = Resultado("A*", meta, 5, 0.01)
        self.assertTrue(r.encontrada)

    def test_no_permite_atributos_nuevos(self):
        r = Resultado("BFS", None, 5, 0.01)
        with self.assertRaises(AttributeError):
            r.otra_cosa = "Debe de dar error"
