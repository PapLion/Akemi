# Resultados

| Brazo | Update | Orden original | Inverso | Conjunta mixta | CE | Swaps estrictos |
|---|---:|---:|---:|---:|---:|---:|
| direct | 300 | 50.00% | 50.00% | 0.00% | 0.693175 | 0/2 |
| direct | 700 | 50.00% | 50.00% | 0.00% | 0.693149 | 0/2 |
| curriculum | 300 | 100.00% | 0.00% | 50.00% | 4.959621 | 1/2 |
| curriculum | 700 | 100.00% | 100.00% | 100.00% | 0.000001 | 2/2 |

Resultados completos y logits8192 en results, curvas cada50 updates. A300 y C300 reproducen exactamente pesos, AdamW y RNG Torch de los checkpoints históricos correspondientes (audit.json). La diferencia posterior corresponde a trayectorias previas distintas bajo batches finales idénticos. Una semilla no establece superioridad poblacional.

El currículo sí desbloquea el ajuste de las ocho respuestas: 100% simultáneo en ambos órdenes y 2/2 intercambios, mientras el directo700 sigue al azar. La trayectoria A300→C400 facilita aprender este fixture; no se limita a conservar el orden original. No hay evidencia de binding composicional general: ambos devs quedan en 50% marginal, 25% conjunta y 0% swaps. Este es un éxito parcial de entrenamiento y un fallo de la compuerta externa.
