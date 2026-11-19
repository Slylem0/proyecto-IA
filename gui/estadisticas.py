"""Panel de estadisticas (issue #16).

tabla que compara las ejecuciones: algoritmo, nodos explorados, tiempo,
si encontro solucion y el costo del horario. cada vez que se presiona
Generar Horario se agrega una fila nueva, asi se pueden comparar los
cuatro algoritmos con los mismos archivos.
"""

from tkinter import ttk

COLUMNAS = ("algoritmo", "nodos", "tiempo", "solucion", "costo")
TITULOS = {
    "algoritmo": "Algoritmo",
    "nodos": "Nodos explorados",
    "tiempo": "Tiempo (s)",
    "solucion": "Solucion",
    "costo": "Costo del horario",
}


def armar_fila(problema, resultado):
    """Valores de una fila de la tabla para un Resultado.

    el costo se calcula con costo_horario del problema (issue #10); si
    no hubo solucion se pone "-". esta separado de la parte grafica
    para poder probarlo sin abrir ventanas.
    """
    if resultado.encontrada:
        solucion = "Si"
        costo = problema.costo_horario(resultado.solucion)
    else:
        solucion = "No"
        costo = "-"
    return (
        resultado.algoritmo,
        resultado.nodos_explorados,
        "%.4f" % resultado.tiempo,
        solucion,
        costo,
    )


class PanelEstadisticas(ttk.LabelFrame):
    """Tabla con una fila por cada ejecucion y un boton para limpiarla."""

    def __init__(self, padre):
        super().__init__(padre, text="Estadisticas", padding=10)

        ttk.Button(self, text="Limpiar tabla", command=self.limpiar).pack(
            side="bottom", anchor="e", pady=(6, 0))

        self.tabla = ttk.Treeview(self, columns=COLUMNAS, show="headings",
                                  height=5)
        for columna in COLUMNAS:
            self.tabla.heading(columna, text=TITULOS[columna])
            self.tabla.column(columna, width=130, anchor="center")

        barra = ttk.Scrollbar(self, orient="vertical",
                              command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)

    def agregar(self, problema, resultado):
        """Agrega al final la fila de una ejecucion y la deja visible."""
        fila = self.tabla.insert("", "end",
                                 values=armar_fila(problema, resultado))
        self.tabla.see(fila)

    def filas(self):
        """Lista con los valores de cada fila (como texto)."""
        return [self.tabla.item(fila, "values")
                for fila in self.tabla.get_children()]

    def limpiar(self):
        """Borra todas las filas."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
