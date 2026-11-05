# Reproducibilidad

Origen Git3950afc. Código nuevo solo addressable/. Intérprete y comandos en README. Dependencias importadas desde las carpetas históricas versionadas de este worktree; fuente aprendida DeltaFast seed17 cargada estrictamente con weights_only desde worktree selective-memory original.

Datos train/dev completos y frecuencias en results. Orden de300batches igual al baseline documentado. Semillas modelo fuente17,decoder101,nuevos módulos707; un hilo,CPU FP32,dropout0. Checkpoints incluyen AdamW completo,sampler RNG,Python RNG,torch RNG,cursor,step,microsteps y acumulación. Sin scheduler. Restauración exacta probada después de updates reales.

No se retocó el baseline ni el checkpoint histórico. historical-integrity.json valida SHA256SUMS de MultiWrite; source-manifest.json identifica checkpoint fuente y código padre. `.certified.pt` corrige solo metadatos de receta de las primeras copias preservadas; usar esos archivos para inspección inequívoca. Reanudador del piloto admite ambas copias porque los pesos y estados no cambian; no certifica otras configuraciones.

Las pruebas generales no son un certificado de calidad lingüística ni de selección, y los diagnósticos postentrenamiento no se usaron para nuevas actualizaciones. No se abrió ninguna evaluación sellada. Artefactos enumerados en SHA256SUMS (excluye propio manifiesto y pycache).

Tras entrenar, ejecutar también `checkpoint_metadata.py` antes de `final_verification.py`; generan copias certificadas y verifican equivalencia. `write_reports.py` produce los informes medidos, verifica el manifiesto anterior y registra procedencia. Generar SHA256SUMS al final para incluir los informes definitivos. Los scripts de evaluación usan solo diagnóstico no sellado.
