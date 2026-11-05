# Recuperación y controles de política

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

| Panel | Política sobre mismo C | Respuesta normal |
|---|---|---:|
| clean | C-17 all | 100.00% |
| clean | C-17 confirmed | 100.00% |
| clean | C-17 confirmed_nonnegated | 100.00% |
| clean | C-17 goal | 100.00% |
| clean | C-17 oracle | 100.00% |
| clean | C-17 random | 98.44% |
| contaminated_pair | C-17 all | 87.50% |
| contaminated_pair | C-17 confirmed | 94.79% |
| contaminated_pair | C-17 confirmed_nonnegated | 100.00% |
| contaminated_pair | C-17 goal | 88.02% |
| contaminated_pair | C-17 oracle | 100.00% |
| contaminated_pair | C-17 random | 86.46% |
| focus_change | C-17 all | 87.50% |
| focus_change | C-17 confirmed | 99.48% |
| focus_change | C-17 confirmed_nonnegated | 100.00% |
| focus_change | C-17 goal | 88.02% |
| focus_change | C-17 oracle | 100.00% |
| focus_change | C-17 random | 86.98% |
| layout | C-17 all | 88.02% |
| layout | C-17 confirmed | 94.79% |
| layout | C-17 confirmed_nonnegated | 100.00% |
| layout | C-17 goal | 88.02% |
| layout | C-17 oracle | 100.00% |
| layout | C-17 random | 84.38% |
| surface | C-17 all | 87.50% |
| surface | C-17 confirmed | 94.27% |
| surface | C-17 confirmed_nonnegated | 99.48% |
| surface | C-17 goal | 88.02% |
| surface | C-17 oracle | 100.00% |
| surface | C-17 random | 85.42% |

Las intervenciones usan los mismos pesos C: todo, confirmación, pertenencia al ámbito, confirmado-no-negado, aleatorio y oráculo. No son nuevas trayectorias entrenadas ni un ranking imparcial de recetas. La tasa aleatoria proviene solo de TRAIN final, guardada en C-17-calibration.json. La conjunción determinista coincide con el oráculo por definición del DSL; no puede exigirse superarla ni llamarse selección semántica por imitarla.

Reset y swap compatibles se guardan en cada métricas. Los swaps conservan entidades, estructura y ámbito, cambiando valor vigente; siguen siendo diagnósticos de distribución limitada. La ventana visible final no contiene las propuestas: Hielo es la vía de prefijo, sin KV cache extra. Ambas consultas declaran su foco antes de leer y conservan etiquetas de escritura iguales. No se atribuye automáticamente una diferencia de exactitud conjunta a escritura o filtro.
