# algoritmos/__init__.py
# Paquete de algoritmos de busqueda del proyecto.
# Cada algoritmo recibe un Problema (la interfaz de modelo) y devuelve
# un Resultado con la solucion (o None), los nodos explorados y el tiempo.
# Los algoritmos no conocen los detalles del horario: solo usan la
# interfaz de Problema, tal como dice el contrato entre modulos.

from algoritmos.amplitud import bfs
from algoritmos.profundidad_iterativa import profundidad_iterativa
from algoritmos.costo_uniforme import costo_uniforme
from algoritmos.a_estrella import a_estrella
