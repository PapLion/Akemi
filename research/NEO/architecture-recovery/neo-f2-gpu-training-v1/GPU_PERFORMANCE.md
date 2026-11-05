# Rendimiento observado

| Modelo | Parámetros | Targets/s updates | Segundos updates | Wall reportado | Pico alloc entrenamiento MiB |
|---|---:|---:|---:|---:|---:|
| F2 | 2082176 | 4083.95 | 1205.31 | 1436.09 | no certificado |
| Transformer | 2032768 | 4315.55 | 1140.63 | 1200.89 | 124.55 |

Targets/s de updates excluye tokenización, batch transfer, evaluación, checkpoint y arranque. Para baseline, wall del worker empieza tras evaluación inicial e incluye evaluaciones intermedias/final y generación. Para F2, wall se reconstruyó desde el nacimiento del log (precisión de un segundo), excluyendo la evaluación inicial e incluyendo la pausa de reparación y reevaluación. La memoria F2 del summary es de la finalización, no un pico certificado de entrenamiento; las muestras por update y nvidia-smi quedan conservadas. No se equiparan esos contadores entre modelos. Tiempo total de alquiler separado en COST_REPORT. Telemetría periódica nvidia-smi en results/*-monitor.jsonl, memoria del proceso en summaries. Bajo uso de GPU no se atribuye automáticamente a una causa; código eager, batch 2 y bucle de posiciones existentes sin optimización en esta ejecución. No se presenta como rendimiento GPU óptimo. FLOPs densos6P orientativos: F2≈12,49M/target; baseline≈12,20M, excluyendo coste cuadrático de atención y distinciones lookup/proyección compartida.

## Diagnósticos observados de optimización

| Modelo | Norma gradiente mediana | Máxima registrada | Updates con clipping | RAM pico del proceso reportado MiB |
|---|---:|---:|---:|---:|
| F2 | 1.7858 | 663.8554 | 91.57% | 1365.38 |
| Transformer | 1.3752 | 10.2089 | 85.89% | 1510.38 |

La RAM F2 es del proceso de finalización, no un pico recuperado del proceso original de entrenamiento. F2 alcanzó 530 MiB y baseline 528 MiB en muestras nvidia-smi; son muestras del dispositivo, no picos certificados del allocator. Las medias de utilización incluyen evaluaciones y pausas de exportación/reparación; no representan utilización sostenida de kernels. Los gradientes se comprobaron finitos en cada update. El clipping frecuente y la diferencia de normas motivan revisar la receta de forma aislada en un estudio posterior, pero no prueban por sí solos la causa de la diferencia de NLL. No se alteró la receta aquí.
