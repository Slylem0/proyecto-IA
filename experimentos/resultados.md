# Comparacion de algoritmos (issue #20)

Limite por corrida: 60 s. Celda: nodos explorados / tiempo (s) / costo.

| Caso | Tamano | BFS | Costo uniforme | IDDFS | A* | A* (h simple) |
|---|---|---|---|---|---|---|
| caso1 | 4 clases, 2 dias x 2 franjas x 2 salones = 8 | 66 / 0.002 / 8 | 257 / 0.018 / 4 | 433 / 0.002 / 8 | 4 / 0.000 / 4 | 4 / 0.000 / 4 |
| caso2 | 5 clases, 2 dias x 2 franjas x 2 salones = 8 | 354 / 0.015 / 8 | 1345 / 0.046 / 6 | 1795 / 0.008 / 8 | 35 / 0.002 / 6 | 545 / 0.029 / 6 |
| caso3 | 6 clases, 2 dias x 2 franjas x 2 salones = 8 | 1362 / 0.041 / 9 | 3345 / 0.112 / 8 | 5269 / 0.039 / 9 | 67 / 0.004 / 8 | 1857 / 0.078 / 8 |
| caso4 | 7 clases, 3 dias x 2 franjas x 2 salones = 12 | 82346 / 6.327 / 8 | no termina | 580827 / 4.869 / 8 | 7 / 0.001 / 7 | 7 / 0.001 / 7 |
| caso5 | 8 clases, 3 dias x 3 franjas x 2 salones = 18 | no termina | no termina | no termina | 8 / 0.001 / 8 | 8 / 0.001 / 8 |
| caso6 | 15 clases, 5 dias x 3 franjas x 3 salones = 45 | no termina | no termina | no termina | 15 / 0.012 / 15 | 15 / 0.007 / 15 |
| caso7 | 30 clases, 5 dias x 4 franjas x 5 salones = 100 | no termina | no termina | no termina | 30 / 0.066 / 30 | 30 / 0.031 / 30 |
| caso8 | 8 clases, 3 dias x 3 franjas x 2 salones = 18 | no termina | no termina | no termina | no termina | no termina |
