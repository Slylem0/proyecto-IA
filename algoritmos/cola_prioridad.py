"""Cola de prioridad propia (monticulo binario de minimos).

la usan costo uniforme y A*: siempre sale primero lo que tenga la
prioridad mas baja. esta hecha desde cero sobre una lista, igual que
la Cola de amplitud.py.
"""


class ColaPrioridad:
    """Monticulo binario de minimos con pares (prioridad, elemento).

    la lista se mira como un arbol: los hijos de la posicion i estan en
    2*i + 1 y 2*i + 2, y el padre de i en (i - 1) // 2. cada padre es
    menor o igual que sus hijos, entonces el minimo siempre esta en 0.
    """

    def __init__(self):
        self.datos = []
        # numera las inserciones para desempatar: con la misma prioridad
        # sale el que entro primero y nunca se comparan dos Estado
        self.contador = 0

    def vacia(self):
        """True si no quedan elementos."""
        return len(self.datos) == 0

    def menor(self, i, j):
        """True si lo de la casilla i debe salir antes que lo de j."""
        return self.datos[i][:2] < self.datos[j][:2]

    def intercambiar(self, i, j):
        """Cambia de lugar dos casillas."""
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]

    def insertar(self, prioridad, elemento):
        """Mete el elemento al final y lo sube hasta su lugar."""
        self.datos.append((prioridad, self.contador, elemento))
        self.contador += 1
        i = len(self.datos) - 1
        while i > 0:
            padre = (i - 1) // 2
            if not self.menor(i, padre):
                break
            self.intercambiar(i, padre)
            i = padre

    def extraer(self):
        """Saca y devuelve (prioridad, elemento) con la menor prioridad."""
        # el minimo esta en 0, se pasa al final para sacarlo con pop()
        self.intercambiar(0, len(self.datos) - 1)
        prioridad, orden, elemento = self.datos.pop()
        # lo que quedo en 0 baja hasta su lugar
        i = 0
        n = len(self.datos)
        while True:
            hijo = 2 * i + 1
            if hijo >= n:
                break
            if hijo + 1 < n and self.menor(hijo + 1, hijo):
                hijo += 1
            if not self.menor(hijo, i):
                break
            self.intercambiar(i, hijo)
            i = hijo
        return prioridad, elemento
