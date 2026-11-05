# Contraste A/C ejecutado

| Brazo | Panel | Objetivo activo | Ambas asociaciones | Corregida | Preservada |
|---|---|---:|---:|---:|---:|
| A-17 | contaminated_pair | 79.69% | 63.54% | 75.00% | 84.38% |
| A-17 | layout | 82.29% | 64.06% | 78.12% | 86.46% |
| A-17 | surface | 79.69% | 64.06% | 75.00% | 84.38% |
| A-17 | clean | 91.67% | 81.25% | 83.33% | 100.00% |
| A-17 | focus_change | 82.29% | 63.54% | 75.00% | 89.58% |
| C-17 | contaminated_pair | 85.42% | 66.67% | 87.50% | 83.33% |
| C-17 | layout | 86.46% | 69.27% | 87.50% | 85.42% |
| C-17 | surface | 84.90% | 66.15% | 86.46% | 83.33% |
| C-17 | clean | 97.92% | 91.67% | 95.83% | 100.00% |
| C-17 | focus_change | 84.90% | 66.67% | 88.54% | 81.25% |

Ambos parten de los mismos pesos Addressable V1.2 y la misma cabeza inicial, no del C final V1. Receta idéntica a V1: CPU FP32, AdamW0,003, betas0,9/0,95, decay0,01, clipping1, batch8, 300updates; solo C recibe BCE0,1. Checkpoint final fijo, sin selección según dev. Curvas completas, pérdidas y gradientes por update en *-curve.json. La comparación V1/V2 es descriptiva porque cambia la distribución; el contraste causal primario es A/C sobre la distribución nueva.
