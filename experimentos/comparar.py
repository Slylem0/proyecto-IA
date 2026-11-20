"""Comparacion de los algoritmos en los casos grandes (issue #20).

corre BFS, costo uniforme, IDDFS y A* sobre cada caso de datos/casos/,
ademas de A* con la heuristica simple (para ver cuanto ayuda la buena),
y arma una tabla con nodos explorados, tiempo y costo del horario.

cada corrida va en un proceso aparte (multiprocessing, de la libreria
estandar) para poder cortarla si pasa del limite de tiempo: los
algoritmos no tienen limite propio y en los casos grandes BFS o IDDFS
pueden tardar horas. si se corta, en la tabla sale "no termina".

uso:  python -m experimentos.comparar [limite_en_segundos]
la tabla se imprime y se guarda en experimentos/resultados.md
"""

import multiprocessing
import os
import sys

from algoritmos import a_estrella, bfs, costo_uniforme, profundidad_iterativa
from experimentos.generar_casos import CARPETA, CASOS
from modelo.lector import construir_problema


def a_estrella_simple(problema):
    """A* con la heuristica simple (clases pendientes), para comparar."""
    return a_estrella(problema, problema.heuristica_pendientes)


ALGORITMOS = {
    "BFS": bfs,
    "Costo uniforme": costo_uniforme,
    "IDDFS": profundidad_iterativa,
    "A*": a_estrella,
    "A* (h simple)": a_estrella_simple,
}
LIMITE = 60  # segundos por corrida
SALIDA = os.path.join(os.path.dirname(__file__), "resultados.md")


def cargar(nombre):
    """Lee los cuatro archivos de un caso con el lector de siempre."""
    carpeta = os.path.join(CARPETA, nombre)
    rutas = [os.path.join(carpeta, n) for n in
             ["profesores.txt", "cursos.txt", "salones.txt", "franjas.txt"]]
    return construir_problema(*rutas)


def correr(nombre_caso, nombre_algoritmo, cola):
    """Lo que hace el proceso hijo: carga el caso, corre y avisa.

    deja en la cola (nodos, tiempo, costo); costo es None si no hubo
    solucion.
    """
    problema = cargar(nombre_caso)
    resultado = ALGORITMOS[nombre_algoritmo](problema)
    costo = None
    if resultado.encontrada:
        costo = problema.costo_horario(resultado.solucion)
    cola.put((resultado.nodos_explorados, resultado.tiempo, costo))


def medir(nombre_caso, nombre_algoritmo, limite):
    """Corre un algoritmo en un caso con limite de tiempo.

    devuelve (nodos, tiempo, costo), o None si no termino a tiempo.
    """
    cola = multiprocessing.Queue()
    proceso = multiprocessing.Process(
        target=correr, args=(nombre_caso, nombre_algoritmo, cola)
    )
    proceso.start()
    proceso.join(limite)
    if proceso.is_alive():
        proceso.terminate()
        proceso.join()
        return None
    return cola.get()


def describir(nombre):
    """Texto corto del tamano de un caso: clases y combinaciones."""
    problema = cargar(nombre)
    combinaciones = len(problema.dias) * len(problema.franjas) * len(problema.salones)
    return "%d clases, %d dias x %d franjas x %d salones = %d" % (
        len(problema.clases), len(problema.dias), len(problema.franjas),
        len(problema.salones), combinaciones,
    )


def main():
    limite = LIMITE
    if len(sys.argv) > 1:
        limite = float(sys.argv[1])

    lineas = [
        "# Comparacion de algoritmos (issue #20)",
        "",
        "Limite por corrida: %d s. Celda: nodos explorados / tiempo (s) / costo."
        % limite,
        "",
        "| Caso | Tamano | " + " | ".join(ALGORITMOS) + " |",
        "|---|---|" + "---|" * len(ALGORITMOS),
    ]
    print("\n".join(lineas))

    for caso in CASOS:
        nombre = caso[0]
        celdas = []
        for algoritmo in ALGORITMOS:
            medida = medir(nombre, algoritmo, limite)
            if medida is None:
                celdas.append("no termina")
            else:
                nodos, tiempo, costo = medida
                if costo is None:
                    costo = "sin solucion"
                celdas.append("%d / %.3f / %s" % (nodos, tiempo, costo))
        fila = "| %s | %s | %s |" % (nombre, describir(nombre), " | ".join(celdas))
        print(fila, flush=True)
        lineas.append(fila)

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print("\nguardado en", SALIDA)


if __name__ == "__main__":
    main()
