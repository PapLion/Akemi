# Resultados funcionales

| Brazo | Familia | Respuesta normal | Ambas consultas | Corregida | Preservada |
|---|---|---:|---:|---:|---:|
| A-17 | contaminated_pair | 100.00% | 79.69% | 100.00% | 100.00% |
| A-17 | layout | 100.00% | 81.77% | 100.00% | 100.00% |
| A-17 | surface | 100.00% | 79.69% | 100.00% | 100.00% |
| A-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |
| B-17 | contaminated_pair | 78.65% | 47.40% | 70.83% | 86.46% |
| B-17 | layout | 73.44% | 46.35% | 67.71% | 79.17% |
| B-17 | surface | 79.17% | 48.44% | 69.79% | 88.54% |
| B-17 | clean | 88.54% | 57.29% | 77.08% | 100.00% |
| C-17 | contaminated_pair | 100.00% | 76.56% | 100.00% | 100.00% |
| C-17 | layout | 100.00% | 75.00% | 100.00% | 100.00% |
| C-17 | surface | 100.00% | 76.56% | 100.00% | 100.00% |
| C-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | contaminated_pair | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | layout | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | surface | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |

Curvas completas y pérdidas separadas en *-curve.json. Una exactitud de selección alta no sustituye exactitud de respuesta. D utiliza supervisión oracular en inferencia y no cuenta como modelo autónomo. El checkpoint evaluado es siempre update300; no hubo selección de mejor dev.


## Alcance de las consultas emparejadas

El entrenamiento consulta siempre la primera entidad del encabezado de objetivo. La segunda consulta de evaluación conserva ese encabezado y cambia solo el token de consulta: introduce una composición consulta/posición de objetivo no entrenada. Por tanto, la exactitud conjunta combina conservación y generalización de lectura; sus fallos no aíslan interferencia ni selección. Se conserva este resultado y no se reentrena para corregirlo. La respuesta normal al 100% tampoco acredita ambas asociaciones.
