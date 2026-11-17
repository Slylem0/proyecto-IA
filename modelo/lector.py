# lectura y la validacion de lso archivos
# cada funcion lee un archivo  .txt y dependiendo si esta bien
# lanza una exepcion sobre que archivo esta mal y en que linea


import os


class ErrorDeFormato(Exception):
    # class la cual le dice a la interface en que parte
    # que archivo y que linea del txt esta el error

    def __init__(self, ruta, num_linea, mensaje):
        self.ruta = ruta
        self.num_linea = num_linea
        nombre = os.path.basename(ruta)
        if num_linea is None:
            texto = "%s: %s" % (nombre, mensaje)
        else:
            texto = "%s, linea %d: %s" % (nombre, num_linea, mensaje)

        super().__init__(texto)


def leer_lineas_utiles(ruta):
    # devuelve las lineas utiles de un archivo eliminando espacios en blanco
    # empeiza en 1 como un editor
    utiles = []
    with open(ruta, "r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if linea == "" or linea.startswith("#"):
                continue
            utiles.append((num_linea, linea))
    if not utiles:
        raise ErrorDeFormato(ruta, None, "El archivo esta vacio ")
    return utiles


def partir(ruta, num_linea, linea, n_campos):
    # separa una linea por :
    # y revisa que tenga los n campos no vacios
    campos = [c.strip() for c in linea.split(";")]
    if len(campos) != n_campos:
        raise ErrorDeFormato(
            ruta,
            num_linea,
            "se esperaban %d campos y hay %d " % (n_campos, len(campos)),
        )
    if "" in campos:
        raise ErrorDeFormato(ruta, num_linea, "hay un campo vacio ")

    return campos


def leer_nombres(ruta):
    # lee los nombres del archivo profesores.txt o salones.txt
    # los nombres pro linea y sin repetir
    nombres = []
    for num_linea, linea in leer_lineas_utiles(ruta):
        nombre = partir(ruta, num_linea, linea, 1)[0]
        if nombre in nombres:
            raise ErrorDeFormato(ruta, num_linea, "el nombre %s esta repetido" % nombre)
        nombres.append(nombre)
    return nombres


def leer_cursos(ruta):
    # leer los cursos del archivo cursos.txt
    # devuelve los parametreos de materia, profesor y grupo

    materias = []
    for num_linea, linea in leer_lineas_utiles(ruta):
        clase = tuple(partir(ruta, num_linea, linea, 3))
        if clase in materias:
            raise ErrorDeFormato(
                ruta, num_linea, "la clase %s esta repetida" % clase[0]
            )
        materias.append(clase)
    return materias
