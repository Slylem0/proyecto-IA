# Informe: parte B

La [parte A](informe_parte_a.md) describe el estado, las restricciones duras
y las búsquedas BFS e IDDFS. Esta parte justifica cómo se evalúa la
calidad de un horario y compara las cuatro búsquedas implementadas.

## Función de costo

Cada asignación válida cuesta una unidad base, más una por cada clase
del mismo grupo ya asignada ese día y otra por cada clase del mismo
profesor ya asignada ese día. Si una pareja coincide tanto en grupo
como en profesor, aporta dos unidades. Las restricciones duras
siguen determinando qué asignaciones son válidas.

En un horario completo de `n` clases, el costo es `n` más el número
de parejas del mismo grupo programadas el mismo día y el número de
parejas del mismo profesor programadas el mismo día. Cada pareja se
cobra al asignar la segunda clase, así que el total es independiente
del orden de asignación. Esta penalización favorece repartir la carga
durante la semana. El costo unitario por sí solo daría el mismo valor
a todos los horarios completos, porque todos tienen exactamente `n`
asignaciones.

Costo uniforme prioriza el costo acumulado `g`. Como cada paso cuesta
al menos uno, la primera meta que extrae tiene costo mínimo. A* usa
`f = g + h` y, en caso de empate en `f`, prioriza un `g` mayor.

## Heurística de A*

La heurística simple `h₀` cuenta las clases pendientes. Es una cota
inferior porque cada clase cuesta al menos una unidad.

La heurística implementada suma, para cada clase pendiente, el menor
costo que tendría asignarla en cualquiera de los días al considerar
solo las clases ya asignadas. Para una clase de grupo `G` y profesor
`P`, el término es el mínimo, sobre todos los días, de
`1 + clases de G ese día + clases de P ese día`. Cada término es
al menos uno, así que esta heurística domina a `h₀`.

- **Admisibilidad.** En cualquier continuación válida, el día elegido
  para cada clase tiene el costo estimado para ese día o uno mayor,
  porque las asignaciones previas permanecen y pueden sumarse otras.
  Minimizar sobre todos los días permite incluso días sin casillas
  disponibles para esa clase. La suma de esos mínimos es una cota
  inferior al costo restante.
- **Consistencia.** Al asignar una clase, su término desaparece de
  `h` y vale como máximo el costo del paso. Para las demás clases,
  los costos estimados por día solo pueden aumentar o mantenerse,
  por lo que sus mínimos también. Así, `h(s) ≤ c(s, a) + h(s')`.
  En la meta, la suma vacía vale cero. Con esta heurística, A* puede
  devolver la primera meta extraída con garantía de costo mínimo.

## Pruebas y comparación

Las pruebas automatizadas verifican la función de costo y su suma
incremental, la heurística y la validez de las soluciones. Los
[nueve casos pequeños](casos_pequenos.md) incluyen seis con soluciones
contadas a mano y tres imposibles por capacidad de profesor, salón
o grupo. También se verifica el flujo de Tkinter con los cuatro
archivos de ejemplo, el botón Generar Horario, un hilo real y la
actualización de la grilla y las estadísticas para cada algoritmo.

Los [resultados completos](../experimentos/resultados.md) registran
nodos, tiempo y costo para ocho casos. Cada corrida tuvo un límite de
60 segundos. Los tiempos corresponden a esa medición. El contador de
IDDFS incluye llamadas al alcanzar el límite de profundidad y la
meta, por lo que las cifras de nodos no representan exactamente la
misma operación en todos los algoritmos.

| Caso | Clases | BFS (nodos / costo) | Costo uniforme (nodos / costo) | IDDFS (nodos / costo) | A* (nodos / costo) | A* con h₀ (nodos / costo) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 66 / 8 | 257 / 4 | 433 / 8 | 4 / 4 | 4 / 4 |
| 2 | 5 | 354 / 8 | 1345 / 6 | 1795 / 8 | 35 / 6 | 545 / 6 |
| 3 | 6 | 1362 / 9 | 3345 / 8 | 5269 / 9 | 67 / 8 | 1857 / 8 |
| 4 | 7 | 82346 / 8 | >60 s | 580827 / 8 | 7 / 7 | 7 / 7 |
| 5 | 8 | >60 s | >60 s | >60 s | 8 / 8 | 8 / 8 |
| 6 | 15 | >60 s | >60 s | >60 s | 15 / 15 | 15 / 15 |
| 7 | 30 | >60 s | >60 s | >60 s | 30 / 30 | 30 / 30 |
| 8 | 8 | >60 s | >60 s | >60 s | >60 s | >60 s |

En los casos 2 y 3, la heurística implementada redujo los nodos de
A* de 545 a 35 y de 1857 a 67, respectivamente, con el mismo costo
óptimo. También bajó el tiempo registrado de 0,029 a 0,002 s y de
0,078 a 0,004 s. En los casos 6 y 7 ambas heurísticas expandieron
la misma cantidad de nodos, y la más simple tardó menos. Alcanzar
un costo igual al número de clases certifica la optimalidad con la
cota del costo base, como ocurre en esos dos casos.

El caso 8 concentra cuatro clases de cada grupo en tres días, lo
que obliga a que cada grupo tenga al menos una pareja el mismo día.
Eso genera penalizaciones inevitables y el ensayo agotó su presupuesto
de tiempo con todas las estrategias. El resultado experimental solo
establece que no se obtuvo una respuesta dentro de los 60 segundos.

Para ejecutar las pruebas y reproducir la comparación desde la raíz
del repositorio, con Tkinter y una sesión gráfica disponibles:

```bash
python -m unittest discover -s pruebas -t . -v
python -m experimentos.comparar 60
```

El segundo comando vuelve a generar `experimentos/resultados.md`.

## Conclusiones

BFS e IDDFS sirven para obtener un horario válido en instancias
pequeñas. En los cuatro casos donde ambos terminaron, encontraron
el mismo costo entre sí, superior al obtenido por A*. Costo uniforme
confirmó el óptimo de A* en los tres casos que logró resolver, pero
agotó el límite a partir del cuarto.

A* resolvió siete de los ocho casos y llegó a 30 clases dentro del
límite. La heurística más informativa aportó su mayor ahorro en los
casos 2 y 3, y su cálculo adicional tuvo un costo visible donde no
redujo las expansiones. El caso 8 muestra que la concentración de
clases por grupo también condiciona el rendimiento. Una extensión
posible es incorporar a la cota los costos inevitables entre clases
pendientes.
