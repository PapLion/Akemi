# Contratos y conservación

Control positivo y contratos pasaron antes de ambos entrenamientos. Reanudación persistida de3+3updates frente a6continuos por condición: exactitud de modelo/decoder/AdamW/RNGTorch/Python/sampler/órdenes; cursor24 al corte, sin acumulación pendiente ni scheduler. Cobertura AdamW exacta, sin parámetros entrenables omitidos o duplicados. Solo CPU FP32 monoproceso/dropout0.

Después se comprueban mismo checkpoint/decoder/optimizador inicial y mismos150batches entre condiciones. Hashes de todos los archivos del estudio previo antes/después, incluidos checkpoints y reportes: sin cambios.

Primer preflight falló porque el arnés reutilizó para la segunda condición una instancia actualizada por la prueba de reanudación de la primera. Se aisló cada condición con setup fresco; mismas tolerancias, sin tocar arquitectura. Preflight fallido y su log permanecen en preflight-first-failure/. No produjo un entrenamiento comparativo.

Checkpoints guardan la receta heredada de two_bindings.py con armA; lambda_post presente en configuración heredada NO se usa para armA. protocol.json fija explícitamente el objetivo inicial-only. No se ha certificado GPU/AMP.
