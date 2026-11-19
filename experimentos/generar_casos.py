"""Genera los casos de prueba de tamano creciente (issue #20).

cada caso es una carpeta datos/casos/<nombre>/ con los cuatro .txt
de siempre (profesores, cursos, salones, franjas), con el mismo
formato que datos/. asi se pueden cargar tambien desde la GUI.

uso:  python -m experimentos.generar_casos
"""

import os

CARPETA = os.path.join(os.path.dirname(__file__), "..", "datos", "casos")

MATERIAS = [
    "Calculo I", "Algebra Lineal", "Fisica I", "Programacion I",
    "Quimica", "Estadistica", "Ecuaciones Diferenciales", "Fisica II",
    "Estructuras de Datos", "Bases de Datos", "Redes", "Sistemas Operativos",
    "Ingles I", "Etica", "Matematicas Discretas", "Calculo II",
    "Probabilidad", "Arquitectura de Computadores", "Ingenieria de Software",
    "Inteligencia Artificial", "Compiladores", "Analisis de Algoritmos",
    "Fundamentos de Lenguajes", "Teoria de la Computacion",
    "Computacion Grafica", "Desarrollo Web", "Seguridad Informatica",
    "Sistemas Distribuidos", "Investigacion de Operaciones",
    "Electronica Digital",
]
DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
FRANJAS = ["07:00-09:00", "09:00-11:00", "11:00-13:00",
           "14:00-16:00", "16:00-18:00", "18:00-20:00"]

# (nombre, clases, dias, franjas, salones, profesores, grupos)
# del caso1 al caso7 crece el tamano. el caso8 es pequeno pero
# "apretado": cada grupo tiene mas clases que dias, asi que si o si
# hay clases del mismo grupo el mismo dia.
CASOS = [
    ("caso1", 4, 2, 2, 2, 2, 2),
    ("caso2", 5, 2, 2, 2, 3, 2),
    ("caso3", 6, 2, 2, 2, 3, 2),
    ("caso4", 7, 3, 2, 2, 4, 3),
    ("caso5", 8, 3, 3, 2, 4, 3),
    ("caso6", 15, 5, 3, 3, 8, 5),
    ("caso7", 30, 5, 4, 5, 10, 6),
    ("caso8", 8, 3, 3, 2, 4, 2),
]


def nombre_profesor(i):
    """Prof_A, Prof_B, ... (hay a lo sumo 26)."""
    return "Prof_" + chr(ord("A") + i)


def escribir(ruta, encabezado, lineas):
    """Escribe un .txt con un comentario arriba y una linea por dato."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# %s\n" % encabezado)
        for linea in lineas:
            f.write(linea + "\n")


def generar(nombre, n_clases, n_dias, n_franjas, n_salones, n_profes, n_grupos):
    """Crea la carpeta de un caso con sus cuatro archivos.

    la clase i la dicta el profesor i % n_profes y la ve el grupo
    i % n_grupos, asi las clases quedan repartidas parejo.
    """
    carpeta = os.path.join(CARPETA, nombre)
    os.makedirs(carpeta, exist_ok=True)

    profesores = [nombre_profesor(i) for i in range(n_profes)]
    cursos = []
    for i in range(n_clases):
        profesor = profesores[i % n_profes]
        grupo = "G%d" % (i % n_grupos + 1)
        cursos.append("%s;%s;%s" % (MATERIAS[i], profesor, grupo))
    salones = ["S%d" % (101 + i) for i in range(n_salones)]
    franjas = ["dias;" + ";".join(DIAS[:n_dias])] + FRANJAS[:n_franjas]

    escribir(os.path.join(carpeta, "profesores.txt"), "profesores.txt", profesores)
    escribir(os.path.join(carpeta, "cursos.txt"),
             "cursos.txt (%d clases)" % n_clases, cursos)
    escribir(os.path.join(carpeta, "salones.txt"), "salones.txt", salones)
    escribir(os.path.join(carpeta, "franjas.txt"), "franjas.txt", franjas)


def main():
    for caso in CASOS:
        generar(*caso)
        print("generado", caso[0])


if __name__ == "__main__":
    main()
