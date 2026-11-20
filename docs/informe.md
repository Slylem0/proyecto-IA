# Generación de horarios académicos

El programa recibe una lista de clases, profesores, salones y franjas, y busca un horario sin choques. Implementamos BFS, IDDFS, costo uniforme y A* para comparar dos cosas: cuánto trabajo hace cada algoritmo y qué tan repartida queda la carga de profesores y grupos. Los cuatro se pueden ejecutar desde la misma interfaz de Tkinter.

## Representación del estado y espacio de búsqueda

Una clase se identifica por la tupla `(materia, profesor, grupo)`. Un estado guarda las clases que ya tienen una casilla `(día, franja, salón)` y las que faltan por asignar. Al comienzo todas están pendientes. Llegamos a una meta cuando la lista de pendientes queda vacía.

En cada paso tomamos la primera clase pendiente, siguiendo el orden de `cursos.txt`. Para cada casilla compatible creamos un estado nuevo. Las asignaciones se guardan internamente como un conjunto inmutable de pares y las pendientes como una tupla. Esto permite comparar estados, usarlos en un conjunto y generar sucesores sin modificar el estado padre.

El orden fijo hace que cada estado alcanzable tenga un solo camino desde el inicial. La búsqueda recorre un árbol de profundidad máxima `n`, donde `n` es el número de clases. Si hay `D` días, `F` franjas y `S` salones, cada nodo tiene a lo sumo `b = D × F × S` sucesores. Sin restricciones el árbol tendría `1 + b + … + bⁿ` nodos. Para `b > 1` esa suma es `(bⁿ⁺¹ − 1)/(b − 1)`. Con una sola casilla hay a lo sumo `n + 1` nodos.

Los archivos de ejemplo de `datos/` tienen 4 clases y 18 casillas. Esta es la diferencia entre el árbol teórico y el que queda al descartar los choques:

| Clases asignadas | Estados sin poda | Estados alcanzables |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 18 | 18 |
| 2 | 324 | 288 |
| 3 | 5.832 | 4.320 |
| 4 | 104.976 | 60.768 |
| **Total** | **111.151** | **65.395** |

Los 60.768 estados del último nivel son horarios completos válidos. Los algoritmos que se detienen en la primera solución solo recorren una parte del árbol.

## Restricciones y modelado del CSP

Cada clase es una variable y su dominio inicial contiene las casillas posibles. Al generar sucesores se descartan las casillas que choquen con alguna clase ya asignada:

| Restricción | Comprobación |
|---|---|
| Salón | Dos clases no pueden ocupar el mismo salón en el mismo día y franja. |
| Profesor | Un profesor solo puede dictar una clase por día y franja. |
| Grupo | Un grupo solo puede recibir una clase por día y franja. |
| Asignación única | Cada clase recibe una sola casilla y se retira de las pendientes. |

Las tres restricciones de choque se comprueban entre pares de clases. El orden de asignación garantiza la cuarta durante la búsqueda. El modelo también ofrece una comprobación de la solución completa para las pruebas. El filtrado solo usa las asignaciones ya hechas. Si dos clases pendientes también podrían chocar, el conflicto se detecta cuando se intenta ubicar la segunda.

## Función de costo

Además de evitar choques, queríamos repartir las clases de un mismo profesor o grupo a lo largo de la semana. Por eso asignar una clase cuesta una unidad de base, más una por cada clase de su grupo que ya quedó ese día y una por cada clase de su profesor que ya quedó ese día. Una pareja que comparte profesor y grupo suma dos unidades. Por ejemplo, si el lunes ya hay una clase del mismo grupo y otra del mismo profesor, la nueva asignación cuesta 3.

En un horario completo, el costo es el número de clases más las penalizaciones por parejas. Cada pareja se cobra al ubicar la segunda clase, así que el total da lo mismo en cualquier orden de asignación. Un costo de una unidad por paso habría dejado empatados todos los horarios completos. La penalización permite que costo uniforme y A* distingan entre ellos.

## Estrategias de búsqueda

### Análisis de BFS e IDDFS

BFS usa una cola FIFO y recorre el árbol por niveles. Cuenta los estados que desencola y comprueba si un sucesor es meta al generarlo. Guarda los estados visitados, aunque con el orden fijo de este problema cada estado se alcanza una sola vez. El costo principal es mantener la frontera y los visitados. En el peor caso el número de estados que guarda crece exponencialmente con la profundidad.

IDDFS repite una búsqueda en profundidad con límites de 0 a `n`. Cuenta cada llamada, incluidas las que se detienen en el límite y la que encuentra la meta. Al aumentar el límite vuelve a visitar los primeros niveles. La pila tiene a lo sumo `O(n)` marcos, pero cada marco puede retener una lista de hasta `b` sucesores. En esta implementación pueden quedar hasta `O(b · n)` estados en esas listas, cada uno con hasta `n` asignaciones.

Ambas búsquedas son completas en el árbol finito del problema. Encuentran una meta de profundidad mínima, pero todos los horarios válidos requieren el mismo número de pasos. Su peor caso crece exponencialmente con `n` para un factor de ramificación fijo mayor que uno.

En el ejemplo de `datos/`, BFS contó 308 estados: el inicial, los 18 del primer nivel, los 288 del segundo y el primero del tercero. En ese último estado encontró una meta al generar los sucesores. IDDFS contó 4.959 llamadas acumuladas. Los dos encontraron un horario de costo 7.

### Costo uniforme y A*

Costo uniforme saca de la cola de prioridad el estado con menor costo acumulado `g`. Cada paso cuesta al menos uno, de modo que la primera meta que extrae tiene costo mínimo. A* ordena la misma clase de cola por `f = g + h`. Cuando dos estados tienen el mismo `f`, se atiende primero el de mayor `g`.

Usamos dos versiones de `h` en la comparación:

- **Heurística simple.** Cuenta las clases pendientes. Cada una cuesta al menos una unidad.
- **Heurística del modelo.** Para cada clase pendiente calcula cuánto costaría asignarla en cada día teniendo en cuenta las clases ya ubicadas. Luego toma el menor de esos costos y suma un mínimo por clase.

La segunda es admisible porque el día que finalmente se elija para cada clase tendrá como mínimo las asignaciones que ya tenía al estimar su costo. El cálculo puede considerar incluso días sin una casilla libre para esa clase. Así, sumar los mínimos da una cota inferior, y cada término es por lo menos uno.

También es consistente. Cuando se asigna una clase, el término que sale de la suma es a lo sumo lo que realmente costó ese paso. Los mínimos de las demás clases se mantienen o suben, porque se agregó una asignación. Por tanto, si `s'` es un sucesor de `s`, se cumple `h(s) ≤ c(s, a) + h(s')`. En una meta la suma es cero. Con esta heurística, la primera meta que A* extrae tiene costo mínimo.

## Pruebas y resultados

Los [nueve casos pequeños](casos_pequenos.md) sirven para verificar el programa con resultados que se pueden contar a mano. Los seis casos factibles tienen 1, 2, 2, 8, 24 y 6 soluciones. Los otros tres aíslan un choque imposible de resolver por capacidad de profesor, salón o grupo. Las pruebas también comprueban el costo, la heurística y la validez de los horarios que devuelven los cuatro algoritmos.

La prueba de extremo a extremo carga los cuatro archivos de ejemplo con los controles de Tkinter, ejecuta cada algoritmo en un hilo real y revisa que aparezcan las cuatro clases en la grilla y se agregue una fila a las estadísticas. En ese ejemplo, costo uniforme y A* encontraron un horario de costo 4, frente al costo 7 de BFS e IDDFS.

La siguiente tabla resume los [resultados de los ocho casos](../experimentos/resultados.md). Cada celda muestra nodos contabilizados y costo del horario. Las corridas se limitaron a 60 segundos. El contador de IDDFS incluye las llamadas que llegan al límite y a la meta, de modo que el número de nodos y el tiempo describen aspectos distintos del trabajo.

| Caso | Clases | BFS | Costo uniforme | IDDFS | A* | A* con heurística simple |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 66 / 8 | 257 / 4 | 433 / 8 | 4 / 4 | 4 / 4 |
| 2 | 5 | 354 / 8 | 1.345 / 6 | 1.795 / 8 | 35 / 6 | 545 / 6 |
| 3 | 6 | 1.362 / 9 | 3.345 / 8 | 5.269 / 9 | 67 / 8 | 1.857 / 8 |
| 4 | 7 | 82.346 / 8 | >60 s | 580.827 / 8 | 7 / 7 | 7 / 7 |
| 5 | 8 | >60 s | >60 s | >60 s | 8 / 8 | 8 / 8 |
| 6 | 15 | >60 s | >60 s | >60 s | 15 / 15 | 15 / 15 |
| 7 | 30 | >60 s | >60 s | >60 s | 30 / 30 | 30 / 30 |
| 8 | 8 | >60 s | >60 s | >60 s | >60 s | >60 s |

En los casos 2 y 3, la heurística del modelo bajó las expansiones de A* de 545 a 35 y de 1.857 a 67, con el mismo costo óptimo. En esas corridas los tiempos bajaron de 0,029 a 0,002 s y de 0,078 a 0,004 s. En los casos 6 y 7 las dos heurísticas expandieron la misma cantidad de nodos y la simple tardó menos. Ambos horarios costaron exactamente lo mismo que su número de clases, así que alcanzaron la cota del costo base.

El caso 8 tiene dos grupos con cuatro clases cada uno y solo tres días. Cada grupo aporta al menos una penalización por compartir día. Las cinco variantes agotaron el tiempo de ensayo. La corrida quedó sin un resultado del que se pueda concluir si existe una solución o cuál sería su costo.

## Conclusiones

Para los casos pequeños, BFS e IDDFS encuentran horarios válidos con el mismo costo en nuestras pruebas. BFS contó menos nodos en los cuatro casos comparables. Por ejemplo, en el caso 4 IDDFS contó unas siete veces más nodos y tardó 4,869 s, frente a los 6,327 s de BFS. Costo uniforme confirmó el óptimo de A* en los tres casos que alcanzó a resolver.

A* resolvió siete de los ocho casos, incluido el de 30 clases. La comparación más clara fue entre los casos 7 y 8: el primero era más grande y permitía un horario de costo base, mientras que el segundo concentraba las clases de cada grupo y agotó el tiempo disponible. Incorporar a la heurística las penalizaciones inevitables entre clases pendientes sería una forma de estudiar ese caso.

## Reproducción

El [modelo y la función de costo](../modelo/problema.py), las [implementaciones de búsqueda](../algoritmos/) y las [pruebas](../pruebas/) están en el repositorio.

Desde la raíz del repositorio, con Python, Tkinter y una sesión gráfica:

```bash
python -m gui.main
python -m unittest discover -s pruebas -t . -v
python -m experimentos.comparar 60
```

Para la GUI se cargan `profesores.txt`, `cursos.txt`, `salones.txt` y `franjas.txt` de `datos/`. El último comando vuelve a generar la tabla en `experimentos/resultados.md`. El [formato de entrada](formato_datos.md) describe los campos de los cuatro archivos.
