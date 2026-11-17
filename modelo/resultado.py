# modelo/resultado.py
# Resultado de un algoritmo de busqueda.
# Todos los algoritmos del paquete algoritmos devuelven un Resultado,
# de modo que la interfaz puede mostrar una tabla de estadisticas
# comparando nodos explorados, tiempo y si hubo solucion.


class Resultado:
    """Resultado de la ejecucion de un algoritmo de busqueda.

    - solucion: estado meta encontrado, o None si no hay solucion
    - nodos_explorados: cantidad de estados que el algoritmo expandio
    - tiempo: segundos que tardo la busqueda
    """

    __slots__ = ("solucion", "nodos_explorados", "tiempo")

    def __init__(self, solucion, nodos_explorados, tiempo):
        self.solucion = solucion
        self.nodos_explorados = nodos_explorados
        self.tiempo = tiempo

    def hay_solucion(self):
        """True si el algoritmo encontro un horario completo."""
        return self.solucion is not None

    def __repr__(self):
        if self.solucion is None:
            texto = "sin solucion"
        else:
            texto = "%d clases asignadas" % len(self.solucion.asignaciones)
        return "Resultado(%s, nodos=%d, tiempo=%.4f s)" % (
            texto, self.nodos_explorados, self.tiempo)
