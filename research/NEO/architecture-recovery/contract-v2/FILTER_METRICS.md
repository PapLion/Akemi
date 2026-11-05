# Filtración por separado

| Brazo | Panel | Precisión | Recall | FPR | Escrituras lógicas |
|---|---|---:|---:|---:|---:|
| A-17 | contaminated_pair | 60.00% | 100.00% | 100.00% | 100.00% |
| A-17 | layout | 60.00% | 100.00% | 100.00% | 100.00% |
| A-17 | surface | 60.00% | 100.00% | 100.00% | 100.00% |
| A-17 | clean | 100.00% | 100.00% | 0.00% | 100.00% |
| A-17 | focus_change | 60.00% | 100.00% | 100.00% | 100.00% |
| C-17 | contaminated_pair | 60.09% | 97.22% | 96.88% | 97.08% |
| C-17 | layout | 59.81% | 96.88% | 97.66% | 97.19% |
| C-17 | surface | 60.02% | 97.22% | 97.14% | 97.19% |
| C-17 | clean | 100.00% | 97.92% | 0.00% | 97.92% |
| C-17 | focus_change | 60.09% | 97.22% | 96.88% | 97.08% |

TP/FP/FN/TN, errores por tipo y cambios reales de Hielo en *-metrics.json. C-17-filter-decisions.json conserva score, decisión, factores y posición por propuesta. final-integrity.json compara decisiones con reglas simples. El extractor es byte-idéntico V1 y entrega todos los candidatos independientemente de la validez; un rechazo deja Hielo exactamente igual. No se confunde aceptar una corrección con rechazar contradicciones.
