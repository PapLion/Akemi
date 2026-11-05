# Checkpoint V1 inmutable, antes de entrenar V2

| Panel | V1 respuesta | V1 conjunta | Precisión | Recall |
|---|---:|---:|---:|---:|
| contaminated_pair | 95.31% | 89.06% | 77.84% | 100.00% |
| layout | 95.31% | 90.62% | 77.84% | 100.00% |
| surface | 95.31% | 89.06% | 77.84% | 100.00% |
| clean | 100.00% | 100.00% | 100.00% | 100.00% |
| focus_change | 100.00% | 89.06% | 77.84% | 100.00% |

Hash y coincidencia con heurística de confirmación en V1-checkpoint-diagnostic.json. Falsos positivos desglosados por negación/fuera de ámbito y otros tipos en V1-frozen-on-V2-metrics.json; predicciones por registro conservadas. Se midieron foco cambiado, conservación, layouts y contrafactuales sin actualizar pesos. El cambio de foco es dentro de un ámbito conservado, no una consulta a información previamente excluida.
