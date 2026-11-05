# Decisión MultiWrite V1

|Brazo / split|Acc A|Acc B|Conjunta|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A/train|30.00%|27.50%|8.12%|1.3461|1.3583|25.00%|
|A/dev|27.50%|25.00%|6.88%|1.3585|1.3632|25.00%|
|B/train|41.25%|42.50%|16.25%|1.2113|1.2044|25.00%|
|B/dev|37.50%|37.50%|13.75%|1.2292|1.2230|25.00%|
|C/train|66.25%|60.00%|33.12%|0.9727|0.9827|63.12%|
|C/dev|61.88%|60.00%|31.25%|1.0119|1.0277|62.50%|

**No se valida esta representación como solución de Hielo.** Hay mejora parcial de decodificación frente a rango1/mismo chunk, pero falla formación conjunta robusta, corrección, intercambio de valores y uso del lector original. Los candidatos mantienen representaciones muy similares; no aprendieron especialización útil demostrada. C mejora más, aunque tampoco supera contrafactuales.

1. K2 no aprende dos bindings fiables que A no consiga; solo aumenta la señal parcial.
2. Queries y pesos de selección difieren, pero candidatos y gradientes casi coinciden.
3. La ganancia pequeña persiste en layout nuevo, no demuestra generalización composicional ni mejora reproducida.
4. Corrección conjunta posterior B15.3125% frente A6.25%; insuficiente para actualizar una asociación conservando la otra de forma fiable.
5. Lector B25%; no usa la mejora del decoder para responder correctamente.
6. +32parámetros y~9.84% de tiempo en esta ejecución CPU; doble transición y más proyecciones, sin ahorrar cómputo por gate pequeño.
7. No hay control de capacidad entrenado; parámetros/inicialización/escalado/cómputo siguen parcialmente confundidos.
8. **Se detiene esta línea MultiWrite V1.** No más K, hidden sizes, seeds ni variantes para perseguir un PASS. Conservar como evidencia negativa con una mejora representacional parcial. No pretraining ni benchmark GPU.

No se ha demostrado incapacidad de memorias asociativas ni que rank1 sea la causa única. Antes de otra arquitectura, reconsiderar explícitamente direccionamiento entidad–valor y señal de aprendizaje, con controles que distingan información presente de readout. La casi coincidencia de candidatos motiva esa pregunta, pero no autoriza añadir ortogonalidad, más slots y otro lector simultáneamente. No se inicia otro experimento automáticamente.
