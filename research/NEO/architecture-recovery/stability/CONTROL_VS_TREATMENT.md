# Comparación funcional B/C

Todos los porcentajes siguientes son respuestas normales, sin decoder auxiliar. Exactitud conjunta exige dos consultas a la misma secuencia, una por entidad, ambas correctas. No es el producto de marginales.

| Brazo | Familia | Corregida | Preservada | Ambas consultas |
|---|---|---:|---:|---:|
| B-17 | held_pair | 100.00% | 28.65% | 28.39% |
| B-17 | held_formation | — | — | 25.00% |
| B-17 | new_layout | 100.00% | 100.00% | 100.00% |
| B-17 | alternate | 100.00% | 100.00% | 100.00% |
| B-17 | held_distractor | 100.00% | 29.69% | 29.69% |
| B-29 | held_pair | 100.00% | 100.00% | 100.00% |
| B-29 | held_formation | — | — | 100.00% |
| B-29 | new_layout | 100.00% | 100.00% | 100.00% |
| B-29 | alternate | 100.00% | 95.00% | 95.00% |
| B-29 | held_distractor | 100.00% | 100.00% | 100.00% |
| B-43 | held_pair | 100.00% | 100.00% | 100.00% |
| B-43 | held_formation | — | — | 100.00% |
| B-43 | new_layout | 100.00% | 100.00% | 100.00% |
| B-43 | alternate | 100.00% | 90.00% | 90.00% |
| B-43 | held_distractor | 100.00% | 100.00% | 100.00% |
| C-17 | held_pair | 100.00% | 100.00% | 100.00% |
| C-17 | held_formation | — | — | 100.00% |
| C-17 | new_layout | 100.00% | 100.00% | 100.00% |
| C-17 | alternate | 100.00% | 100.00% | 100.00% |
| C-17 | held_distractor | 100.00% | 100.00% | 100.00% |
| C-29 | held_pair | 100.00% | 100.00% | 100.00% |
| C-29 | held_formation | — | — | 100.00% |
| C-29 | new_layout | 100.00% | 100.00% | 100.00% |
| C-29 | alternate | 100.00% | 99.38% | 99.69% |
| C-29 | held_distractor | 100.00% | 100.00% | 97.92% |
| C-43 | held_pair | 100.00% | 100.00% | 100.00% |
| C-43 | held_formation | — | — | 100.00% |
| C-43 | new_layout | 100.00% | 100.00% | 100.00% |
| C-43 | alternate | 100.00% | 100.00% | 100.00% |
| C-43 | held_distractor | 100.00% | 100.00% | 100.00% |

Curvas, CE, gradientes por tensor, coste y exactitud sobre exposición train se conservan sin selección de ejemplos. Dos consultas requieren dos forwards de evaluación; no cambian supervisión de entrenamiento. Las familias comparten símbolos y algunas estructuras: no tratar sus filas como réplicas estadísticas independientes.
