# Coste CPU

| Brazo | Train s | ms/update | Parámetros modelo | Entrenables | RSS pico proceso KiB |
|---|---:|---:|---:|---:|---:|
| A-17 | 40.144 | 133.812 | 292612 | 284096 | 1058668 |
| B-17 | 44.619 | 148.729 | 292612 | 284096 | 1058668 |
| C-17 | 46.571 | 155.237 | 292612 | 284641 | 812104 |
| D-17 | 44.710 | 149.033 | 292612 | 284096 | 1063796 |

La cabeza nueva tiene 545 parámetros. Todos los brazos la instancian; solo C los entrena. Los pesos de inferencia existentes no aumentan de dimensión. Cada brazo consume 2.400 respuestas y 230.400 IDs. C añade 12.000 etiquetas BCE de aceptación.

Se mide tiempo completo de update, sin evaluación ni carga inicial. No se aisló un coste de filtro por sustracción entre brazos: sería confundir diferencias de backward/loss. El microbenchmark congelado, si se ejecuta, queda separado en policy-timing.json.

Las escrituras rechazadas se omiten **lógicamente en H**, pero la implementación sigue calculando key, value y el producto exterior candidato; **no ahorra esas operaciones**. No se declara reducción de FLOPs ni aceleración CUDA. La tasa de escritura no equivale a ahorro de cómputo. La prioridad de V1 es selección funcional verificable.

Microbenchmark ejecutado: 0.9188 ms para las 24 llamadas de cabeza de un forward batch8, 200 repeticiones, CPU sin gradientes. No incluye backward, extracción ni escritura y no es un ahorro end-to-end.
