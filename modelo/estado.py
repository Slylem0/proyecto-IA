
class Accion:
    """Asignar una clase a una combinacion (dia, franja, salon)."""

    __slots__ = ("clase", "dia", "franja", "salon")

    def __init__(self, clase, dia, franja, salon):
        self.clase = clase
        self.dia = dia
        self.franja = franja
        self.salon = salon

    def __repr__(self):
        return "Accion(%s, %s, %s, %s)" % (
            self.clase[0], self.dia, self.franja, self.salon)


class Estado:
    """Estado parcial del horario.

    - asignaciones: diccionario {clase: (dia, franja, salon)}
      donde clase es la tupla (materia, profesor, grupo)
    - pendientes: tupla con las clases que aun no tienen horario

    Por convencion un Estado no se modifica despues de crearse (no hay
    metodos que lo cambien) y define __eq__ y __hash__, de modo que se
    puede usar en conjuntos de visitados y compararlo con ==.
    """

    __slots__ = ("asignaciones", "pendientes")

    def __init__(self, asignaciones=None, pendientes=None):
        # copiamos para que dos estados no compartan la misma estructura
        self.asignaciones = dict(asignaciones) if asignaciones else {}
        self.pendientes = tuple(pendientes) if pendientes else ()

    def __eq__(self, otro):
        return (isinstance(otro, Estado)
                and self.asignaciones == otro.asignaciones
                and self.pendientes == otro.pendientes)

    def __hash__(self):
        return hash((frozenset(self.asignaciones.items()), self.pendientes))

    def __repr__(self):
        return "Estado(asignadas=%d, pendientes=%d)" % (
            len(self.asignaciones), len(self.pendientes))
