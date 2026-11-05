# Contraste primario ejecutado

|Brazo / split|Acc A|Acc B|Conjunta|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A/train|30.00%|27.50%|8.12%|1.3461|1.3583|25.00%|
|A/dev|27.50%|25.00%|6.88%|1.3585|1.3632|25.00%|
|B/train|41.25%|42.50%|16.25%|1.2113|1.2044|25.00%|
|B/dev|37.50%|37.50%|13.75%|1.2292|1.2230|25.00%|
|C/train|66.25%|60.00%|33.12%|0.9727|0.9827|63.12%|
|C/dev|61.88%|60.00%|31.25%|1.0119|1.0277|62.50%|

A/B utilizan idénticos programas. En este estudio se fijaron y ejecutaron300updates completos para TODOS los brazos. Semilla17, batch8, LR.003, clip1, AdamW betas(.9,.95),decay.01. `CE_respuesta + .1 CE_inicial` con2targets medios, sin supervisión posterior. Orden de los300batches idéntico. Checkpoint0/150/300 preservado por brazo. Datos160programas por brazo, sin corpus/tokenizador nuevo. Dev desplazado, comparte combinaciones y órdenes; no es generalización composicional independiente.

Ganancia B−A conjunta train8.125puntos,dev6.875puntos. Es parcial y de una semilla; no equivale a almacenamiento fiable, y no habilita confirmación. C es una referencia secundaria con otra trayectoria, no una ablación de igual visibilidad temporal de memoria. El lector B sigue25%, igual A.300updates no solucionan end-to-end.

Gate fijado en protocol.json antes de resultados: mejora≥10puntos train/dev,dev conjunta≥50%,swap estricto≥25%. confirmation-gate.json lo rechaza. No más semillas, K4/K8 ni hidden mayor. Curvas, gradientes por tensor, CE/accuracy de cada update y predicciones por documento quedan completas.
