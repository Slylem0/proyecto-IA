
from modelo.estado import Accion, Estado


class Problema:
    """Contrato de un problema de busqueda en espacios de estados.

    Los algoritmos (BFS, costo uniforme, profundidad iterativa, A*)
    trabajan unicamente contra esta interfaz.
    """

    def estado_inicial(self):
        raise NotImplementedError

    def sucesores(self, estado):
        raise NotImplementedError

    def es_meta(self, estado):
        raise NotImplementedError

    def costo(self, estado, accion):
        raise NotImplementedError


class ProblemaHorario(Problema):
    """Problema concreto: asignar a cada clase un (dia, franja, salon).

    Una accion es asignar una clase pendiente a una combinacion
    (dia, franja, salon), representada con la clase Accion.
    """

    def __init__(self, clases, salones, dias, franjas):
        # clases: lista de tuplas (materia, profesor, grupo)
        self.clases = list(clases)
        self.salones = list(salones)
        self.dias = list(dias)
        self.franjas = list(franjas)

    def estado_inicial(self):
        """Estado inicial: ninguna clase asignada, todas pendientes."""
        return Estado({}, self.clases)

    def siguiente_clase(self, estado):
        """Clase que se asigna en el siguiente paso.

        Orden de seleccion: se toma siempre la PRIMERA clase pendiente
        (pendientes[0]), es decir, las clases se asignan en el orden en
        que se declararon en el problema (el orden de cursos.txt).

        Por que ese orden:
        - cada nivel del arbol de busqueda asigna siempre la misma clase,
          de modo que no aparecen estados equivalentes que solo se
          diferencian en el orden en que se asignaron;
        - el recorrido del arbol es reproducible de una corrida a otra.

        Devuelve None si no queda ninguna clase pendiente.
        """
        if estado.pendientes:
            return estado.pendientes[0]
        return None

    def dominio(self, estado, clase):
        """Dominio de una clase en un estado.

        Son todas las combinaciones (dia, franja, salon) que no violan
        restricciones duras con las clases ya asignadas:
        - salon ocupado en esa franja
        - el profesor de la clase ya dicta otra en esa franja
        - el grupo de la clase ya tiene otra en esa franja

        Devuelve una lista de tuplas (dia, franja, salon).
        """
        dominio = []
        for dia in self.dias:
            for franja in self.franjas:
                for salon in self.salones:
                    if self.es_valida(estado, Accion(clase, dia, franja, salon)):
                        dominio.append((dia, franja, salon))
        return dominio

    def sucesores(self, estado):
        """Genera los sucesores de un estado.

        En cada paso se asigna la siguiente clase pendiente (ver
        siguiente_clase) a una de las combinaciones de su dominio (ver
        dominio). Solo se aceptan combinaciones que no violan
        restricciones duras, asi los sucesores siempre son validos.

        Devuelve una lista de pares (accion, estado_siguiente).
        """
        sucesores = []
        clase = self.siguiente_clase(estado)
        if clase is None:
            return sucesores

        for dia, franja, salon in self.dominio(estado, clase):
            accion = Accion(clase, dia, franja, salon)
            # la propiedad asignaciones ya devuelve una copia,
            # se puede llenar sin tocar el estado original
            asignadas = estado.asignaciones
            asignadas[clase] = (dia, franja, salon)
            nuevo = Estado(asignadas, estado.pendientes[1:])
            sucesores.append((accion, nuevo))
        return sucesores

    def es_meta(self, estado):
        """Un estado es meta cuando todas las clases tienen horario."""
        return len(estado.pendientes) == 0

    def costo(self, estado, accion):
        """Costo de aplicar una accion en un estado.

        Por ahora todas las acciones cuestan 1 (asignar una clase).
        El costo de un camino es entonces la cantidad de clases asignadas.
        Si mas adelante se modelan las restricciones blandas, bastaria
        con devolver un costo mayor cuando la accion las viola.
        """
        return 1

    def es_valida(self, estado, accion):
        """Revisa las restricciones duras contra las clases ya asignadas:
        - el salon no puede estar ocupado en esa franja
        - el profesor no puede dictar dos clases en la misma franja
        - el grupo no puede tener dos clases en la misma franja
        """
        dia, franja, salon = accion.dia, accion.franja, accion.salon
        profesor, grupo = accion.clase[1], accion.clase[2]
        for otra_clase, (d, f, s) in estado.asignaciones.items():
            if d == dia and f == franja:
                if s == salon:
                    return False
                if otra_clase[1] == profesor:
                    return False
                if otra_clase[2] == grupo:
                    return False
        return True

    def restricciones_cumplidas(self, estado):
        """Verifica que entre las clases ya asignadas no exista ningun
        conflicto. Sirve para comprobar en las pruebas que los sucesores
        nunca violan las restricciones duras."""
        items = list(estado.asignaciones.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                c1, (d1, f1, s1) = items[i]
                c2, (d2, f2, s2) = items[j]
                if d1 == d2 and f1 == f2:
                    if s1 == s2 or c1[1] == c2[1] or c1[2] == c2[2]:
                        return False
        return True
