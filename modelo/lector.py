"""Lectura y validacion de los archivos de datos.

Cada funcion lee un archivo .txt y, si algo esta mal, lanza un
ErrorDeFormato que dice que archivo y que linea tienen el problema.
"""

import os

from modelo.problema import ProblemaHorario


class ErrorDeFormato(Exception):
    """Error en un archivo de datos.

    Le dice a la interfaz en que archivo y en que linea del .txt esta
    el error. num_linea es None cuando el error es del archivo completo.
    """

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
    """Devuelve las lineas utiles de un archivo como (num_linea, texto).

    Quita espacios, salta lineas vacias y comentarios (#). Los numeros
    de linea empiezan en 1, como en un editor.
    """
    utiles = []
    with open(ruta, "r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if linea == "" or linea.startswith("#"):
                continue
            utiles.append((num_linea, linea))
    if not utiles:
        raise ErrorDeFormato(ruta, None, "el archivo esta vacio")
    return utiles


def partir(ruta, num_linea, linea, n_campos):
    """Separa una linea por ';' y revisa que tenga n_campos no vacios."""
    campos = [c.strip() for c in linea.split(";")]
    if len(campos) != n_campos:
        raise ErrorDeFormato(
            ruta,
            num_linea,
            "se esperaban %d campos y hay %d" % (n_campos, len(campos)),
        )
    if "" in campos:
        raise ErrorDeFormato(ruta, num_linea, "hay un campo vacio")

    return campos


def leer_nombres(ruta):
    """Lee profesores.txt o salones.txt: un nombre por linea, sin repetir."""
    nombres = []
    for num_linea, linea in leer_lineas_utiles(ruta):
        nombre = partir(ruta, num_linea, linea, 1)[0]
        if nombre in nombres:
            raise ErrorDeFormato(ruta, num_linea, "el nombre %s esta repetido" % nombre)
        nombres.append(nombre)
    return nombres


def leer_cursos(ruta):
    """Lee cursos.txt y devuelve una lista de tuplas (materia, profesor, grupo).

    Aqui no se revisa que el profesor exista, porque esta funcion solo
    conoce cursos.txt; eso lo hace construir_problema, que tiene los
    cuatro archivos.
    """
    materias = []
    for num_linea, linea in leer_lineas_utiles(ruta):
        clase = tuple(partir(ruta, num_linea, linea, 3))
        if clase in materias:
            raise ErrorDeFormato(
                ruta, num_linea, "la clase %s esta repetida" % clase[0]
            )
        materias.append(clase)
    return materias


def aux_minutos(hora):
    """Convierte 'hh:mm' a minutos totales desde las 00:00.

    Lanza ValueError si no tiene ese formato o no es una hora valida.
    """
    if len(hora) != 5 or hora[2] != ":":
        raise ValueError(hora)
    hh, mm = hora[:2], hora[3:]
    if not (hh.isdigit() and mm.isdigit()):
        raise ValueError(hora)
    h, m = int(hh), int(mm)
    if h > 23 or m > 59:
        raise ValueError(hora)

    return h * 60 + m


def leer_franjas(ruta):
    """Lee franjas.txt y devuelve (dias, franjas).

    La primera linea util es 'dias;Lunes;Martes;...'. Las demas son
    franjas 'hh:mm-hh:mm' en orden ascendente y sin cruzarse.
    """
    lineas = leer_lineas_utiles(ruta)
    num_linea, primera = lineas[0]
    campos = [c.strip() for c in primera.split(";")]
    if campos[0] != "dias":
        raise ErrorDeFormato(
            ruta, num_linea, "la primera linea debe ser dias;dia1;dia2;..."
        )
    dias = campos[1:]
    if not dias or "" in dias:
        raise ErrorDeFormato(ruta, num_linea, "falta un dia o hay uno vacio")
    if len(dias) != len(set(dias)):
        raise ErrorDeFormato(ruta, num_linea, "hay dias repetidos")

    franjas = []
    fin_anterior = -1

    for num_linea, linea in lineas[1:]:
        partes = linea.split("-")
        try:
            if len(partes) != 2:
                raise ValueError(linea)
            inicio, fin = aux_minutos(partes[0]), aux_minutos(partes[1])

        except ValueError:
            raise ErrorDeFormato(
                ruta, num_linea, "%s no tiene formato hh:mm-hh:mm" % linea
            )
        if fin <= inicio:
            raise ErrorDeFormato(
                ruta, num_linea, "la hora de fin debe ser mayor que la de inicio"
            )
        if inicio < fin_anterior:
            raise ErrorDeFormato(
                ruta, num_linea, "las franjas deben estar en orden y sin cruzarse"
            )

        fin_anterior = fin
        franjas.append(linea)

    if not franjas:
        raise ErrorDeFormato(ruta, None, "no hay franjas despues de los dias")
    return dias, franjas


def construir_problema(ruta_profesores, ruta_cursos, ruta_salones, ruta_franjas):
    """Lee los cuatro archivos y devuelve un ProblemaHorario listo para buscar.

    Ademas revisa que cada profesor de cursos.txt este en profesores.txt.
    """
    profesores = leer_nombres(ruta_profesores)
    clases = leer_cursos(ruta_cursos)
    salones = leer_nombres(ruta_salones)
    dias, franjas = leer_franjas(ruta_franjas)

    for materia, profesor, grupo in clases:
        if profesor not in profesores:
            raise ErrorDeFormato(
                ruta_cursos,
                None,
                "el profesor %s de %s no esta en profesores.txt" % (profesor, materia),
            )
    return ProblemaHorario(clases, salones, dias, franjas)
