# Contratos y reproducibilidad

Tres tests ejecutados antes de entrenar y de nuevo al cierre: distribución/identidad histórica; targets, tokenización, causalidad, aislamiento, no fuga y cobertura AdamW; trayectoria8 updates continua frente a3+5 para los cuatro brazos con parámetros, estados AdamW, RNG y cursor exactos. Gradientes finitos en ambos bloques. Tokenizer original verificado por hash.

Checkpoint incluye modelo, optimizer, Torch/Python RNG, cursor updates/samples, orden/dataset SHA, fingerprint y SHA tokenizer, protocolo y código fuente; sin scheduler ni acumulación pendientes. Carga weights_only=True. Todos los optimizadores finales tienen paso400 y cobertura exacta de parámetros activos. Se evalúa siempre final400; checkpoint300 solo para auditoría histórica, no selección.

A300 reproduce exactamente pesos, AdamW y RNG Torch de nivel3; D400 los de nivel4. Global Python RNG histórico difiere, pero no participa en forward/update: muestreo usa random.Random(17) local. Su estado sí se restaura exactamente dentro de la nueva prueba de reanudación. No se declara identidad global histórica de ese RNG.

Dos incidencias de instrumentación preservadas: import-preflight-failure.log registra colisión con el nombre experiment.py histórico, corregida renombrando el nuevo script factorial.py antes de entrenar; audit-first-metadata-failure.log registra el requisito excesivo de igualar RNG Python global no usado entre invocaciones históricas. No cambió ningún peso ni tolerancia; se registró la diferencia explícitamente.

Los tests heredados ya certificaban el forward de dos capas. Esta fase no modifica modelo, Hielo, Trapos, tokenizer, A4 ni corpus. Sin GPU, gasto o pretraining.
