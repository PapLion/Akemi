# Smoke tests lingüísticos ejecutados

Protocolo fijado en protocol.json antes de entrenar: tres brazos, semilla17,64updates, batch2, ventanas128, chunk16, FP32CPU, un thread; AdamW .003, betas(.9,.95), decay.01, clipping1. Checkpoint final fijo, sin selección por dev. Cada brazo recibe idéntico orden y12.537 targets; pérdidas solo siguiente token, sin pérdida auxiliar.

| Brazo | Parámetros activos | NLL train real inicial → final | NLL dev real inicial → final | Targets/s | Tiempo 64 updates |
|---|---:|---:|---:|---:|---:|
| no_ice | 280,736 | 8.9912 → 5.9867 | 8.9776 → 7.2575 | 2013.9 | 6.225s |
| ice | 284,096 | 8.9912 → 5.9912 | 8.9776 → 7.1039 | 1838.3 | 6.820s |
| transformer | 277,600 | 8.9901 → 6.0290 | 8.9732 → 8.0506 | 3490.7 | 3.592s |


El promedio real pondera targets y separa los relatos sintéticos; results/smoke-*.json conserva NLL/PPL por ES/EN/dominio y cada update/gradiente. ES dev conversación solo273 targets y EN código1251 dominan métricas distintas: el agregado no basta. Hielo obtiene NLL dev real7.1039 vs7.2575 sin Hielo, pero una semilla/panel mínimo no permite atribuir una ventaja general ni retención selectiva. Transformer no es B0 histórico certificado: bloque convencional del mismo origen, menos parámetros activos y mayor visibilidad; se etiqueta explícitamente.

Las seis generaciones fijadas (2prompts×3brazos) resultan en24puntos cada una. Se registran IDs, byteshex, SHA y validez UTF8; todas válidas en esta ejecución. La ruta de generación está operativa, la generación lingüística sigue siendo incoherente/repetitiva. Pérdida menor no acredita entendimiento ni utilidad de Hielo. No se extendieron updates ni se eligieron muestras favorables.
