# Informe: parte A

Este documento cubre los tres temas asignados en la issue #21:

1. Representación del estado y espacio de búsqueda.
2. Restricciones y modelado del CSP.
3. Análisis de BFS e IDDFS.

Todo lo que se describe está implementado en `modelo/` y en `algoritmos/`.
Las cifras de los casos grandes salen de `experimentos/resultados.md`
(issue #20); las del ejemplo base se midieron sobre los archivos de
`datos/`.

## 1. Representación del estado y espacio de búsqueda

### 1.1 De los archivos al problema

El sistema recibe cuatro archivos de texto: `profesores.txt`,
`cursos.txt`, `salones.txt` y `franjas.txt`. El lector
(`modelo/lector.py`) los valida y construye un `ProblemaHorario` con:

| Dato | Tipo | Origen |
|------|------|--------|
| `clases` | lista de tuplas `(materia, profesor, grupo)` | `cursos.txt` |
| `salones` | lista de nombres | `salones.txt` |
| `dias` | lista de nombres | primera línea de `franjas.txt` |
| `franjas` | lista de `hh:mm-hh:mm` | resto de `franjas.txt` |

La clase es una tupla inmutable con sus tres atributos: materia,
profesor y grupo. No se guarda un identificador aparte porque la
combinación de los tres campos es única (el lector rechaza repetidos).
El grupo vive en la clase porque cada clase pertenece a un solo grupo,
igual que tiene un solo profesor.

### 1.2 El estado

Un estado del problema es un horario parcial. `Estado` guarda dos cosas:

- `asignaciones`: qué clase está en qué `(día, franja, salón)`.
- `pendientes`: las clases que todavía no tienen horario, en el orden
  en que se van a asignar.

La representación es **inmutable**: internamente las asignaciones son un
`frozenset` de pares y las pendientes una tupla. La propiedad
`asignaciones` devuelve un diccionario nuevo en cada acceso, así que
nadie puede modificar el estado original. Esto es importante para los
algoritmos:

- los sucesores se arman copiando las asignaciones y agregando una
  entrada, sin tocar el estado padre;
- el estado se puede comparar (`__eq__`) y usar en un conjunto
  (`__hash__`), lo que permite el conjunto de visitados de BFS;
- al ser inmutable, la misma referencia se puede compartir entre la
  cola y el conjunto de visitados sin riesgo de cambios inesperados.

El nivel de un estado es `n - len(pendientes)`, donde `n` es el número
de clases: cada nivel asigna exactamente una clase.

### 1.3 Acciones, sucesores y dominio

Una acción es `Accion(clase, dia, franja, salon)`. El problema concreto
la interpreta como "asignar esta clase a esta casilla".

El orden de asignación es fijo: `siguiente_clase(estado)` devuelve
siempre `pendientes[0]`, la primera clase del orden de `cursos.txt`.
Esa decisión tiene dos consecuencias:

1. Cada nivel del árbol asigna siempre la misma clase, así que no
   aparecen estados equivalentes que solo se diferencian en el orden en
   que se asignaron las clases.
2. Con ese orden, cada estado se alcanza por un único camino: el
   espacio de búsqueda es un **árbol**, no un grafo con caminos
   repetidos. Por eso el recorrido es reproducible de una corrida a otra
   y por eso IDDFS no necesita conjunto de visitados.

El dominio de una clase en un estado (`dominio(estado, clase)`) son
todas las combinaciones `(día, franja, salón)` que no chocan con las
clases ya asignadas. `sucesores(estado)` recorre ese dominio y devuelve
pares `(acción, estado_siguiente)`. Nunca se genera un sucesor que viole
una restricción dura.

### 1.4 Estado inicial y estado meta

- **Estado inicial:** no hay asignaciones y todas las clases están
  pendientes.
- **Estado meta:** no queda ninguna clase pendiente
  (`len(pendientes) == 0`).
- **Solución válida:** es una meta que además cumple las cuatro
  restricciones duras (`es_solucion_valida`). En la práctica todo
  sucesor generado ya las cumple; la comprobación queda como red de
  seguridad para la solución que devuelve cada algoritmo.

Todas las soluciones tienen exactamente `n` asignaciones, porque cada
paso asigna una clase distinta y no se puede repetir.

### 1.5 Tamaño del espacio de búsqueda

Sean `n` el número de clases, `D` los días, `F` las franjas y `S` los
salones. Cada clase tiene a lo sumo

```
b = D × F × S
```

valores posibles (todas las casillas). Sin poda, el árbol tiene un nodo
en el nivel 0, `b` en el nivel 1, `b²` en el nivel 2, y así hasta `b^n`
en el nivel `n`. En total:

```
1 + b + b² + ... + b^n = (b^(n+1) - 1) / (b - 1)     nodos
```

El crecimiento es exponencial en el número de clases, que es la razón
por la que los casos grandes no terminan con búsqueda no informada.

**Ejemplo base** (`datos/`): 4 clases, 3 días, 3 franjas y 2 salones.

```
b = 3 × 3 × 2 = 18
árbol completo sin poda = 1 + 18 + 324 + 5.832 + 104.976 = 111.151 nodos
```

El podado de restricciones reduce bastante el árbol. Contando los
estados alcanzables con el orden fijo de clases:

| Nivel | Clases asignadas | Estados | Sin poda (b^k) |
|-------|------------------|---------|----------------|
| 0 | 0 | 1 | 1 |
| 1 | 1 | 18 | 18 |
| 2 | 2 | 288 | 324 |
| 3 | 3 | 4.320 | 5.832 |
| 4 | 4 | 60.768 | 104.976 |
| **Total** | | **65.395** | **111.151** |

En el nivel 4 hay 60.768 horarios completos válidos de 104.976
repartos posibles (58 %). El podado descarta el 41 % del árbol teórico
del ejemplo.

En los casos grandes el número explota: el caso 4 tiene 7 clases y 12
casillas (`12^0 + ... + 12^7 = 39.069.245` nodos sin poda) y el caso 5
tiene 8 clases y 18 casillas (`18^0 + ... + 18^8 = 11.668.193.551`).
Por eso BFS e IDDFS dejan de terminar en esos casos, mientras A* los
resuelve en pocos nodos.

## 2. Restricciones y modelado del CSP

### 2.1 Variables, dominios y restricciones

El problema se modela como un CSP:

- **Variables:** las `n` clases.
- **Dominio de cada variable:** las `b = D × F × S` casillas
  `(día, franja, salón)`. Al inicio todas valen; el dominio efectivo se
  reduce con las asignaciones previas.
- **Restricciones:** relaciones binarias entre clases que comparten
  profesor, grupo o salón.

Es un CSP binario: cada restricción involucra dos clases (la que se está
asignando y una ya asignada). Las restricciones se pueden ver como tres
"colores" que no se pueden repetir a la vez: salón, profesor y grupo.

### 2.2 Restricciones duras

| # | Restricción | Significado | Función |
|---|-------------|-------------|---------|
| 1 | Salón | Dos clases no pueden ocupar el mismo salón en el mismo día y franja | `choca_salon` |
| 2 | Profesor | Un profesor no puede dictar dos clases en el mismo día y franja | `choca_profesor` |
| 3 | Grupo | Un grupo no puede tener dos clases en el mismo día y franja | `choca_grupo` |
| 4 | Asignación única | Cada clase se asigna exactamente una vez | construcción |

Formalmente, para dos clases `i` y `j` con valores `(d_i, f_i, s_i)` y
`(d_j, f_j, s_j)`:

```
R1: (d_i, f_i, s_i) ≠ (d_j, f_j, s_j)
R2: si profesor_i = profesor_j → (d_i, f_i) ≠ (d_j, f_j)
R3: si grupo_i = grupo_j     → (d_i, f_i) ≠ (d_j, f_j)
R4: cada clase aparece una sola vez
```

La restricción 4 no se comprueba en `sucesores` porque el propio
mecanismo la garantiza: cada nivel asigna `pendientes[0]` y lo saca de
la lista de pendientes. El diccionario de asignaciones tampoco puede
tener una clave repetida. `restricciones_cumplidas` la revisa igual,
para detectar estados construidos a mano.

### 2.3 Poda: dominio y comprobación hacia adelante

`dominio(estado, clase)` recorre las `b` combinaciones y descarta las
que violan R1, R2 o R3 con alguna clase ya asignada. Esto equivale a una
**comprobación hacia adelante** (*forward checking*) de una variable
contra las asignadas:

- se detectan los choques con el pasado;
- no se detectan choques entre dos clases futuras (por ejemplo, dos
  clases del mismo profesor que todavía no tienen hora), porque esas se
  verán cuando se asignen;
- por eso el espacio se reduce mucho, pero la búsqueda sigue siendo
  necesaria.

El costo de generar el dominio de una clase con `k` clases ya asignadas
es `O(b · k)`: para cada casilla se revisan las `k` asignaciones. Un
estado tiene `O(b)` sucesores, así que expandir un nodo cuesta
`O(b · k)`.

Si en vez de podar se probaran todos los repartos y se filtraran al
final (*generate and test*), el ejemplo base requeriría revisar
`18⁴ = 104.976` horarios completos. Con poda, BFS exploró 308 nodos para
encontrar el primero. Esa es la diferencia práctica del modelado.

### 2.4 Restricciones blandas y función de costo

Además de las restricciones duras, el enunciado pide preferir horarios
cómodos: no amontonar las clases de un grupo o de un profesor en el
mismo día. Eso no es una restricción (un horario con todas las clases
el mismo día sigue siendo válido), sino un **costo**:

```
costo(estado, acción) = 1
                      + clases ya asignadas del mismo grupo ese día
                      + clases ya asignadas del mismo profesor ese día
```

Cada asignación cuesta al menos 1, y se cobra una unidad extra por cada
compañero de grupo y por cada clase del mismo profesor que ya esté ese
día. El costo de un horario completo (`costo_horario`) es la suma de
esos costos, sin importar el orden en que se asignaron.

Esta separación es clave para interpretar los resultados:

- **BFS e IDDFS** ignoran el costo: devuelven el primer horario válido
  que encuentran.
- **Costo uniforme y A\*** usan el costo: devuelven el horario más
  barato.

Por eso, en el caso 1, BFS e IDDFS encuentran horarios de costo 8 y
costo uniforme y A* encuentran uno de costo 4 (ver
`experimentos/resultados.md`). Las cuatro soluciones son válidas; solo
cambia la calidad.

## 3. Análisis de BFS e IDDFS

### 3.1 Elementos comunes

Los dos algoritmos implementan la interfaz `Problema`
(`estado_inicial`, `sucesores`, `es_meta`, `costo`) y devuelven un
`Resultado(algoritmo, solucion, nodos_explorados, tiempo)`. La medición
es la misma para todos:

- **nodos explorados:** se suma 1 cada vez que un estado se saca de la
  frontera y se expande;
- **tiempo:** `time.perf_counter()` antes y después de la búsqueda.

Ninguno de los dos usa `costo`: son estrategias no informadas que solo
distinguen entre "hay solución" y "no hay solución".

### 3.2 BFS (búsqueda en amplitud)

**Implementación.** Usa una cola FIFO propia (`Cola`), construida sobre
una lista con un índice de lectura que avanza. Así desencolar es
`O(1)` amortizado, sin el `pop(0)` que desplaza toda la lista. Mantiene
un conjunto `visitados` de estados y comprueba la meta al generar cada
sucesor: el primer meta que aparece está al mínimo nivel posible.

```
cola ← [inicial]
visitados ← {inicial}
mientras la cola no esté vacía:
    estado ← desencolar()
    explorados ← explorados + 1
    para cada (acción, sucesor) de sucesores(estado):
        si sucesor es meta → devolver sucesor
        si sucesor no está en visitados:
            visitados ← visitados ∪ {sucesor}
            encolar(sucesor)
devolver "sin solución"
```

**Propiedades.**

| Aspecto | BFS |
|---------|-----|
| Completitud | Sí: el espacio es finito y recorre todos los niveles |
| Optimalidad en pasos | Sí, pero en este problema todas las soluciones tienen `n` pasos, así que no distingue |
| Optimalidad en costo | No: ignora `costo` |
| Tiempo | `O(b^n)` en el peor caso |
| Memoria | `O(b^n)`: guarda la frontera completa y los visitados |

**Medición en el ejemplo base.** BFS expandió 308 nodos en 0,0171 s y
encontró un horario de costo 7. Los 308 nodos se explican así: expandió
el inicial (1), todo el nivel 1 (18), todo el nivel 2 (288) y un nodo del
nivel 3 (1); al generar sus sucesores apareció la primera meta y se
detuvo. No llegó a expandir el nivel 4, que tiene 60.768 estados.

**Limitación principal.** La memoria. En el caso 4 exploró 82.346 nodos
en 6,327 s, pero la frontera y el conjunto de visitados llegan a tener
decenas de miles de estados; en el caso 5 (8 clases, 18 casillas) no
termina en 60 s.

**Detalle sobre el conjunto de visitados.** Con el orden fijo de clases
cada estado se alcanza por un único camino, así que en este problema el
conjunto no llega a descartar estados repetidos. Se mantiene como
salvaguarda (y para que BFS siga siendo correcto si cambia el orden de
asignación), a un costo de memoria bajo comparado con la cola.

### 3.3 IDDFS (profundidad iterativa)

**Implementación.** Repite una búsqueda en profundidad limitada con
límite creciente: 0, 1, 2, ..., hasta `n` (si no se indica otro máximo).
La DFS limitada es recursiva y se detiene al llegar a la meta o al
agotar el límite. Los nodos explorados se **acumulan** entre
iteraciones, porque IDDFS vuelve a explorar los niveles anteriores en
cada vuelta.

```
para límite = 0, 1, ..., n:
    encontrado ← dfs(inicial, límite)
    si encontrado ≠ None → devolver encontrado
devolver "sin solución"

dfs(estado, límite):
    explorados ← explorados + 1
    si estado es meta → devolver estado
    si límite = 0 → devolver None
    para cada (acción, sucesor) de sucesores(estado):
        encontrado ← dfs(sucesor, límite - 1)
        si encontrado ≠ None → devolver encontrado
    devolver None
```

No usa conjunto de visitados: con el orden fijo de clases el espacio es
un árbol y no hay ciclos.

**Propiedades.**

| Aspecto | IDDFS |
|---------|-------|
| Completitud | Sí: prueba todas las profundidades hasta `n` |
| Optimalidad en pasos | Sí (encuentra al nivel mínimo), pero todas las soluciones tienen `n` pasos |
| Optimalidad en costo | No: ignora `costo` |
| Tiempo | `O(b^n)`, con el costo extra de repetir los niveles |
| Memoria | `O(n)` estados en la pila (cada uno con hasta `n` asignaciones) |

**Medición en el ejemplo base.** IDDFS exploró 4.959 nodos en 0,0138 s
y también encontró un horario de costo 7. Son 16 veces más nodos que
BFS, por la reexploración: las iteraciones con límites 0 a 3 recorren
los niveles poco profundos, y recién en la iteración con límite 4 llega
a la meta. Aun así tardó menos en tiempo de reloj, porque no mantiene
una cola ni un conjunto de visitados grandes.

**Limitación principal.** El tiempo y la reexploración. En el caso 4
exploró 580.827 nodos (7 veces más que BFS) en 4,869 s; desde el caso 5
tampoco termina en 60 s.

### 3.4 Comparación

| Caso | Clases | Casillas | BFS (nodos / tiempo) | IDDFS (nodos / tiempo) |
|------|--------|----------|----------------------|------------------------|
| ejemplo | 4 | 18 | 308 / 0,017 s | 4.959 / 0,014 s |
| caso1 | 4 | 8 | 66 / 0,002 s | 433 / 0,002 s |
| caso2 | 5 | 8 | 354 / 0,015 s | 1.795 / 0,008 s |
| caso3 | 6 | 8 | 1.362 / 0,041 s | 5.269 / 0,039 s |
| caso4 | 7 | 12 | 82.346 / 6,327 s | 580.827 / 4,869 s |
| caso5 | 8 | 18 | no termina | no termina |

Lectura de la tabla:

- **BFS explora menos nodos** en todos los casos donde ambos terminan,
  porque se detiene apenas genera la primera meta y no repite niveles.
- **IDDFS explora más nodos** (entre 6 y 16 veces más en estos casos),
  pero suele tardar menos en tiempo de reloj: evita el costo de mantener
  la cola y el conjunto de visitados, y trabaja con listas chicas.
- **La diferencia crece con el tamaño**: en el caso 4 IDDFS explora
  7 veces más nodos que BFS, y la ventaja de memoria es lo que compensa
  ese trabajo extra.
- **Ninguno de los dos optimiza el costo.** En los casos 1 a 4 sus
  horarios cuestan 8, 8, 9 y 8, mientras costo uniforme y A* encuentran
  horarios de costo 4, 6, 8 y 7.

### 3.5 Conclusiones

1. **BFS es la opción natural para tableros chicos**: es completo, simple
   de explicar y explora menos nodos. Su problema es la memoria: guarda
   la frontera y los visitados completos, y en este problema la frontera
   del último nivel puede tener decenas de miles de estados.
2. **IDDFS es la opción cuando la memoria es el límite**: usa espacio
   lineal en la profundidad, a cambio de reexplorar los niveles
   anteriores. En las mediciones fue más rápido en tiempo de reloj, pero
   exploró bastantes más nodos.
3. **La optimalidad en pasos no aporta nada aquí**: todas las soluciones
   tienen `n` asignaciones, así que "menos pasos" no diferencia
   soluciones. La calidad del horario la mide el costo, y para eso hacen
   falta costo uniforme o A*.
4. **El podado del CSP es lo que hace viable el ejemplo**: sin poda el
   árbol tendría 111.151 nodos y 104.976 horarios candidatos; con poda,
   BFS encuentra una solución explorando 308 estados.
5. **Los dos algoritmos sirven como línea base**: permiten comparar
   cuánto aportan la función de costo y la heurística, y muestran el
   crecimiento exponencial que aparece en los casos grandes.

### 3.6 Cómo reproducir las mediciones

```bash
# pruebas de todo el proyecto
python -m unittest discover -s pruebas -t . -v

# tabla comparativa de los casos grandes (60 s por corrida)
python -m experimentos.comparar 60
```

Las cifras de los casos 1 a 5 son las de `experimentos/resultados.md`
(generadas con la versión del proyecto de la issue #20). Las del ejemplo
base se obtuvieron cargando `datos/` con `modelo.lector` y ejecutando
`bfs` y `profundidad_iterativa`.

*Nota de nomenclatura:* el enunciado llama "profundidad interactiva" al
algoritmo y el boceto de la interfaz muestra "DFS"; en el código y en la
interfaz se usa **IDDFS**. El nombre está pendiente de confirmar con el
profesor.
