"""Busqueda de costo uniforme (UCS), hecha desde cero (issue #11).

expande siempre el nodo con menor costo acumulado g. usa la cola de
prioridad propia de algoritmos/cola_prioridad.py.
"""

import time

from algoritmos.cola_prioridad import ColaPrioridad
from modelo.resultado import Resultado


def costo_uniforme(problema):
    """Busqueda de costo uniforme.

    - la frontera es una ColaPrioridad ordenada por g (costo acumulado)
    - la meta se revisa al SACAR el nodo, no al generarlo: asi la
      primera meta que sale es la de menor costo
    - mejor_g guarda el menor g conocido de cada estado; si un estado
      sale con un g peor (una entrada vieja) se ignora
    - nodos_explorados cuenta los estados que se sacan y se expanden,
      igual que en amplitud

    Devuelve un Resultado con la solucion de menor costo, o None.
    """
    inicio = time.perf_counter()
    explorados = 0

    inicial = problema.estado_inicial()
    frontera = ColaPrioridad()
    frontera.insertar(0, inicial)
    mejor_g = {inicial: 0}

    while not frontera.vacia():
        g, estado = frontera.extraer()
        if g > mejor_g[estado]:
            continue  # entrada vieja, ya hay un camino mas barato
        if problema.es_meta(estado):
            return Resultado(
                "Costo uniforme", estado, explorados, time.perf_counter() - inicio
            )
        explorados += 1
        for accion, sucesor in problema.sucesores(estado):
            nuevo_g = g + problema.costo(estado, accion)
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                mejor_g[sucesor] = nuevo_g
                frontera.insertar(nuevo_g, sucesor)

    # se vacio la frontera sin llegar a la meta: no hay horario posible
    return Resultado("Costo uniforme", None, explorados, time.perf_counter() - inicio)
