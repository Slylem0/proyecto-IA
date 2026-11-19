"""Pruebas de los casos grandes y del script de comparacion (issue #20)."""

import unittest

from algoritmos import a_estrella, costo_uniforme
from experimentos.comparar import cargar, medir
from experimentos.generar_casos import CASOS


class TestCasos(unittest.TestCase):

    def test_todos_los_casos_se_leen(self):
        # si un archivo estuviera mal, el lector lanzaria ErrorDeFormato
        for nombre, n_clases, n_dias, n_franjas, n_salones, _, _ in CASOS:
            problema = cargar(nombre)
            self.assertEqual(len(problema.clases), n_clases)
            self.assertEqual(len(problema.dias), n_dias)
            self.assertEqual(len(problema.franjas), n_franjas)
            self.assertEqual(len(problema.salones), n_salones)

    def test_a_estrella_igual_costo_que_costo_uniforme(self):
        # en los casos chicos se puede correr costo uniforme y comparar
        for nombre in ["caso1", "caso2", "caso3"]:
            problema = cargar(nombre)
            ucs = costo_uniforme(problema)
            a = a_estrella(problema)
            self.assertEqual(problema.costo_horario(a.solucion),
                             problema.costo_horario(ucs.solucion))
            self.assertLess(a.nodos_explorados, ucs.nodos_explorados)

    def test_a_estrella_resuelve_los_grandes(self):
        for nombre in ["caso6", "caso7"]:
            problema = cargar(nombre)
            resultado = a_estrella(problema)
            self.assertTrue(problema.es_solucion_valida(resultado.solucion))

    def test_medir_corta_si_pasa_el_limite(self):
        # BFS en el caso5 no termina en medio segundo
        self.assertIsNone(medir("caso5", "BFS", 0.5))

    def test_medir_devuelve_nodos_tiempo_y_costo(self):
        nodos, tiempo, costo = medir("caso1", "A*", 30)
        self.assertEqual((nodos, costo), (4, 4))


if __name__ == "__main__":
    unittest.main()
