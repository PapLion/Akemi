# Contrafactuales e intervención del estado

Evaluación exploratoria posterior al primer ensayo; BENCHMARK_PROTOCOL.md.224pares por brazo/semilla. La edición mueve la combinación consultada al soporte train: su exactitud aislada no mide generalización composicional independiente. Se exige acertar ambos miembros.

| Brazo | Ambos correctos % | Predicción cambia % | Exactitud editado % |
|---|---:|---:|---:|
| b0_local | 0.00 | 0.00 | 23.96 |
| b0_full | 0.00 | 0.74 | 17.56 |
| cryo_history | 55.65 | 68.60 | 70.83 |
| event | 0.00 | 0.15 | 20.83 |
| delta | 0.00 | 0.74 | 19.35 |
| event_no_memory | 0.00 | 0.00 | 23.96 |
| event_no_filter | 0.00 | 0.15 | 20.83 |
| event_always_write | 0.00 | 0.00 | 20.98 |
| event_no_persist | 0.00 | 0.00 | 23.96 |
| delta_no_persist | 0.00 | 0.00 | 23.96 |

## Event: intervenciones de inferencia

| Modo | Exactitud % | NLL | Cambio frente a soft % | Slots ejecutados/elegibles |
|---|---:|---:|---:|---|
| soft | 0.00 | 5.454 | 0.00 | 21504/21504 |
| hard_0.5 | 0.00 | 5.386 | 42.11 | 7696/21504 |
| no_persist_inference | 0.00 | 6.078 | 49.26 | 21504/21504 |

Una intervención de inferencia no sustituye la ablación entrenada. Ningún modoEvent resuelve este dev. Hard omite candidatos reales pero cambia la función; no acredita selección o ahorro aprendido. Velocidad del salto: PERFORMANCE.md.

## Compuertas descriptivas

| Modelo | Relevantes: write medio | Otros: write medio |
|---|---:|---:|
| event | 0.5117 | 0.4860 |
| delta | 0.5556 | 0.5375 |

Descripciones por semilla; no inferencia causal de relevancia. La clasificación de fragmentos relevantes usa el oráculoDSL, no un anotador humano ni supervisión adicional de gates. Su valor no demuestra que almacenen el hecho correcto.
