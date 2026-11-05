# Capacidad real

Foreground actual: 299520 parámetros asignados, 296160 entrenables; 3360 de la ruta Hielo permanecen congelados e inactivos. Dos bloques causales width32, cuatro cabezas Q / dos KV, dimensión por cabeza8, RoPE sin posiciones aprendidas; MLP gated SiLU inner128 por bloque. Refinamiento rápido residual normalizado repetido dos veces, sin nueva atención ni estado temporal. Ventana piloto128, reset por ventana; los estudios de binding usaban119 IDs válidos y padding128. No hay KV cache ni persistencia oculta.

| Componente | Parámetros |
|---|---:|
| Embedding y salida compartida | 262144 |
| Q/K/V/O dos bloques | 6144 |
| MLP dos bloques | 24576 |
| Refinamiento rápido | 3104 |
| Normalizaciones activas | 192 |
| Memoria inactiva | 3360 |

Embedding = 88.51% de los parámetros activos (87.52% del total). La cabeza es F.linear(hidden, emb.weight), sin bias ni una segunda matriz vocabulario×width. Quedan **34016 parámetros entrenables no embedding**; atención+MLP apenas30720. No se deduce imposibilidad de aprender, pero este reparto no es una base convincente para generalización lingüística amplia. La fracción de vocabulario es un diagnóstico de presupuesto, no una causa aislada demostrada.

Baseline disponible: vendor.cryo_historical.Baseline(v8192,d32,layers2,dropout0), 293024 activos, atención/MLP iguales, sin refinamiento rápido. Inicialización propia ya existente con escalado residual; no es idéntica a la del foreground. Diferencia3136 parámetros activos y receta de inicialización: contraste de referencia, no ablación causal perfecta. No se modificó ninguno.

Inventario tensor por tensor en results/capacity.json. Piloto: RSS high-water del proceso773MiB aproximadamente; temporales de logits8192×128 dominan más que 1,2MiB de pesos FP32. RAM observada no es pico independiente por brazo ni predicción para modelos mayores. Velocidades en CPU_LANGUAGE_PILOT.md.
