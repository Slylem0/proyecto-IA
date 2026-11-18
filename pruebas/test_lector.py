"""Pruebas del lector de archivos (issue #7)."""

import os
import tempfile
import unittest

from modelo.lector import (
    ErrorDeFormato,
    construir_problema,
    leer_cursos,
    leer_franjas,
    leer_nombres,
)

DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")


class TestLector(unittest.TestCase):

    def crear_archivo(self, contenido):
        """Crea un .txt temporal con ese contenido y devuelve su ruta.
        Se borra solo al terminar la prueba."""
        f = tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        )
        f.write(contenido)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_ejemplos_de_datos_son_validos(self):
        rutas = [
            os.path.join(DATOS, n)
            for n in ["profesores.txt", "cursos.txt", "salones.txt", "franjas.txt"]
        ]
        problema = construir_problema(*rutas)
        self.assertEqual(problema.dias, ["Lunes", "Martes", "Miercoles"])
        self.assertEqual(len(problema.clases), 4)

    def test_nombre_repetido_dice_la_linea(self):
        ruta = self.crear_archivo("S101\n# comentario\nS101\n")
        with self.assertRaises(ErrorDeFormato) as ctx:
            leer_nombres(ruta)
        self.assertEqual(ctx.exception.num_linea, 3)

    def test_archivo_vacio(self):
        with self.assertRaises(ErrorDeFormato):
            leer_nombres(self.crear_archivo("# solo comentarios\n\n"))

    def test_curso_con_campo_vacio(self):
        with self.assertRaises(ErrorDeFormato):
            leer_cursos(self.crear_archivo("Calculo;;G1\n"))

    def test_franjas_validas(self):
        dias, franjas = leer_franjas(
            self.crear_archivo("dias;Lunes;Martes\n07:00-09:00\n09:00-11:00\n")
        )
        self.assertEqual(dias, ["Lunes", "Martes"])
        self.assertEqual(franjas, ["07:00-09:00", "09:00-11:00"])

    def test_franja_al_reves(self):
        with self.assertRaises(ErrorDeFormato):
            leer_franjas(self.crear_archivo("dias;Lunes\n09:00-07:00\n"))

    def test_franjas_que_se_cruzan(self):
        with self.assertRaises(ErrorDeFormato):
            leer_franjas(self.crear_archivo("dias;Lunes\n07:00-09:00\n08:00-10:00\n"))

    def test_hora_invalida(self):
        with self.assertRaises(ErrorDeFormato):
            leer_franjas(self.crear_archivo("dias;Lunes\n24:00-25:00\n"))

    def test_profesor_inexistente(self):
        with self.assertRaises(ErrorDeFormato):
            construir_problema(
                self.crear_archivo("Prof_A\n"),
                self.crear_archivo("Calculo;Prof_X;G1\n"),
                self.crear_archivo("S101\n"),
                self.crear_archivo("dias;Lunes\n07:00-09:00\n"),
            )


if __name__ == "__main__":
    unittest.main()
