# Resultados completos

|Condición|Aux train|CE|Respuesta original|Aux layout nuevo|Respuesta layout|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|A|45.59%|1.2182|99.22%|40.90%|67.50%|22.0|
|B|56.48%|1.0504|28.91%|51.21%|30.00%|22.0|
|C|54.26%|1.0540|41.09%|30.43%|25.62%|26.5|
|D|52.38%|1.0484|25.00%|38.28%|25.00%|24.8|

Curvas150updates por brazo, índices muestreados y normas por tensor: *-curves.json. Checkpoints incluyen modelo, decoder, AdamW, RNG y cursor1200. Predicciones, confusión4×4 y contadores entidad/valor en *-evaluation.json. Umbral ≥90% y CE<.5 aplicado únicamente al auxiliar; no equivale a competencia del lector original. No se habilitan brazos600.
