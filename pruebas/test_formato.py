# pruebas/test_formato.py
# Pruebas de los archivos de ejemplo de datos/ (issue 2).
# Comprueban que los ejemplos cumplan lo definido en docs/formato_datos.md.
# La lectura completa con validacion de errores se implementara despues.

import os
import re
import unittest

# carpeta donde estan los archivos de ejemplo
DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")

# formato de una franja horaria: hh:mm-hh:mm con dos digitos por campo
FRANJA_RE = re.compile(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$")


def leer_lineas(nombre):
    """Devuelve las lineas utiles de un archivo de datos:
    sin espacios sobrantes, sin lineas vacias y sin comentarios."""
    ruta = os.path.join(DATOS, nombre)
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()
    utiles = []
    for linea in lineas:
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue
        utiles.append(linea)
    return utiles


def leer_franjas():
    """Separa franjas.txt en (dias, franjas).
    La primera linea util es dias;Dia1;Dia2;... y el resto son franjas."""
    lineas = leer_lineas("franjas.txt")
    dias = lineas[0].split(";")[1:]
    return dias, lineas[1:]


def hay_repetidos(lista):
    return len(lista) != len(set(lista))


class TestFormatoDatos(unittest.TestCase):

    def test_los_cuatro_archivos_existen(self):
        for nombre in ["profesores.txt", "cursos.txt", "salones.txt",
                       "franjas.txt"]:
            self.assertTrue(os.path.isfile(os.path.join(DATOS, nombre)),
                            "falta " + nombre)

    # --- profesores ------------------------------------------------------

    def test_profesores_un_campo_por_linea(self):
        for linea in leer_lineas("profesores.txt"):
            self.assertNotIn(";", linea, "profesores no usa separador")
            self.assertNotEqual(linea, "", "no puede haber campos vacios")

    def test_profesores_sin_duplicados(self):
        lineas = leer_lineas("profesores.txt")
        self.assertFalse(hay_repetidos(lineas))

    # --- cursos ----------------------------------------------------------

    def test_cursos_tres_campos_no_vacios(self):
        for linea in leer_lineas("cursos.txt"):
            campos = [c.strip() for c in linea.split(";")]
            self.assertEqual(len(campos), 3, "formato: materia;profesor;grupo")
            for campo in campos:
                self.assertNotEqual(campo, "", "ningun campo puede ser vacio")

    def test_cursos_profesores_existen(self):
        profesores = set(leer_lineas("profesores.txt"))
        for linea in leer_lineas("cursos.txt"):
            profesor = linea.split(";")[1].strip()
            self.assertIn(profesor, profesores,
                          profesor + " no esta en profesores.txt")

    def test_cursos_sin_clases_repetidas(self):
        clases = leer_lineas("cursos.txt")
        self.assertFalse(hay_repetidos(clases))

    # --- salones ---------------------------------------------------------

    def test_salones_sin_duplicados(self):
        lineas = leer_lineas("salones.txt")
        self.assertFalse(hay_repetidos(lineas))
        for linea in lineas:
            self.assertNotIn(";", linea, "salones no usa separador")

    # --- franjas ---------------------------------------------------------

    def test_franjas_primera_linea_son_dias(self):
        primera = leer_lineas("franjas.txt")[0]
        self.assertTrue(primera.startswith("dias;"),
                        "la primera linea debe ser dias;Dia1;Dia2;...")
        dias, _ = leer_franjas()
        self.assertGreater(len(dias), 0, "debe haber al menos un dia")
        for dia in dias:
            self.assertNotEqual(dia.strip(), "", "no puede haber dias vacios")
        self.assertFalse(hay_repetidos(dias), "no puede haber dias repetidos")

    def test_franjas_formato_horario(self):
        _, franjas = leer_franjas()
        for linea in franjas:
            m = FRANJA_RE.match(linea)
            self.assertIsNotNone(
                m, "franja invalida: " + linea + " (debe ser hh:mm-hh:mm)")
            h1, m1, h2, m2 = [int(g) for g in m.groups()]
            self.assertLess((h1, m1), (h2, m2),
                            "la hora de fin debe ser mayor: " + linea)

    def test_franjas_en_orden_ascendente(self):
        def en_minutos(linea):
            m = FRANJA_RE.match(linea)
            h1, m1, _, _ = [int(g) for g in m.groups()]
            return h1 * 60 + m1

        _, franjas = leer_franjas()
        inicios = [en_minutos(f) for f in franjas]
        self.assertEqual(inicios, sorted(inicios),
                         "las franjas deben ir en orden ascendente")
        self.assertFalse(hay_repetidos(franjas))


if __name__ == "__main__":
    unittest.main()
