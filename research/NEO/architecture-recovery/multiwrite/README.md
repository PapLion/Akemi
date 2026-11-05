# DeltaFast-MultiWrite V1 — resultado CPU

Rama cryo-multiwrite-v1, origen7ec47a4. Variante aislada, no oficial. A=DeltaFast K1/mismo chunk; B=MultiWrite K2/mismo chunk; C=DeltaFast K1/separados.300updates por brazo, seed17, CPU FP32, sin nuevos datos/modelos lingüísticos/GPU/gastos.

|Brazo / split|Acc A|Acc B|Conjunta|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A/train|30.00%|27.50%|8.12%|1.3461|1.3583|25.00%|
|A/dev|27.50%|25.00%|6.88%|1.3585|1.3632|25.00%|
|B/train|41.25%|42.50%|16.25%|1.2113|1.2044|25.00%|
|B/dev|37.50%|37.50%|13.75%|1.2292|1.2230|25.00%|
|C/train|66.25%|60.00%|33.12%|0.9727|0.9827|63.12%|
|C/dev|61.88%|60.00%|31.25%|1.0119|1.0277|62.50%|

MultiWrite mejora parcialmente sobre A, sin resolver bindings, correcciones ni uso funcional. Gate de confirmación NO superado: no se ejecutan más semillas, K ni hidden sizes. Código y artefactos completos en esta carpeta. Ver DECISION.md.
