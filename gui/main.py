import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from algoritmos.amplitud import bfs
from algoritmos.profundidad_iterativa import profundidad_iterativa
from gui.carga import ARCHIVOS, construir_problema, leer_archivo
from modelo.lector import ErrorDeFormato

# algoritmos del menu (mismos nombres que pide la issue #16);
# los que estan en None se activan cuando existan sus issues
ALGORITMOS = {
    "BFS": bfs,
    "Costo uniforme": None,
    "IDDFS": profundidad_iterativa,
    "A*": None,
}


class Aplicacion(tk.Tk):
    """Ventana principal."""

    def __init__(self):
        super().__init__()
        self.title("Programacion Academica Universitaria")
        self.geometry("780x460")
        self.minsize(660, 400)

        self.archivos = {}  # nombre -> ruta (None si no se ha cargado)
        self.etiquetas_ruta = {}
        self.etiquetas_estado = {}
        for nombre in ARCHIVOS:
            self.archivos[nombre] = None

        self._crear_panel_carga()
        self._crear_panel_configuracion()

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
        """Menu de algoritmos y boton Generar Horario."""
        marco = ttk.LabelFrame(self, text="Configuracion", padding=10)
        marco.pack(fill="x", padx=10, pady=5)

        ttk.Label(marco, text="Algoritmo:").pack(side="left")
        self.combo = ttk.Combobox(marco, values=list(ALGORITMOS),
                                  state="readonly", width=22)
        self.combo.set(list(ALGORITMOS)[0])
        self.combo.pack(side="left", padx=8)

        ttk.Button(marco, text="Generar Horario",
                   command=self.generar).pack(side="right")

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
        """Revisa los 4 archivos y ejecuta el algoritmo del menu."""
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
        algoritmo = ALGORITMOS[nombre]
        if algoritmo is None:
            messagebox.showinfo(
                "Algoritmo no disponible",
                nombre + " todavia no esta implementado.\n"
                "Se activa cuando se integre su issue.")
            return

        resultado = algoritmo(problema)

        if resultado.encontrada:
            texto = ("Solucion encontrada con %s.\n\n"
                     "Nodos explorados: %d\n"
                     "Tiempo: %.4f s"
                     % (resultado.algoritmo, resultado.nodos_explorados,
                        resultado.tiempo))
        else:
            texto = ("No se encontro solucion con %s.\n\n"
                     "Nodos explorados: %d\n"
                     "Tiempo: %.4f s"
                     % (resultado.algoritmo, resultado.nodos_explorados,
                        resultado.tiempo))
        messagebox.showinfo("Resultado", texto)


def main():
    Aplicacion().mainloop()


if __name__ == "__main__":
    main()
