# pruebas/test_estructura.py
# Pruebas de la estructura del proyecto (issue 3).
# Comprueban las carpetas, el README y el .gitignore.

import os
import unittest

RAIZ = os.path.join(os.path.dirname(__file__), "..")


def ruta(*partes):
    return os.path.join(RAIZ, *partes)


class TestEstructura(unittest.TestCase):

    def test_carpetas_del_proyecto(self):
        # las carpetas definidas en la issue deben existir
        for carpeta in ["modelo", "algoritmos", "gui", "datos",
                        "pruebas", "docs"]:
            self.assertTrue(os.path.isdir(ruta(carpeta)),
                            "falta la carpeta " + carpeta)

    def test_paquetes_tienen_init(self):
        # modelo, algoritmos, gui y pruebas son paquetes de python
        for carpeta in ["modelo", "algoritmos", "gui", "pruebas"]:
            self.assertTrue(os.path.isfile(ruta(carpeta, "__init__.py")),
                            carpeta + " no tiene __init__.py")

    def test_gitignore_existe(self):
        self.assertTrue(os.path.isfile(ruta(".gitignore")))
        with open(ruta(".gitignore"), "r", encoding="utf-8") as f:
            contenido = f.read()
        # lo basico que no debe entrar al repositorio
        self.assertIn("__pycache__", contenido)
        self.assertIn("*.pyc", contenido)

    def test_readme_documenta_como_ejecutar(self):
        with open(ruta("README.md"), "r", encoding="utf-8") as f:
            readme = f.read().lower()
        # comandos de ejecucion
        self.assertIn("python -m unittest discover", readme)
        self.assertIn("python -m gui.main", readme)

    def test_readme_documenta_restricciones(self):
        with open(ruta("README.md"), "r", encoding="utf-8") as f:
            readme = f.read().lower()
        self.assertIn("solo python", readme)
        self.assertIn("bibliotecas externas", readme)
        self.assertIn("tkinter", readme)

    def test_readme_documenta_contrato(self):
        with open(ruta("README.md"), "r", encoding="utf-8") as f:
            readme = f.read()
        # el contrato de la issue 1 debe estar documentado
        for metodo in ["estado_inicial()", "sucesores(estado)",
                       "es_meta(estado)", "costo(estado, accion)"]:
            self.assertIn(metodo, readme,
                          "el README no documenta " + metodo)


if __name__ == "__main__":
    unittest.main()
