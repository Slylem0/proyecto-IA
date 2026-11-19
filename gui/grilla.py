"""Grilla del horario (issue #15).

muestra el horario encontrado como una tabla: las filas son las
franjas y las columnas los dias. cada celda dice que clases hay en esa
franja ese dia (materia, grupo, profesor y salon). las celdas libres
quedan en gris.
"""

import tkinter as tk
from tkinter import ttk

COLOR_LIBRE = "#e6e6e6"
COLOR_OCUPADA = "#fff4d6"


def armar_celdas(solucion):
    """Agrupa las clases de un horario por (dia, franja).

    devuelve un diccionario {(dia, franja): [texto, ...]} donde cada
    texto es "materia (grupo)", el profesor y el salon en lineas
    separadas. en una misma franja puede haber varias clases (en
    salones distintos), por eso es una lista.

    esta separado de la parte grafica para poder probarlo sin abrir
    ventanas.
    """
    celdas = {}
    for clase, (dia, franja, salon) in solucion.asignaciones.items():
        materia, profesor, grupo = clase
        texto = "%s (%s)\n%s\n%s" % (materia, grupo, profesor, salon)
        if (dia, franja) not in celdas:
            celdas[(dia, franja)] = []
        celdas[(dia, franja)].append(texto)
    # orden fijo dentro de cada celda para que no cambie entre corridas
    for textos in celdas.values():
        textos.sort()
    return celdas


class Grilla(ttk.LabelFrame):
    """Panel con la tabla del horario.

    mensaje: etiqueta de arriba (que algoritmo encontro el horario, o
    que no hubo solucion)
    celdas: {(dia, franja): Label} de la ultima tabla dibujada, la usan
    las pruebas para revisar lo que se ve
    """

    def __init__(self, padre):
        super().__init__(padre, text="Horario", padding=10)
        self.mensaje = ttk.Label(
            self, text="Carga los archivos y presiona Generar Horario.",
            foreground="gray")
        self.mensaje.pack(anchor="w", pady=(0, 6))
        self.tabla = None
        self.celdas = {}

    def limpiar(self):
        """Borra la tabla anterior, si habia una."""
        if self.tabla is not None:
            self.tabla.destroy()
            self.tabla = None
        self.celdas = {}

    def mostrar(self, problema, resultado):
        """Dibuja el horario del resultado, o avisa si no hubo solucion."""
        self.limpiar()
        if not resultado.encontrada:
            self.mensaje.config(
                text="No se encontro un horario sin choques con %s."
                % resultado.algoritmo,
                foreground="red")
            return

        self.mensaje.config(text="Horario encontrado con %s."
                            % resultado.algoritmo, foreground="")
        contenido = armar_celdas(resultado.solucion)

        self.tabla = ttk.Frame(self)
        self.tabla.pack(fill="both", expand=True)

        # fila 0: los dias; columna 0: las franjas
        ttk.Label(self.tabla, text="Franja").grid(row=0, column=0, padx=4)
        for c, dia in enumerate(problema.dias, start=1):
            ttk.Label(self.tabla, text=dia, anchor="center").grid(
                row=0, column=c, sticky="ew", pady=(0, 4))
            self.tabla.columnconfigure(c, weight=1, uniform="dias")

        for f, franja in enumerate(problema.franjas, start=1):
            ttk.Label(self.tabla, text=franja).grid(
                row=f, column=0, sticky="w", padx=4)
            self.tabla.rowconfigure(f, weight=1, uniform="franjas")
            for c, dia in enumerate(problema.dias, start=1):
                textos = contenido.get((dia, franja))
                if textos:
                    texto = "\n\n".join(textos)
                    color = COLOR_OCUPADA
                else:
                    texto = ""
                    color = COLOR_LIBRE
                celda = tk.Label(self.tabla, text=texto, bg=color, fg="black",
                                 relief="solid", borderwidth=1,
                                 justify="center", padx=4, pady=4)
                celda.grid(row=f, column=c, sticky="nsew", padx=1, pady=1)
                self.celdas[(dia, franja)] = celda
