
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
        """Una accion es valida si no viola ninguna de las tres
        restricciones de choque contra las clases ya asignadas.
        (La cuarta restriccion, que cada clase se asigne exactamente
        una vez, se revisa en restricciones_cumplidas)."""
        dia, franja, salon = accion.dia, accion.franja, accion.salon
        profesor, grupo = accion.clase[1], accion.clase[2]
        return (not self.choca_salon(estado, dia, franja, salon)
                and not self.choca_profesor(estado, profesor, dia, franja)
                and not self.choca_grupo(estado, grupo, dia, franja))

    def choca_salon(self, estado, dia, franja, salon):
        """Restriccion 1: un salon no puede tener dos clases
        en la misma franja. True si el salon ya esta ocupado
        en ese dia y esa franja."""
        for (d, f, s) in estado.asignaciones.values():
            if d == dia and f == franja and s == salon:
                return True
        return False

    def choca_profesor(self, estado, profesor, dia, franja):
        """Restriccion 2: un profesor no puede dictar dos clases
        en la misma franja. True si ese profesor ya tiene una clase
        en ese dia y esa franja."""
        for otra_clase, (d, f, s) in estado.asignaciones.items():
            if d == dia and f == franja and otra_clase[1] == profesor:
                return True
        return False

    def choca_grupo(self, estado, grupo, dia, franja):
        """Restriccion 3: un grupo de estudiantes no puede tener dos
        clases en la misma franja. True si ese grupo ya tiene una clase
        en ese dia y esa franja."""
        for otra_clase, (d, f, s) in estado.asignaciones.items():
            if d == dia and f == franja and otra_clase[2] == grupo:
                return True
        return False

    def restricciones_cumplidas(self, estado):
        """Verifica las cuatro restricciones duras del enunciado en un
        estado. Sirve para comprobar en las pruebas que los sucesores
        nunca las violan y para validar soluciones de los algoritmos."""
        # restricciones 1 a 3: choques entre las clases ya asignadas
        items = list(estado.asignaciones.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                c1, (d1, f1, s1) = items[i]
                c2, (d2, f2, s2) = items[j]
                if d1 == d2 and f1 == f2:
                    if s1 == s2 or c1[1] == c2[1] or c1[2] == c2[2]:
                        return False
        # restriccion 4: cada clase asignada exactamente una vez.
        # asignaciones es un diccionario, asi que no puede haber claves
        # repetidas; lo que hay que revisar es que ninguna clase que
        # sigue pendiente este ya asignada (puede pasar con estados
        # construidos a mano)
        for clase in estado.pendientes:
            if clase in estado.asignaciones:
                return False
        return True

    def es_solucion_valida(self, estado):
        """Un estado es solucion valida cuando es meta (todas las clases
        asignadas) y ademas cumple las cuatro restricciones duras.
        Los algoritmos de busqueda lo usan al final, como comprobacion
        extra de la solucion encontrada."""
        return self.es_meta(estado) and self.restricciones_cumplidas(estado)
