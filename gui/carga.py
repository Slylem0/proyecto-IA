import os

from modelo import lector

ARCHIVOS = ["profesores.txt", "cursos.txt", "salones.txt", "franjas.txt"]

# funcion del lector que valida cada archivo
VALIDADORES = {
    "profesores.txt": lector.leer_nombres,
    "cursos.txt": lector.leer_cursos,
    "salones.txt": lector.leer_nombres,
    "franjas.txt": lector.leer_franjas,
}


def leer_archivo(nombre, ruta):
    """Devuelve (ok, mensaje) al validar un archivo con el lector."""
    if not ruta or not os.path.isfile(ruta):
        return False, "el archivo no existe"
    try:
        VALIDADORES[nombre](ruta)
    except lector.ErrorDeFormato as error:
        return False, str(error)
    except (OSError, UnicodeDecodeError):
        return False, "no se pudo leer como UTF-8"
    return True, "leido correctamente"


def construir_problema(rutas):
    """Arma el ProblemaHorario con los cuatro archivos ya cargados."""
    faltan = [nombre for nombre in ARCHIVOS if not rutas.get(nombre)]
    if faltan:
        raise ValueError("Falta cargar " + ", ".join(faltan))
    return lector.construir_problema(
        rutas["profesores.txt"], rutas["cursos.txt"],
        rutas["salones.txt"], rutas["franjas.txt"])
