# Protocolo congelado

`protocol.json` y `results/FREEZE.json` preceden al primer entrenamiento. Semilla inicial 17; solo si supera todas las compuertas se permiten B/C 29 y 43. 300 updates por brazo, batch 8, CPU FP32, un thread, AdamW LR 0,003, betas (0,9;0,95), decay 0,01, clipping 1. Checkpoint final update 300; sin selección por dev, búsqueda ni prolongación.

**Diferencia declarada con V1.1:** antes se usaba CE de respuesta + 0,1 CE auxiliar inicial. La instrucción V1.2 exige únicamente respuesta, por lo que B y C usan exactamente CE del siguiente token de respuesta al final. B reproduce la distribución anterior, no el objetivo completo histórico. No atribuir diferencias frente a porcentajes publicados de V1.1 solo a datos. La comparación causal primaria es B frente a C dentro de esta ejecución.

El decoder auxiliar se crea idéntico, se congela, queda fuera de AdamW y no se usa en loss ni inferencia. No se añaden parámetros al modelo ni pérdidas. Cada brazo recibe 2.400 respuestas, cero targets auxiliares y 153.600 IDs. Misma arquitectura, inicialización, índices base y variantes por semilla; C transforma pares/layouts/distractores. Los cambios de distribución están agrupados: el contraste no identifica por separado cuál contribuye.

Compuertas en held_pair, new_layout, alternate y held_distractor: corregida y preservada ≥95%, ambas consultas correctas ≥90%, contrafactuales obsoleto/vigente ≥95%. Formación en par reservado ≥90%, intercambio ≥95%, caída conjunta ≤5 puntos frente a B en familias previstas. Son criterios prospectivos de ingeniería; no pruebas estadísticas. No cambiar umbrales tras observar resultados.

Se conservó el modo eval de la receta histórica durante updates (dropout=0; autograd activo). La causalidad también se comprobó expresamente en train. No transferir este resultado a dropout, CUDA, BF16 o entrenamiento de lenguaje.
