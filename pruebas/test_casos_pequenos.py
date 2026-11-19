import os
import unittest
from itertools import product

from algoritmos import a_estrella, bfs, costo_uniforme, profundidad_iterativa
from modelo.estado import Estado
from modelo.lector import construir_problema

CASOS = os.path.join(os.path.dirname(__file__), "..", "datos", "casos_pequenos")

# nombre, clases, dias, franjas, salones, soluciones (contadas a mano)
ESPERADOS = [
    ("caso1_trivial", 1, 1, 1, 1, 1),
    ("caso2_dos_franjas", 2, 1, 2, 1, 2),
    ("caso3_dos_dias", 2, 2, 1, 1, 2),
    ("caso4_mismo_grupo", 2, 1, 2, 2, 8),
    ("caso5_tablero_lleno", 4, 2, 2, 1, 24),
    ("caso6_al_limite", 3, 1, 3, 1, 6),
    ("caso7_sin_solucion_profesor", 3, 1, 2, 3, 0),
    ("caso8_sin_solucion_salon", 3, 1, 2, 1, 0),
    ("caso9_sin_solucion_grupo", 3, 1, 2, 3, 0),
]

ALGORITMOS = [bfs, costo_uniforme, profundidad_iterativa, a_estrella]


def cargar(nombre):
    """Arma el problema de un caso con el lector de verdad."""
    carpeta = os.path.join(CASOS, nombre)
    return construir_problema(
        os.path.join(carpeta, "profesores.txt"),
        os.path.join(carpeta, "cursos.txt"),
        os.path.join(carpeta, "salones.txt"),
        os.path.join(carpeta, "franjas.txt"))


def todas_las_soluciones(problema):
    """Cuenta las soluciones por fuerza bruta, sin usar los algoritmos.

    Prueba todas las formas de repartir las clases entre las casillas
    (dia, franja, salon) y se queda con las que cumplen las cuatro
    restricciones duras. En estos casos hay pocas combinaciones, asi que
    el resultado se puede comparar con el conteo hecho a mano.
    """
    casillas = [(dia, franja, salon) for dia in problema.dias
                for franja in problema.franjas for salon in problema.salones]
    soluciones = []
    for reparto in product(casillas, repeat=len(problema.clases)):
        estado = Estado(dict(zip(problema.clases, reparto)))
        if problema.es_solucion_valida(estado):
            soluciones.append(estado.asignaciones)
    return soluciones


class TestCasosPequenos(unittest.TestCase):

    def test_tamano_de_cada_caso(self):
        for nombre, n_clases, n_dias, n_franjas, n_salones, _ in ESPERADOS:
            problema = cargar(nombre)
            self.assertEqual(
                (len(problema.clases), len(problema.dias),
                 len(problema.franjas), len(problema.salones)),
                (n_clases, n_dias, n_franjas, n_salones), nombre)

    def test_soluciones_contadas_a_mano(self):
        for nombre, _, _, _, _, n_soluciones in ESPERADOS:
            problema = cargar(nombre)
            self.assertEqual(len(todas_las_soluciones(problema)),
                             n_soluciones, nombre)

    def test_todas_las_soluciones_son_validas(self):
        for nombre, _, _, _, _, n_soluciones in ESPERADOS:
            if n_soluciones == 0:
                continue
            problema = cargar(nombre)
            for asignaciones in todas_las_soluciones(problema):
                estado = Estado(asignaciones)
                self.assertTrue(problema.es_solucion_valida(estado), nombre)

    def test_los_algoritmos_coinciden_con_el_conteo(self):
        # los cuatro algoritmos tienen que decir "hay" o "no hay" segun
        # el caso, y cuando hay, la solucion debe ser valida
        for nombre, _, _, _, _, n_soluciones in ESPERADOS:
            problema = cargar(nombre)
            for algoritmo in ALGORITMOS:
                resultado = algoritmo(problema)
                self.assertEqual(resultado.encontrada, n_soluciones > 0,
                                 nombre + " con " + resultado.algoritmo)
                if resultado.encontrada:
                    self.assertTrue(problema.es_solucion_valida(
                        resultado.solucion), nombre + " con " + resultado.algoritmo)

    def test_solucion_unica_del_caso_trivial(self):
        # el caso1 tiene una sola solucion y se puede escribir a mano
        problema = cargar("caso1_trivial")
        soluciones = todas_las_soluciones(problema)
        self.assertEqual(len(soluciones), 1)
        self.assertEqual(
            soluciones[0],
            {("Calculo", "Prof_A", "G1"): ("Lunes", "07:00-09:00", "S1")})


if __name__ == "__main__":
    unittest.main()
