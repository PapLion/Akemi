# Escalera de aprendizaje

Presupuesto y gates congelados antes de ejecutar. Cada nivel usa modelo B sin cambios, seed17 e inicialización fresca idéntica. Se exige100% train, CE≤0,1 y P correcta≥0,9 en todas las respuestas al checkpoint final fijo. Son criterios de memorización, no generalización.

|Nivel|Respuestas únicas|Updates|Accuracy train|CE train|Probabilidad correcta mínima|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|1|1|200|100.00%|0.000188|0.999812|6.26|
|2|2|200|100.00%|0.000532|0.999463|6.27|
|3|4|300|100.00%|0.000095|0.999892|9.42|
|4|48|400|35.42%|1.300943|0.148044|13.56|

1. Una historia y una consulta.
2. Misma historia con consultas independientes a Nora/Iris.
3. Añade la historia con valores intercambiados y ambas consultas: cuatro respuestas.
4. Las48 respuestas originales: dos órdenes, cuatro valores, pares distintos, dos consultas. Los nombres son los reales del fixture y su tokenización V3 queda intacta.

Los niveles1–3 pasan. Nivel3 prueba que el mismo nombre recibe respuestas distintas según los hechos. Las cuatro respuestas son simultáneamente correctas; no es un predictor fijo por nombre. Sus logits completos, sensibilidad al cambio de consulta y hechos están en functional-final.json y level-3-four-cf.pt.

Nivel4 falla incluso en train. El checkpoint reproduce EXACTAMENTE los pesos del B histórico (state hash), de modo que el resultado no proviene de un nuevo motor incompatible. Se detiene la escalera en4; solo se ejecuta el contraste de señal autorizado por esa frontera. No se entrenan otras semillas ni Hielo. Dev es descriptivo: nivel3 no constituye generalización más allá de sus cuatro respuestas de train.
