# Generalización separada

|Brazo|Evaluación independiente|Accuracy|Conjunta|Intercambios|
|---|---|---:|---:|---:|
|A|dev-layouts|25.00%|0.00%|0/1|
|A|dev-new-entity-pair|75.00%|50.00%|0/1|
|A|dev-opposite-order|0.00%|0.00%|0/1|
|B|dev-layouts|25.00%|0.00%|0/6|
|B|dev-new-entity-pair|50.00%|25.00%|0/6|
|B|dev-opposite-order|8.33%|0.00%|0/6|
|C|dev-layouts|50.00%|0.00%|0/2|
|C|dev-new-entity-pair|50.00%|0.00%|0/2|
|D|dev-layouts|33.33%|0.00%|0/12|
|D|dev-new-entity-pair|25.00%|8.33%|0/12|

A pasa train pero obtiene0% en orden opuesto y25% en layout verbal alternativo; B obtiene8,33% y25%, respectivamente. No hay generalización estructural certificada. El nuevo par contiene una entidad no entrenada: no es prueba pura de combinación de entidades familiares. Ningún brazo logra un intercambio estricto en esos devs.

A sobreajusta el fixture; C y D fallan ya en ajuste. B tiene ambas limitaciones: ajuste parcial y deterioro fuera de orden. El mismo límite de contexto mantiene visibles ambos hechos; no se evalúa memoria. No se presenta este resultado como comprensión lingüística general ni como control positivo de memoria.
