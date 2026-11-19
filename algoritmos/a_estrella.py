"""Busqueda A*, hecha desde cero (issue #13).

es costo uniforme pero ordenando la frontera por f = g + h: el costo
que ya se pago mas lo que la heuristica estima que falta. usa la misma
cola de prioridad propia de algoritmos/cola_prioridad.py.
"""

import time

from algoritmos.cola_prioridad import ColaPrioridad
from modelo.resultado import Resultado


def a_estrella(problema, heuristica=None):
    """Busqueda A*.

    - la frontera es una ColaPrioridad ordenada por f = g + h; si dos
      nodos tienen el mismo f, sale primero el de mayor g (el que esta
      mas cerca de la meta). eso no cambia el costo de la solucion, solo
      evita expandir muchos estados empatados
    - h sale de problema.heuristica (issue #12), salvo que se pase otra
      funcion en heuristica (sirve para comparar en el informe)
    - como la heuristica es consistente, la primera meta que sale de la
      frontera es la de menor costo, igual que en costo uniforme
    - mejor_g guarda el menor g conocido de cada estado; si un estado
      sale con un g peor (una entrada vieja) se ignora
    - nodos_explorados cuenta los estados que se sacan y se expanden

    Devuelve un Resultado con la solucion de menor costo, o None.
    """
    if heuristica is None:
        heuristica = problema.heuristica

    inicio = time.perf_counter()
    explorados = 0

    inicial = problema.estado_inicial()
    frontera = ColaPrioridad()
    # la prioridad es la tupla (f, -g): primero el menor f y, si empatan,
    # el mayor g
    frontera.insertar((heuristica(inicial), 0), (0, inicial))
    mejor_g = {inicial: 0}

    while not frontera.vacia():
        prioridad, (g, estado) = frontera.extraer()
        if g > mejor_g[estado]:
            continue  # entrada vieja, ya hay un camino mas barato
        if problema.es_meta(estado):
            return Resultado("A*", estado, explorados, time.perf_counter() - inicio)
        explorados += 1
        for accion, sucesor in problema.sucesores(estado):
            nuevo_g = g + problema.costo(estado, accion)
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                mejor_g[sucesor] = nuevo_g
                f = nuevo_g + heuristica(sucesor)
                frontera.insertar((f, -nuevo_g), (nuevo_g, sucesor))

    # se vacio la frontera sin llegar a la meta: no hay horario posible
    return Resultado("A*", None, explorados, time.perf_counter() - inicio)
