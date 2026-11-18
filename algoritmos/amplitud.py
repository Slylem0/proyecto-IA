# algoritmos/amplitud.py
# Busqueda en amplitud (BFS), implementada desde cero.
# Solo se usa la biblioteca estandar de Python (time para medir el tiempo);
# la cola es propia, no se usan collections ni nada externo.

import time

from modelo.resultado import Resultado


class Cola:
    """Cola FIFO propia, construida sobre una lista.

    En lugar de hacer pop(0), que desplaza todos los elementos y es lento,
    se guarda un indice de lectura que avanza; asi desencolar cuesta
    lo mismo que leer una casilla.
    """

    def __init__(self):
        self.elementos = []
        self.lectura = 0

    def encolar(self, x):
        """Agrega un elemento al final de la cola."""
        self.elementos.append(x)

    def desencolar(self):
        """Saca y devuelve el elemento mas antiguo, o None si esta vacia."""
        if self.lectura >= len(self.elementos):
            return None
        x = self.elementos[self.lectura]
        self.lectura += 1
        # cuando ya se leyeron todos, se limpia la lista de una vez
        if self.lectura >= len(self.elementos):
            self.elementos = []
            self.lectura = 0
        return x

    def vacia(self):
        """True si no quedan elementos por leer."""
        return self.lectura >= len(self.elementos)


def bfs(problema):
    """Busqueda en amplitud (BFS).

    Recorre el espacio de estados por niveles: primero el estado inicial,
    luego todos sus sucesores, luego los sucesores de estos, y asi
    siguiendo, usando una cola FIFO (Cola).

    Detalles de la implementacion:
    - Se guarda un conjunto de visitados (Estado es hashable) para no
      encolar dos veces el mismo estado.
    - La meta se comprueba al generar cada sucesor: el primer meta que
      aparece en amplitud esta al minimo nivel posible.
    - nodos_explorados cuenta los estados que se sacaron de la cola y
      se expandieron (se generaron sus sucesores).

    Devuelve un Resultado con la solucion (o None), el numero de
    nodos explorados y el tiempo de la busqueda.
    """
    inicio = time.perf_counter()
    explorados = 0

    inicial = problema.estado_inicial()
    if problema.es_meta(inicial):
        return Resultado("BFS", inicial, explorados, time.perf_counter() - inicio)

    visitados = {inicial}
    cola = Cola()
    cola.encolar(inicial)

    while not cola.vacia():
        estado = cola.desencolar()
        explorados += 1
        for accion, sucesor in problema.sucesores(estado):
            if problema.es_meta(sucesor):
                return Resultado("BFS", sucesor, explorados,
                                 time.perf_counter() - inicio)
            if sucesor not in visitados:
                visitados.add(sucesor)
                cola.encolar(sucesor)

    # la cola se vacio sin encontrar la meta: el problema no tiene solucion
    return Resultado("BFS", None, explorados, time.perf_counter() - inicio)
