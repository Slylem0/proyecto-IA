# proyecto-IA

Proyecto 1 de Inteligencia Artificial (Universidad del Valle):
**Sistema de Asignación de Horarios Universitarios**.

El programa construye el horario académico de un semestre asignando a cada
clase una franja horaria y un salón, garantizando que no se presenten
conflictos. El problema es un CSP (Problema de Satisfacción de Restricciones)
y se resuelve comparando 4 estrategias de búsqueda:

- **No informada:** amplitud (BFS), costo uniforme y profundidad iterativa
- **Informada:** A*

## Estructura del proyecto

```
proyecto-IA/
├── modelo/      Estado, Accion y la interfaz del problema (Problema, ProblemaHorario)
├── algoritmos/  Estrategias de busqueda (BFS, costo uniforme, profundidad iterativa, A*)
├── gui/         Interfaz grafica con tkinter
├── datos/       Archivos de entrada: profesores.txt, cursos.txt, salones.txt, franjas.txt
├── docs/        Documentacion (formato de datos, informes)
└── pruebas/     Pruebas automatizadas con unittest
```

## Cómo ejecutar

Requisitos: tener instalado **Python 3** (no se necesita instalar ninguna
biblioteca adicional).

Correr todas las pruebas:

```bash
python -m unittest discover -s pruebas -t . -v
```

Abrir la interfaz gráfica (cuando esté implementada):

```bash
python -m gui.main
```

## Contrato entre módulos

Los módulos se comunican solo por la interfaz definida en la issue #1:

- **`modelo`** define las piezas del problema:
  - `Accion(clase, dia, franja, salon)`: asignar una clase a una combinación.
  - `Estado`: asignaciones parciales `{clase: (dia, franja, salon)}` y clases
    pendientes. Es inmutable por convención y hashable (usable en conjuntos
    de visitados).
  - `Problema` (clase abstracta): `estado_inicial()`, `sucesores(estado)`,
    `es_meta(estado)` y `costo(estado, accion)`.
  - `ProblemaHorario`: implementación concreta; sus `sucesores` solo producen
    estados que cumplen las restricciones duras.
- **`algoritmos`** implementan las estrategias de búsqueda consumiendo
  únicamente la interfaz de `Problema` (no conocen los detalles del horario).
  Cada algoritmo devuelve un `Resultado` con la solución (si existe), el
  número de nodos explorados y el tiempo.
- **`gui`** (tkinter) solo carga archivos, llama a un algoritmo y muestra el
  resultado; no contiene lógica de búsqueda.
- **`datos`** contiene los archivos `.txt` cuyo formato está definido en
  [docs/formato_datos.md](docs/formato_datos.md).
- **`pruebas`** contiene las pruebas con `unittest` de todos los módulos.

## Restricciones del enunciado

- Lenguaje permitido: **solo Python**.
- **No se permite usar bibliotecas externas.** Los algoritmos se implementan
  desde cero.
- La interfaz gráfica se hace con **tkinter** (biblioteca estándar de Python).
- El código debe estar **documentado** y **estructurado en clases o módulos
  separados**.

## Flujo de trabajo con Git

- La rama `main` está protegida: los cambios entran únicamente mediante
  **pull request**, y cada PR debe ser revisado por el otro integrante
  antes de hacer merge.
- Cada issue se trabaja en una rama propia con el nombre
  `feature/<numero>-<tema>` (por ejemplo `feature/1-contrato-estado-problema`).
- Un PR solo se aprueba si todas las pruebas pasan:

  ```bash
  python -m unittest discover -s pruebas -t . -v
  ```
