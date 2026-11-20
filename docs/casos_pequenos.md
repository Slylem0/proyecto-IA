# Casos pequeños verificables a mano (issue #19)

Casos diminutos para comprobar el sistema a mano: se pueden contar las
soluciones sin escribir código. Cada caso está en
`datos/casos_pequenos/<caso>/` con los cuatro archivos de entrada.

## Resumen

| Caso | Clases | Días | Franjas | Salones | Casillas | Soluciones |
|------|--------|------|---------|---------|----------|------------|
| caso1_trivial | 1 | 1 | 1 | 1 | 1 | 1 |
| caso2_dos_franjas | 2 | 1 | 2 | 1 | 2 | 2 |
| caso3_dos_dias | 2 | 2 | 1 | 1 | 2 | 2 |
| caso4_mismo_grupo | 2 | 1 | 2 | 2 | 4 | 8 |
| caso5_tablero_lleno | 4 | 2 | 2 | 1 | 4 | 24 |
| caso6_al_limite | 3 | 1 | 3 | 1 | 3 | 6 |
| caso7_sin_solucion_profesor | 3 | 1 | 2 | 3 | 6 | 0 |
| caso8_sin_solucion_salon | 3 | 1 | 2 | 1 | 2 | 0 |
| caso9_sin_solucion_grupo | 3 | 1 | 2 | 3 | 6 | 0 |

Casillas = días × franjas × salones, es decir, cuántas clases caben en
total. En los casos sin solución hay menos franjas (o días) que clases
que comparten profesor, salón o grupo.

## Con solución

### caso1_trivial

```
profesores: Prof_A
cursos:     Calculo;Prof_A;G1
salones:    S1
franjas:    dias;Lunes / 07:00-09:00
```

Una sola clase y una sola casilla: **1 solución**, `Calculo` el lunes
de 07:00 a 09:00 en `S1`.

### caso2_dos_franjas

```
profesores: Prof_A
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_A;G2
salones:    S1
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00
```

Las dos clases son del mismo profesor y hay dos franjas: una en cada
franja (2 órdenes) → **2 soluciones**.

### caso3_dos_dias

```
profesores: Prof_A
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_A;G2
salones:    S1
franjas:    dias;Lunes;Martes / 07:00-09:00
```

Igual que el caso 2, pero el espacio extra está en los días: las clases
van en días distintos (2 órdenes) → **2 soluciones**.

### caso4_mismo_grupo

```
profesores: Prof_A / Prof_B
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_B;G1
salones:    S1 / S2
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00
```

El grupo `G1` no puede tener dos clases a la misma hora, así que cada
una va en una franja distinta (2 órdenes). En cada franja el salón es
libre, así que cada clase puede usar `S1` o `S2` (2 × 2). Total:
2 × 2 × 2 = **8 soluciones**.

### caso5_tablero_lleno

```
profesores: Prof_A / Prof_B
cursos:     Calculo;Prof_A;G1 / Algebra;Prof_B;G2
            Fisica;Prof_A;G3 / Quimica;Prof_B;G4
salones:    S1
franjas:    dias;Lunes;Martes / 07:00-09:00 / 09:00-11:00
```

Hay exactamente 4 casillas (2 días × 2 franjas × 1 salón) para 4 clases
con grupos distintos y dos profesores. Como hay un solo salón, las cuatro
casillas corresponden a horarios distintos. Cualquier reparto de las
4 clases es válido: 4! = **24 soluciones**.

### caso6_al_limite

```
profesores: Prof_A
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_A;G2 / Quimica;Prof_A;G3
salones:    S1
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00 / 11:00-13:00
```

Tres clases del mismo profesor y exactamente tres franjas: se llenan
todas y cualquier orden sirve: 3! = **6 soluciones**.

## Sin solución

En los tres casos el problema es de capacidad: hay más clases que
huecos disponibles para un mismo profesor, salón o grupo.

### caso7_sin_solucion_profesor

```
profesores: Prof_A
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_A;G2 / Quimica;Prof_A;G3
salones:    S1 / S2 / S3
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00
```

Las tres clases son del mismo profesor, que solo puede dictar una por
franja. Con 2 franjas caben 2 clases, no 3 → **0 soluciones**. Los tres
salones no ayudan porque el choque es del profesor.

### caso8_sin_solucion_salon

```
profesores: Prof_A / Prof_B / Prof_C
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_B;G2 / Quimica;Prof_C;G3
salones:    S1
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00
```

Hay un solo salón y 2 franjas: caben 2 clases, no 3 → **0 soluciones**.

### caso9_sin_solucion_grupo

```
profesores: Prof_A / Prof_B / Prof_C
cursos:     Calculo;Prof_A;G1 / Fisica;Prof_B;G1 / Quimica;Prof_C;G1
salones:    S1 / S2 / S3
franjas:    dias;Lunes / 07:00-09:00 / 09:00-11:00
```

Las tres clases son del grupo `G1`, que solo puede tener una por
franja: 2 franjas para 3 clases → **0 soluciones**.

## Cómo lo comprueban las pruebas

`pruebas/test_casos_pequenos.py`:

- revisa el tamaño de cada caso (clases, días, franjas y salones);
- cuenta todas las soluciones por fuerza bruta, probando todos los
  repartos posibles y filtrando con `es_solucion_valida`, y compara con
  el número de la tabla;
- comprueba que BFS, costo uniforme, IDDFS y A* dicen "hay" o "no hay"
  de acuerdo con el caso, y que sus soluciones son válidas;
- verifica la solución única del caso 1.

Para probar un caso en la interfaz, carga los cuatro archivos de
`datos/casos_pequenos/<caso>/` y presiona Generar Horario.
