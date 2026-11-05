# Decisión Trapos V2

Piloto semilla17: **FAIL**. Compuertas incumplidas: ['advantage-confirmed', 'advantage-random', 'contaminated_pair-answer', 'contaminated_pair-correction', 'contaminated_pair-current', 'contaminated_pair-invalid', 'contaminated_pair-joint', 'contaminated_pair-obsolete', 'contaminated_pair-precision', 'contaminated_pair-preservation', 'focus_change-answer', 'focus_change-correction', 'focus_change-current', 'focus_change-invalid', 'focus_change-joint', 'focus_change-obsolete', 'focus_change-precision', 'focus_change-preservation', 'layout-answer', 'layout-correction', 'layout-current', 'layout-invalid', 'layout-joint', 'layout-obsolete', 'layout-precision', 'layout-preservation', 'surface-answer', 'surface-correction', 'surface-current', 'surface-invalid', 'surface-joint', 'surface-obsolete', 'surface-precision', 'surface-preservation'].

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

El contrato se corrigió antes de entrenar: ambas entidades pertenecen al ámbito de conservación y las consultas/focos se balancean. V1 mezclaba esa semántica legítima con una composición consulta/posición no entrenada; esto no prueba que aquel fuera el único motivo de fallo. A/C distingue entrenamiento con o sin filtro bajo el mismo contrato nuevo; la señal BCE adicional sigue siendo una diferencia declarada.

Si falla alguna compuerta, Trapos V2 se congela: no se ejecutan semillas29/43, no se buscan lambdas, tamaños o arquitecturas. Hielo Addressable conserva su evidencia independiente. Puede continuar el desarrollo lingüístico mediante una ruta determinista/sintáctica explícita, con Trapos desactivado y conservación/restablecimiento documentados; esta alternativa no certifica que detectar acontecimientos en lenguaje libre esté resuelto. No se inicia pretraining ni se levantan sus compuertas de datos y entrenador.

Si el piloto pasa, las confirmaciones29/43 usan la misma receta. Aun así, el resultado sería selección aprendida en un DSL, no comprensión lingüística ni aislamiento térmico completo. La heurística de conjunción es una solución exacta disponible por definición, y nunca debe presentarse el aprendizaje de ese DSL como superioridad sobre ella.

## Resultado medido y decisión estratégica cerrada

C alcanza85,42% de respuesta base frente79,69% de A (+5,73pp), pero ambas asociaciones solo66,67% frente63,54%. C tiene precisión60,09%, recall97,22% y ejecuta97,08% de escrituras: no aprendió la selección requerida. Acepta54/54 negaciones confirmadas y219/220 propuestas fuera de ámbito, además de perder13/192 correcciones válidas.

En el MISMO C, forzar todo mejora a87,50%; la regla confirmado-no-negado y el oráculo alcanzan100%. La mejora C/A no es evidencia del beneficio causal de las decisiones aprendidas: la pérdida BCE también cambia las representaciones compartidas y el entrenamiento. La intervención sobre decisiones, limitada al mismo checkpoint/distribución, no favorece la política aprendida. No se aisló una causa única de fallo de optimización.

El oráculo100% acredita que la ruta funcional de ese checkpoint puede resolver las consultas base cuando se selecciona correctamente; no demuestra robustez universal ni que cada escritura individual sea perfecta. El fracaso de la política persiste bajo la semántica coherente de conservación y consulta; no puede atribuirse únicamente al error de consulta V1. La cobertura condicional incompleta restante limita conclusiones más amplias y queda publicada sin ocultarla.

**Se congela Trapos V2, sin semillas29/43 ni transición a lenguaje natural como filtro aprendido.** Se conserva Hielo Addressable y se separa la investigación del filtro del desarrollo lingüístico. FALLBACK_CONFIG.json prepara la alternativa con escritura sintáctica/determinista original y Trapos desactivado. No declara detección de acontecimientos lingüísticos ni autoriza pretraining; datos, tokenizer, coste y entrenador deben cerrar sus compuertas independientes.
