# Contrafactuales

Cada swap requiere cuatro respuestas correctas: ambas consultas del relato original y ambas del relato con valores intercambiados. Dos pares estrictos en C, uno por orden. No basta cambiar arbitrariamente la predicción.

| Brazo | Update | Orden original | Inverso | Conjunta mixta | CE | Swaps estrictos |
|---|---:|---:|---:|---:|---:|---:|
| direct | 300 | 50.00% | 50.00% | 0.00% | 0.693175 | 0/2 |
| direct | 700 | 50.00% | 50.00% | 0.00% | 0.693149 | 0/2 |
| curriculum | 300 | 100.00% | 0.00% | 50.00% | 4.959621 | 1/2 |
| curriculum | 700 | 100.00% | 100.00% | 100.00% | 0.000001 | 2/2 |

Logits completos, probabilidades y etiquetas/inputs originales guardados para cada panel en updates0/300/700. El campo same_answer_stories registra colapso entre consultas. No se declara éxito a partir de diferencias de atención o representaciones.
