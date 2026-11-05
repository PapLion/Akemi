# Certificación antes del aprendizaje

results/certification.json acredita causalidad train/eval: modificar futuro desdeID32 no cambia logits anteriores ni CE/logits auxiliares inicial/posterior. Equivalencia de memoria con prefijos disponibles mediante tolerancia1e-5. Padding y batch independientes; concatenación de dos documentos resetea Hielo y coincide con sesión aislada. Gradientes iniciales finitos alcanzan memory_head.value. Cobertura AdamW exacta sin duplicados.

Reanudación para cada nueva pérdida:4updates, guardado real, restauración weights_only y4updates. Igualdad exacta frente a8continuos de modelo,decoder,AdamW,TorchRNG,PythonRNG,Random del sampler y órdenes/métricas. Cursor32 al corte,microstep0,acumulación1,sin scheduler. No certifica AMP/CUDA/multiproceso ni interrupciones entre microsteps.

output-verification.json acredita mismos parámetros/decoder/optimizador iniciales, mismos150órdenes de batch, cambios de parámetros/AdamW y decoder ausente en inferencia normal. Estas verificaciones de salida ocurrieron después; contratos de entrenamiento principales sí se ejecutaron antes. historical-preservation.json y hashes comprueban evidencias previas intactas.

Preflight rechazó un generador con desequilibrio posterior, una expectativa errónea640en vez de320 y unos índices fuera de rango. Se conservan fixtures/logs en preflight-failed-*. No se entrenó con ellos. El diagnóstico posterior falló al agregar categoría vacía; se corrigió únicamente ese agregado y se volvió a ejecutar análisis, sin reentrenar.
