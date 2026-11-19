import os
import shutil
import tempfile
import unittest
from unittest import mock

from gui import main
from gui.main import Aplicacion

DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")


class TestVentana(unittest.TestCase):

    def setUp(self):
        self.app = Aplicacion()
        self.app.withdraw()  # ventana oculta durante la prueba

    def tearDown(self):
        self.app.destroy()

    def _examinar(self, nombre, ruta):
        with mock.patch.object(main.filedialog, "askopenfilename",
                               return_value=ruta):
            self.app.examinar(nombre)

    def _cargar_los_cuatro(self, carpeta):
        for nombre in self.app.archivos:
            self._examinar(nombre, os.path.join(carpeta, nombre))

    def test_widgets_de_carga(self):
        # una fila por archivo, con ruta y estado vacios al inicio
        self.assertEqual(len(self.app.etiquetas_ruta), 4)
        self.assertEqual(len(self.app.etiquetas_estado), 4)
        for nombre in self.app.archivos:
            self.assertIsNone(self.app.archivos[nombre])
            self.assertEqual(self.app.etiquetas_ruta[nombre].cget("text"),
                             "(sin archivo)")
            self.assertEqual(self.app.etiquetas_estado[nombre].cget("text"),
                             "")

    def test_menu_de_algoritmos(self):
        # los cuatro nombres que pide la issue #16
        valores = list(self.app.combo.cget("values"))
        self.assertEqual(valores,
                         ["BFS", "Costo uniforme", "IDDFS", "A*"])
        self.assertEqual(self.app.combo.get(), "BFS")

    def test_examinar_archivo_valido(self):
        ruta = os.path.join(DATOS, "profesores.txt")
        self._examinar("profesores.txt", ruta)
        # ruta mostrada, indicador en verde y ruta guardada
        self.assertEqual(self.app.etiquetas_ruta["profesores.txt"].cget("text"),
                         ruta)
        self.assertIn("✔", self.app.etiquetas_estado["profesores.txt"].cget("text"))
        self.assertEqual(self.app.archivos["profesores.txt"], ruta)

    def test_examinar_archivo_con_error(self):
        ruta = os.path.join(DATOS, "no_existe.txt")
        self._examinar("salones.txt", ruta)
        self.assertIn("✘", self.app.etiquetas_estado["salones.txt"].cget("text"))
        self.assertIsNone(self.app.archivos["salones.txt"])

    def test_generar_sin_archivos_avisa(self):
        with mock.patch.object(main.messagebox, "showwarning") as aviso:
            self.app.generar()
        aviso.assert_called_once()
        self.assertIn("Faltan archivos", aviso.call_args[0][0])

    def test_generar_con_los_cuatro_archivos(self):
        # el horario sale en la grilla: 4 clases en 3 dias x 3 franjas
        self._cargar_los_cuatro(DATOS)
        self.app.generar()
        self.assertIn("Horario encontrado con BFS",
                      self.app.grilla.mensaje.cget("text"))
        self.assertEqual(len(self.app.grilla.celdas), 9)
        ocupadas = [c for c in self.app.grilla.celdas.values()
                    if c.cget("text")]
        self.assertGreater(len(ocupadas), 0)

    def test_generar_con_iddfs(self):
        self._cargar_los_cuatro(DATOS)
        self.app.combo.set("IDDFS")
        self.app.generar()
        self.assertIn("IDDFS", self.app.grilla.mensaje.cget("text"))

    def test_generar_con_costo_uniforme(self):
        self._cargar_los_cuatro(DATOS)
        self.app.combo.set("Costo uniforme")
        self.app.generar()
        self.assertIn("Costo uniforme", self.app.grilla.mensaje.cget("text"))

    def test_estadisticas_acumulan_filas(self):
        # cada ejecucion agrega una fila; limpiar las borra todas
        self._cargar_los_cuatro(DATOS)
        for nombre in ["BFS", "Costo uniforme", "IDDFS"]:
            self.app.combo.set(nombre)
            self.app.generar()
        filas = self.app.estadisticas.filas()
        self.assertEqual([f[0] for f in filas],
                         ["BFS", "Costo uniforme", "IDDFS"])
        # costo uniforme encuentra el horario mas barato (costo 4)
        self.assertEqual(filas[1][4], "4")
        self.app.estadisticas.limpiar()
        self.assertEqual(self.app.estadisticas.filas(), [])

    def test_generar_sin_solucion_avisa_en_la_grilla(self):
        # dos clases del mismo profesor y una sola franja: no hay horario
        carpeta = tempfile.mkdtemp()
        try:
            contenido = {
                "profesores.txt": "P1\n",
                "cursos.txt": "A;P1;G1\nB;P1;G2\n",
                "salones.txt": "S1\nS2\n",
                "franjas.txt": "dias;Lunes\n07:00-09:00\n",
            }
            for nombre, texto in contenido.items():
                with open(os.path.join(carpeta, nombre), "w",
                          encoding="utf-8") as f:
                    f.write(texto)
            self._cargar_los_cuatro(carpeta)
            self.app.generar()
            self.assertIn("No se encontro",
                          self.app.grilla.mensaje.cget("text"))
            self.assertEqual(self.app.grilla.celdas, {})
            self.assertEqual(self.app.estadisticas.filas()[0][3], "No")
        finally:
            shutil.rmtree(carpeta)

    def test_algoritmo_pendiente_avisa(self):
        # A* todavia no existe (#13)
        self._cargar_los_cuatro(DATOS)
        self.app.combo.set("A*")
        with mock.patch.object(main.messagebox, "showinfo") as info:
            self.app.generar()
        info.assert_called_once()
        self.assertIn("no esta implementado", info.call_args[0][1])

    def test_generar_vuelve_a_validar_los_archivos(self):
        # si un archivo cambia despues de cargarlo, generar debe avisar
        carpeta = tempfile.mkdtemp()
        try:
            for nombre in self.app.archivos:
                shutil.copy(os.path.join(DATOS, nombre),
                            os.path.join(carpeta, nombre))
            self._cargar_los_cuatro(carpeta)
            # se daña el archivo de cursos despues de la carga
            with open(os.path.join(carpeta, "cursos.txt"), "w",
                      encoding="utf-8") as f:
                f.write("Calculo;Prof_A\n")  # faltan campos
            with mock.patch.object(main.messagebox, "showerror") as error:
                self.app.generar()
            error.assert_called_once()
            self.assertIn("cursos.txt", error.call_args[0][1])
        finally:
            shutil.rmtree(carpeta)


if __name__ == "__main__":
    unittest.main()
