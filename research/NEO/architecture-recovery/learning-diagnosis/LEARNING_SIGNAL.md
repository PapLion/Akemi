# Señal de aprendizaje: único contraste adicional

Hipótesis congelada después de observar nivel3 PASS y nivel4 FAIL: una respuesta supervisada por119 IDs puede ser insuficiente para aprender bindings composicionales con esta receta. No se declara causa demostrada. DENSE_PROTOCOL.json fija peso0,1 y400 updates antes de entrenar.

Original: L_respuesta. Tratamiento: L_respuesta +0,1×media CE de próximos tokens factuales. Los11 tokens del tramo factual se predicen desde sus posiciones anteriores causales; no hay labels entidad–valor adicionales ni parser oracular. Se excluyen targets de consulta, neutral y padding. La media de respuesta permanece idéntica; no se normaliza mezclando ambos conjuntos de targets.

Mismo B, seed, inicialización, datos y orden, batch8,400 updates, optimizer y clipping. Control reutiliza nivel4, cuya igualdad exacta con B histórico está verificada. Tratamiento añade35.200 targets factuales frente a3.200 de respuesta; no es igualdad de supervisión ni de cómputo. Se certifican máscara causal, igualdad de CE principal, gradientes y reanudación. Checkpoint denso debe cargarse junto a dense-checkpoint-contract.json y DENSE_PROTOCOL.json para verificar objetivo/script/hash.

|Objetivo|Panel|Accuracy respuesta|Conjunta|CE respuesta|Intercambios|
|---|---|---:|---:|---:|---:|
|Original|train|35.42%|0.00%|1.300943|0/12|
|Original|dev-combinations|25.00%|8.33%|3.603910|0/12|
|Original|dev-layouts|33.33%|0.00%|1.346518|0/12|
|Denso|train|25.00%|8.33%|1.394328|0/12|
|Denso|dev-combinations|12.50%|0.00%|13.036391|0/12|
|Denso|dev-layouts|25.00%|8.33%|1.394178|0/12|

El último minibatch denso tiene CE factual 0.325865; CE respuesta 1.365857. Aprende predicción factual superficial sin resolver consulta. Tiempo tratamiento 17.31s (incluye evaluaciones de curva/final; no es benchmark puro comparable). Resultado negativo: no prueba que toda supervisión densa sea inútil, solo que esta intervención no resuelve el bloqueo. No se prueban otras lambdas, losses o recetas.
