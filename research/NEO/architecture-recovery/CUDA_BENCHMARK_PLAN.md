# Validación CUDA posterior, no ejecutada

`future_cuda.py` produce un plan por defecto. `--execute` requiere CUDA, usa únicamente IDs sintéticos, FP32, un único dispositivo y límite temporal180s. No contiene llamadas Vast.ai ni credenciales, alquiler o transferencia. No se ha contratado una GPU para este trabajo.

Antes de autorizar un alquiler deben portarse y ejecutar los contratos CPU completos: sesiones, packing, fronteras, gradientes, AdamW, checkpoints y reanudación. El script incluye checks limitados de causalidad/gradientes; **no constituye certificación CUDA completa**. BF16, compilación, Triton y CUDA Graphs quedan pendientes para esta arquitectura nueva.

Comparación propuesta: localB0, fullB0 con contexto visible equivalente, CryoTiny congelado de referencia, Event y Delta (secuencial/scan), contextos128/256, batch4. Los parámetros reales son ~0,28M; no extrapolar a12M/50M. Publicar FLOPs y contextos distintos junto al throughput. Capturar warmup y muestras sostenidas separadas, picos VRAM y trazas acotadas. Repetir fuera del profiler.

Cuello de implementación conocido: `_plans` mueve metadatos aCPU, convierte escalares y crea índices desdePython; contadores y bucles por fragmento también pueden sincronizar CUDA. No sabemos cuánto costarán allí. Una futura optimización debe preconstruir el plan de packing enCPU y moverlo una vez, vectorizar selección y verificar paridad; no trasladar sin más el certificado de CryoTiny antiguo.

No se recomienda gastar saldo para buscar una victoria de calidad todavía. Primero resolver la falta de generalización sintética observada con otro protocolo fijado. Un benchmark de velocidad puede decidirse independientemente, con autorización económica nueva y exportación/destrucción obligatoria del recurso remoto.
