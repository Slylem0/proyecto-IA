# Formato de los archivos de datos

Este documento define el formato de los archivos que alimenta el sistema:
`profesores.txt`, `cursos.txt`, `salones.txt` y `franjas.txt`.
El programa que lee y valida estos archivos se implementara despues
(lectura y validacion de archivos); aqui solo se define el formato.

## Reglas generales

- Codificacion: UTF-8.
- Separador de campos: `;` (punto y coma). Los campos no pueden contener `;`.
- Las lineas vacias se ignoran.
- Las lineas que empiezan con `#` son comentarios y se ignoran.
- Se permiten espacios al inicio y al final de cada campo; se recortan al leer.
- Los nombres distinguen mayusculas de minusculas (`S101` es distinto de `s101`).
- Ningun campo puede quedar vacio.

Casos invalidos comunes a todos los archivos:

- Una linea con menos o mas campos de los que le corresponden.
- Un campo vacio (por ejemplo `Calculo;;G1` o `;Prof_A`).
- Dos lineas con el mismo identificador (nombre repetido).

## profesores.txt

Un profesor por linea, con un solo campo:

```
nombre
```

- **Campos obligatorios:** `nombre`.
- **Restricciones:** el nombre no puede repetirse.

Ejemplo:

```
Prof_A
Prof_B
```

## cursos.txt

Una clase por linea, con tres campos:

```
materia;profesor;grupo
```

- **Campos obligatorios:** `materia`, `profesor`, `grupo`.
- **Restricciones:**
  - El `profesor` debe existir en `profesores.txt`.
  - La combinacion `materia + profesor + grupo` no puede repetirse
    (cada clase se asigna exactamente una vez).

Ejemplo:

```
Calculo;Prof_A;G1
Algebra;Prof_A;G2
```

> **Nota:** el enunciado deja pendiente decidir en que archivo se declara
> el grupo de estudiantes de cada clase. Por ahora se incluye aqui
> como tercer campo; si se decide mover a otro archivo, este formato
> se actualizara.

## salones.txt

Un salon por linea, con un solo campo:

```
nombre
```

- **Campos obligatorios:** `nombre`.
- **Restricciones:** el nombre no puede repetirse.

Ejemplo:

```
S101
S102
```

## franjas.txt

Una franja horaria por linea, con un solo campo:

```
hh:mm-hh:mm
```

- **Campos obligatorios:** la franja en formato `hh:mm-hh:mm`,
  con dos digitos para la hora y dos para los minutos
  (por ejemplo `07:00-09:00`, no `7:00-9:00`).
- **Restricciones:**
  - La hora de fin debe ser mayor que la de inicio.
  - Las franjas deben listarse en orden ascendente.

Ejemplo:

```
07:00-09:00
09:00-11:00
```

> **Nota:** el enunciado deja pendiente definir donde se declaran los
> dias (semana) y como se combinan con las franjas. Esa decision
> completara este formato mas adelante.

## Resumen

| Archivo         | Separador | Campos                      | Unicidad                          |
|-----------------|-----------|-----------------------------|-----------------------------------|
| profesores.txt  | (ninguno) | `nombre`                    | nombre                            |
| cursos.txt      | `;`       | `materia;profesor;grupo`    | materia + profesor + grupo        |
| salones.txt     | (ninguno) | `nombre`                    | nombre                            |
| franjas.txt     | (ninguno) | `hh:mm-hh:mm`               | franja (y orden ascendente)       |
