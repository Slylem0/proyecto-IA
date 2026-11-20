import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from algoritmos.a_estrella import a_estrella
from algoritmos.amplitud import bfs
from algoritmos.costo_uniforme import costo_uniforme
from algoritmos.profundidad_iterativa import profundidad_iterativa
from gui.carga import ARCHIVOS, construir_problema, leer_archivo
from gui.estadisticas import PanelEstadisticas
from gui.grilla import Grilla
from modelo.lector import ErrorDeFormato

# algoritmos del menu (mismos nombres que pide la issue #16)
ALGORITMOS = {
    "BFS": bfs,
    "Costo uniforme": costo_uniforme,
    "IDDFS": profundidad_iterativa,
    "A*": a_estrella,
}

# cada cuantos milisegundos se revisa si el hilo ya termino
INTERVALO_SONDEO = 100


class Aplicacion(tk.Tk):
    """Ventana principal."""

    def __init__(self):
        super().__init__()
        self.title("Programacion Academica Universitaria")
        self.geometry("1000x860")
        self.minsize(760, 680)

        self.archivos = {}  # nombre -> ruta (None si no se ha cargado)
        self.etiquetas_ruta = {}
        self.etiquetas_estado = {}
        for nombre in ARCHIVOS:
            self.archivos[nombre] = None

        self.cola = queue.Queue()  # resultado que deja el hilo
        self.hilo = None

        self._crear_panel_carga()
        self._crear_panel_configuracion()

        # estadisticas (#16) abajo, se empaca antes que la grilla para
        # que siempre se vea aunque la ventana sea pequena
        self.estadisticas = PanelEstadisticas(self)
        self.estadisticas.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        # grilla del horario (#15), ocupa el resto de la ventana
        self.grilla = Grilla(self)
        self.grilla.pack(fill="both", expand=True, padx=10, pady=5)

    def _crear_panel_carga(self):
        """Fila por archivo: boton, ruta e indicador."""
        marco = ttk.LabelFrame(self, text="Carga de archivos", padding=10)
        marco.pack(fill="x", padx=10, pady=(10, 5))

        for nombre in ARCHIVOS:
            fila = ttk.Frame(marco)
            fila.pack(fill="x", pady=3)

            ttk.Button(fila, text="Examinar...",
                       command=lambda n=nombre: self.examinar(n)
                       ).pack(side="left")
            ttk.Label(fila, text=nombre, width=15).pack(side="left", padx=6)

            etiqueta_ruta = ttk.Label(fila, text="(sin archivo)",
                                      foreground="gray")
            etiqueta_ruta.pack(side="left", fill="x", expand=True)

            etiqueta_estado = ttk.Label(fila, text="")
            etiqueta_estado.pack(side="right", padx=4)

            self.etiquetas_ruta[nombre] = etiqueta_ruta
            self.etiquetas_estado[nombre] = etiqueta_estado

    def _crear_panel_configuracion(self):
        """Menu de algoritmos, estado y boton Generar Horario."""
        marco = ttk.LabelFrame(self, text="Configuracion", padding=10)
        marco.pack(fill="x", padx=10, pady=5)

        ttk.Label(marco, text="Algoritmo:").pack(side="left")
        self.combo = ttk.Combobox(marco, values=list(ALGORITMOS),
                                  state="readonly", width=22)
        self.combo.set(list(ALGORITMOS)[0])
        self.combo.pack(side="left", padx=8)

        self.boton_generar = ttk.Button(marco, text="Generar Horario",
                                        command=self.generar)
        self.boton_generar.pack(side="right")

        self.estado = ttk.Label(marco, text="", foreground="gray")
        self.estado.pack(side="right", padx=8)

    def examinar(self, nombre):
        """Abre el explorador y valida el archivo elegido."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar " + nombre,
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Todos los archivos", "*.*")])
        if not ruta:
            return  # el usuario cancelo

        ok, mensaje = leer_archivo(nombre, ruta)
        self.etiquetas_ruta[nombre].config(text=ruta)
        if ok:
            self.etiquetas_estado[nombre].config(text="✔ " + mensaje,
                                                 foreground="green")
            self.archivos[nombre] = ruta
        else:
            self.etiquetas_estado[nombre].config(text="✘ " + mensaje,
                                                 foreground="red")
            self.archivos[nombre] = None

    def generar(self):
        """Valida los archivos y lanza el algoritmo en segundo plano."""
        faltan = [nombre for nombre in ARCHIVOS
                  if not self.archivos[nombre]]
        if faltan:
            messagebox.showwarning(
                "Faltan archivos",
                "Debes cargar estos archivos:\n" + "\n".join(faltan))
            return

        try:
            problema = construir_problema(self.archivos)
        except (ErrorDeFormato, ValueError) as error:
            messagebox.showerror("Error en los datos", str(error))
            return

        nombre = self.combo.get()
        self._iniciar(nombre, ALGORITMOS[nombre], problema)

    def _iniciar(self, nombre, algoritmo, problema):
        """Arranca el hilo que ejecuta el algoritmo elegido."""
        self.combo.config(state="disabled")
        self.boton_generar.config(state="disabled")
        self.estado.config(text="Ejecutando " + nombre + "...")

        self.hilo = threading.Thread(target=self._ejecutar,
                                     args=(algoritmo, problema),
                                     daemon=True)
        self.hilo.start()
        self.after(INTERVALO_SONDEO, self._revisar)

    def _ejecutar(self, algoritmo, problema):
        """Corre el algoritmo (en el hilo) y deja el resultado en la cola."""
        try:
            self.cola.put(("ok", problema, algoritmo(problema)))
        except Exception as error:  # el error se avisa en la ventana
            self.cola.put(("error", str(error)))

    def _revisar(self):
        """Busca el resultado en la cola; si no esta, vuelve a preguntar."""
        try:
            datos = self.cola.get_nowait()
        except queue.Empty:
            self.after(INTERVALO_SONDEO, self._revisar)
            return

        self._habilitar()
        if datos[0] == "error":
            messagebox.showerror("Error al ejecutar", datos[1])
        else:
            self._mostrar_resultado(datos[1], datos[2])

    def _habilitar(self):
        """Vuelve a dejar el menu y el boton listos para otra ejecucion."""
        self.combo.config(state="readonly")
        self.boton_generar.config(state="normal")
        self.estado.config(text="")

    def _mostrar_resultado(self, problema, resultado):
        """Dibuja el horario en la grilla y agrega la fila de estadisticas."""
        self.grilla.mostrar(problema, resultado)
        self.estadisticas.agregar(problema, resultado)


def main():
    Aplicacion().mainloop()


if __name__ == "__main__":
    main()
