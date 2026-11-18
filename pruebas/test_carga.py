import os
import tempfile
import unittest

from algoritmos.amplitud import bfs
from gui.carga import ARCHIVOS, construir_problema, leer_archivo
from modelo.lector import ErrorDeFormato
from modelo.problema import ProblemaHorario

DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")


def ruta_de(nombre):
    return os.path.join(DATOS, nombre)


def crear_temporal(texto):
    """Crea un .txt temporal con el contenido dado y devuelve su ruta."""
    archivo = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8")
    try:
        archivo.write(texto)
    finally:
        archivo.close()
    return archivo.name


class TestLeerArchivo(unittest.TestCase):

    def test_los_cuatro_archivos_validos(self):
        for nombre in ARCHIVOS:
            ok, mensaje = leer_archivo(nombre, ruta_de(nombre))
            self.assertTrue(ok, nombre + ": " + mensaje)
            self.assertEqual(mensaje, "leido correctamente")

    def test_archivo_inexistente(self):
        ok, mensaje = leer_archivo("profesores.txt",
                                   ruta_de("no_existe.txt"))
        self.assertFalse(ok)
        self.assertEqual(mensaje, "el archivo no existe")

    def test_ruta_vacia(self):
        ok, mensaje = leer_archivo("salones.txt", "")
        self.assertFalse(ok)
        self.assertEqual(mensaje, "el archivo no existe")

    def test_archivo_solo_con_comentarios(self):
        ruta = crear_temporal("# solo comentarios\n\n   \n")
        try:
            ok, mensaje = leer_archivo("profesores.txt", ruta)
            self.assertFalse(ok)
            self.assertIn("vacio", mensaje)
        finally:
            os.remove(ruta)

    def test_cursos_con_campos_de_mas(self):
        ruta = crear_temporal("Calculo;Prof_A;G1;extra\n")
        try:
            ok, mensaje = leer_archivo("cursos.txt", ruta)
            self.assertFalse(ok)
            self.assertIn("se esperaban 3 campos", mensaje)
        finally:
            os.remove(ruta)

    def test_franjas_sin_linea_de_dias(self):
        ruta = crear_temporal("07:00-09:00\n09:00-11:00\n")
        try:
            ok, mensaje = leer_archivo("franjas.txt", ruta)
            self.assertFalse(ok)
            self.assertIn("dias", mensaje)
        finally:
            os.remove(ruta)

    def test_profesor_repetido(self):
        ruta = crear_temporal("Prof_A\nProf_A\n")
        try:
            ok, mensaje = leer_archivo("profesores.txt", ruta)
            self.assertFalse(ok)
            self.assertIn("repetido", mensaje)
        finally:
            os.remove(ruta)


class TestConstruirProblema(unittest.TestCase):

    def rutas(self):
        return {nombre: ruta_de(nombre) for nombre in ARCHIVOS}

    def test_arma_el_problema(self):
        p = construir_problema(self.rutas())
        self.assertIsInstance(p, ProblemaHorario)
        self.assertEqual(len(p.clases), 4)
        self.assertEqual(len(p.salones), 2)
        self.assertEqual(len(p.franjas), 3)
        # los dias vienen declarados en la primera linea de franjas.txt
        self.assertEqual(p.dias, ["Lunes", "Martes", "Miercoles"])

    def test_el_problema_armado_se_resuelve(self):
        p = construir_problema(self.rutas())
        r = bfs(p)
        self.assertTrue(r.encontrada)
        self.assertTrue(p.es_solucion_valida(r.solucion))

    def test_falta_un_archivo(self):
        rutas = self.rutas()
        rutas["salones.txt"] = None
        with self.assertRaises(ValueError):
            construir_problema(rutas)

    def test_profesor_inexistente_en_cursos(self):
        ruta = crear_temporal("Calculo;Prof_Z;G1\n")
        try:
            rutas = self.rutas()
            rutas["cursos.txt"] = ruta
            with self.assertRaises(ErrorDeFormato):
                construir_problema(rutas)
        finally:
            os.remove(ruta)


if __name__ == "__main__":
    unittest.main()
