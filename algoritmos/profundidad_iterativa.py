# algoritmos/profundidad_iterativa.py
# Busqueda en profundidad iterativa (IDDFS), implementada desde cero.
# Solo se usa la biblioteca estandar de Python (time para medir el tiempo).
#
# NOTA DE NOMBRE: en la interfaz grafica y en la tabla de estadisticas
# este algoritmo se mostrara como "IDDFS". El enunciado del proyecto lo
# llama "profundidad interactiva" y el boceto de la interfaz muestra
# "DFS"; el nombre correcto para confirmar con el profesor.

import time

from modelo.resultado import Resultado


def profundidad_iterativa(problema, limite_max=None):
    """Busqueda en profundidad iterativa (IDDFS).

    Repite una busqueda en profundidad limitada con limite creciente
    (0, 1, 2, ...): en la iteracion con limite L solo se pueden hacer L
    asignaciones a partir del estado inicial. Se detiene en la primera
    iteracion que encuentre la meta, o cuando se agota el limite maximo.

    Detalles de la implementacion:
    - La DFS limitada es recursiva y se escribe aqui mismo (desde cero).
    - nodos_explorados se ACUMULA entre iteraciones: la suma de todos
      los estados que se expandieron en todas las iteraciones. Es el
      precio de IDDFS: re-explora los niveles poco profundos en cada
      iteracion, a cambio de usar poca memoria (solo la rama actual).
    - Como cada paso asigna exactamente una clase, una solucion (si
      existe) esta a lo sumo a la profundidad del numero de clases;
      por eso, si no se da limite_max, se usa ese valor como maximo.
    - No hace falta conjunto de visitados: con el orden de asignacion
      fijado (pendientes[0]), cada estado se alcanza por un unico
      camino y no puede haber ciclos.

    Devuelve un Resultado con la solucion (o None), el numero de nodos
    explorados acumulado y el tiempo total de la busqueda.
    """
    inicio = time.perf_counter()
    explorados = 0

    def dfs(estado, limite):
        """DFS con limite de profundidad: permite hacer como mucho
        `limite` asignaciones mas desde este estado. Devuelve el estado
        meta o None. `explorados` es compartido con la funcion externa
        (nonlocal) para acumular entre iteraciones."""
        nonlocal explorados
        explorados += 1
        if problema.es_meta(estado):
            return estado
        if limite == 0:
            return None
        for accion, sucesor in problema.sucesores(estado):
            encontrado = dfs(sucesor, limite - 1)
            if encontrado is not None:
                return encontrado
        return None

    if limite_max is None:
        limite_max = len(problema.clases)

    for limite in range(limite_max + 1):
        encontrado = dfs(problema.estado_inicial(), limite)
        if encontrado is not None:
            return Resultado("IDDFS", encontrado, explorados,
                             time.perf_counter() - inicio)

    # se agotaron todas las profundidades sin encontrar la meta
    return Resultado("IDDFS", None, explorados, time.perf_counter() - inicio)
