# Protocolo congelado

Ver PROTOCOL.json, escrito antes del entrenamiento. Directo C700 frente A300→C400. Arquitectura B histórica, 299520 parámetros asignados / 296160 entrenables, dos bloques width32; Hielo/Trapos OFF. CPU FP32, un thread, AdamW .003, betas .9/.95, wd .01, clip1, batch8. CE original de respuesta sobre 8192 IDs. Sin pérdida auxiliar. Checkpoint final fijo, sin selección por dev.

El optimizador no se recrea entre etapas. Snapshots completos 0/300/700 contienen parámetros, AdamW, RNG Python/Torch, cursor global, etapa siguiente, hashes de datos/tokenizer/código.

Compuertas train: ocho respuestas, historias y swaps 100%, ambos órdenes. Generalización: conjunta y swaps ≥90% en ambos devs; sin dependencia exclusiva de posición. Solo entonces semillas29/43.
