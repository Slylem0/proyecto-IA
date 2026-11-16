
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
    """Estado parcial del horario (inmutable).

    - asignaciones: propiedad que devuelve un diccionario nuevo
      {clase: (dia, franja, salon)}, donde clase es la tupla
      (materia, profesor, grupo)
    - pendientes: tupla con las clases que aun no tienen horario

    Internamente las asignaciones se guardan como frozenset y las
    pendientes como tupla, de modo que ninguna de las dos se puede
    cambiar despues de crear el estado. El estado define __eq__ y
    __hash__, asi que sirve como elemento de un conjunto de visitados.
    """

    __slots__ = ("_asignaciones", "_pendientes")

    def __init__(self, asignaciones=None, pendientes=None):
        # se guardan como frozenset/tupla para que no se puedan cambiar
        self._asignaciones = (
            frozenset(asignaciones.items()) if asignaciones else frozenset())
        self._pendientes = tuple(pendientes) if pendientes else ()

    @property
    def asignaciones(self):
        """Copia del diccionario de asignaciones (nueva en cada acceso)."""
        return dict(self._asignaciones)

    @property
    def pendientes(self):
        return self._pendientes

    def __eq__(self, otro):
        return (isinstance(otro, Estado)
                and self._asignaciones == otro._asignaciones
                and self._pendientes == otro._pendientes)

    def __hash__(self):
        return hash((self._asignaciones, self._pendientes))

    def __repr__(self):
        return "Estado(asignadas=%d, pendientes=%d)" % (
            len(self._asignaciones), len(self._pendientes))
