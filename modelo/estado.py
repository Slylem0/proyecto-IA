"""Contrato del Estado (issue #1).

Un estado es una asignación parcial de clases a (día, franja, salón) junto con
las clases que todavía no se han asignado. Solo usa la biblioteca estándar.
"""

from dataclasses import dataclass
from typing import NamedTuple

# Identificadores simples (str) tomados de los archivos .txt.
Clase = str
Dia = str
Franja = str
Salon = str

# Valor que se le asigna a una clase: (día, franja, salón).
Asignacion = tuple[Dia, Franja, Salon]


class Accion(NamedTuple):
    """Asignar `clase` a (`dia`, `franja`, `salon`). Es el paso entre dos estados."""

    clase: Clase
    dia: Dia
    franja: Franja
    salon: Salon


@dataclass(frozen=True)
class Estado:
    """Asignación parcial de clases.

    Atributos:
        asignaciones: pares (clase, (día, franja, salón)) de las clases ya
            asignadas, en el orden en que se asignaron. Equivale al diccionario
            {clase: (día, franja, salón)}, pero como tupla para que el estado
            sea inmutable y hashable.
        pendientes: clases que faltan por asignar, en el orden de selección
            definido en la issue #5. La siguiente clase a asignar es pendientes[0].

    Invariantes:
        - Una clase aparece una sola vez, ya sea en asignaciones o en pendientes.
        - Estado inicial: asignaciones vacía y pendientes con todas las clases.
        - Estado meta: pendientes vacía.
        - La profundidad del estado es len(asignaciones).

    Al ser inmutable, generar un sucesor crea un Estado nuevo y no modifica el
    anterior, así que los algoritmos pueden compartir estados sin copiarlos.
    """

    asignaciones: tuple[tuple[Clase, Asignacion], ...]
    pendientes: tuple[Clase, ...]
