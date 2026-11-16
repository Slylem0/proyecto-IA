class Resultado:
    """Lo que devuelve cualquier algoritmo de busqueda.

    algoritmo: guarda el nombre del algoritmo que se ejecuto
    solucion: el estado meta encontrado, o None si no encontro nada
    nodos_explorados: cuantos nodos se sacaron de la frontera para explorarlos
    tiempo: segundos que tardo la busqueda
    """

    __slots__ = ("algoritmo", "solucion", "nodos_explorados", "tiempo")

    def __init__(self, algoritmo, solucion, nodos_explorados, tiempo):
        self.algoritmo = algoritmo
        self.solucion = solucion
        self.nodos_explorados = nodos_explorados
        self.tiempo = tiempo

    @property
    def encontrada(self):
        # true si el algoritmo encuentra un horario completo
        return self.solucion is not None

    def __repr__(self):
        return "Resultado(%s, nodo: %d, tiempo: %.4fs, encontrada=%s)" % (
            self.algoritmo,
            self.nodos_explorados,
            self.tiempo,
            self.encontrada,
        )
