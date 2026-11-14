"""Contrato de la interfaz Problema (issue #1).

Todos los algoritmos (BFS, IDDFS, costo uniforme y A*) dependen solo de esta
interfaz, no de cómo está modelado el horario por dentro.
"""

from abc import ABC, abstractmethod

from modelo.estado import Accion, Estado


class Problema(ABC):
    """Problema de búsqueda sobre estados de asignación parcial."""

    @abstractmethod
    def estado_inicial(self) -> Estado:
        """Devuelve el estado sin clases asignadas y con todas pendientes."""

    @abstractmethod
    def sucesores(self, estado: Estado) -> list[tuple[Accion, Estado]]:
        """Devuelve los pares (acción, estado resultante) de asignar la
        siguiente clase pendiente (pendientes[0]).

        Solo incluye sucesores que cumplen las restricciones duras (choque de
        salón, de profesor y de grupo). Si el estado es meta, devuelve [].
        El orden de la lista es determinista para que los resultados se puedan
        reproducir.
        """

    @abstractmethod
    def es_meta(self, estado: Estado) -> bool:
        """True si no quedan clases pendientes (todas asignadas una vez)."""

    @abstractmethod
    def costo(self, estado: Estado, accion: Accion) -> float:
        """Costo de aplicar `accion` en `estado`. Debe ser mayor o igual a 0.

        La definición concreta se decide en la issue #10.
        """
