# Comportamiento del filtro

| Brazo | Familia | Precisión | Recall | Escrituras lógicas |
|---|---|---:|---:|---:|
| A-17 | contaminated_pair | 60.00% | 100.00% | 100.00% |
| A-17 | layout | 60.00% | 100.00% | 100.00% |
| A-17 | surface | 60.00% | 100.00% | 100.00% |
| A-17 | clean | 100.00% | 100.00% | 100.00% |
| B-17 | contaminated_pair | 58.32% | 73.61% | 75.73% |
| B-17 | layout | 58.74% | 74.65% | 76.25% |
| B-17 | surface | 59.30% | 76.91% | 77.81% |
| B-17 | clean | 100.00% | 76.56% | 76.56% |
| C-17 | contaminated_pair | 75.00% | 100.00% | 80.00% |
| C-17 | layout | 75.00% | 100.00% | 80.00% |
| C-17 | surface | 75.00% | 100.00% | 80.00% |
| C-17 | clean | 100.00% | 100.00% | 100.00% |
| D-17 | contaminated_pair | 100.00% | 100.00% | 60.00% |
| D-17 | layout | 100.00% | 100.00% | 60.00% |
| D-17 | surface | 100.00% | 100.00% | 60.00% |
| D-17 | clean | 100.00% | 100.00% | 100.00% |

Las matrices TP/FP/FN/TN, tasas de error y desglose por tipo de evento se guardan en cada *-metrics.json. La precisión/recall usa decisiones ejecutadas, no únicamente p>0 ni gradientes. El control aleatorio se compara con el presupuesto TRAIN del C final: calibration-*.json. Puede haber diferencias de frecuencia en dev, que se registran; no se recalibra allí.

El override-all usa exactamente los pesos del C entrenado y fuerza todas las escrituras: controla capacidad y entrenamiento compartido al intervenir decisiones. Esto no demuestra que cada neurona sea interpretable ni que el filtro sea general fuera del DSL.

## Diagnóstico de regla superficial

En las 960 decisiones por familia contaminada, las decisiones de C coinciden exactamente (100%) con «aceptar si el bit confirmado está activo», frente al 80% de coincidencia con el oráculo completo. Rechaza hipótesis y citas, pero acepta todas las negaciones confirmadas y afirmaciones fuera del objetivo. Esta equivalencia observada no identifica una neurona causal ni prueba el algoritmo interno; demuestra que el panel no distingue sus decisiones de esa heurística superficial. Evidencia: final-integrity.json y C-17-filter-decisions.json.
