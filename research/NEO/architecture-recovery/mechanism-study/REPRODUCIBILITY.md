# Reproducibilidad y recursos

## Identidad

Worktree nuevo `cryo-mechanism-study`, rama `cryo-mechanism-v1`, padre78373cc. El worktree histórico `cryo-next-generation` se conserva separado en su rama y commit originales. Los scripts importan el código congelado del padre y mantienen todos los cambios en `mechanism-study/`. Ningún peso A4, tokenizer, corpus o evaluación sellada forma parte del estudio.

`results/run-metadata.json` conserva hashes de fuentes y protocolo de la matriz principal. El protocolo inicial exacto está preservado como `PROTOCOL_MATRIX_FROZEN.md`; `PROTOCOL.md` añade los suplementos cronológicamente. `ARTIFACT_MANIFEST.json` registra SHA256/tamaño de código, informes, logs, predicciones y checkpoints derivados locales. Los pesos `.pt` están excluidos de Git pero permanecen en el disco y en ese manifest; no se publicaron ni subieron.

## Contabilidad

39trayectorias nuevas de1000updates, tres semillas por13brazos. Cada trayectoria consume8000targets de respuesta y512000IDs de entrada. Total312000targets consumidos y19968000IDs; se reutilizan los448programas train, no son312000ejemplos únicos. Se comparan además las tres trayectorias intactas originales, sin reentrenarlas. Cinco microfits adicionales de200updates×batch16 consumen16000respuestas de16ejemplos reutilizados.

Suma de tiempos de entrenamiento registrados en39trayectorias:2985,82segundos (~49,76min). Excluye auditorías, evaluaciones finales, microfits, tests y benchmarks; no equivale al tiempo total transcurrido de la sesión. CPU N100, FP32, un thread por proceso ML. Pico RSS medido del benchmark intercalado:785,5MiB con cuatro modelos residentes; no es memoria por arquitectura. No se contrató hardware ni se usó CUDA/Vast.ai.

## Evidencias completas

- `original-audit.json`/`original-logits.jsonl`: reproducción estricta de15checkpoints y predicciones originales completas.
- `microfit.json`: pérdidas de todos los updates y predicciones, incluidos los brazos originalmente0%.
- `ablations/`, `capacity/`, `matched/`, `hybrid/`: configuraciones, órdenes, curvas, predicciones train/dev y checkpoints con modelo/AdamW/RNG/cursor.
- `result-validation.json`:39comprobaciones PASS de finitud, carga estricta, AdamW paso1000 y correspondencia de predicciones/órdenes.
- `summary.json`, `curves.csv`, `task-metrics.json`: todos los resultados, sin selección favorable.
- `stale-fact-*`, `support-probe-*`, `hybrid-effects*`, `parameter-gradients.json`: controles posteriores identificados por separado.
- `benchmark-interleaved.json`: muestras individuales y orden; `benchmark.json`: grilla secundaria con alcance distinto.

## Reanudar y reconstruir

Usar los comandos de README con el entorno especificado. Los runners omiten únicamente brazos con resultado final; no iniciar una segunda instancia del mismo runner. Ante apagado a mitad de un brazo, se repite ese brazo; no hay CLI de recuperación parcial del runner. Los tests sí verifican recuperar modelo/optimizador/RNG/sampler/cursor después de updates y continuar exactamente en CPU monoproceso.

Ejecutar report.py, task_metrics.py y final_report.py para reconstruir tablas; luego validate_results.py y manifest.py. El manifest se genera al final para evitar hashes obsoletos por logs todavía abiertos. Comprobarlo sin modificar archivos. No se heredan garantías de determinismo CUDA/AMP/multiproceso.
