# Contrafactuales

|Brazo|Panel|Respuesta %|Conjunta %|CE|Intercambios|Respuestas iguales|
|---|---|---:|---:|---:|---:|---:|
|A|train|45.83|4.17|1.23294|0/12|22/24|
|A|dev-combinations|22.92|0.00|13.41540|0/12|0/24|
|A|dev-layouts|35.42|0.00|1.32328|0/12|18/24|
|B|train|35.42|0.00|1.30094|0/12|16/24|
|B|dev-combinations|25.00|8.33|3.60391|0/12|6/24|
|B|dev-layouts|33.33|0.00|1.34652|0/12|12/24|
|C|train|41.67|0.00|1.18279|0/12|24/24|
|C|dev-combinations|41.67|0.00|1.18161|0/12|24/24|
|C|dev-layouts|29.17|4.17|1.61719|0/12|18/24|

Intercambiar valores obliga a invertir respuestas: todos los brazos fallan los12 controles estrictos de cada panel. Cambiar consulta no basta para acertar ambas entidades. Las predicciones y aciertos por lado, orden, seguimiento de primer/último valor están en *-evaluation.json.

C responde igual en24/24 historias de train y pares nuevos; B reduce esta frecuencia a16/24 y6/24, pero no logra corrección sistemática. Variación de predicciones o atención no demuestra recuperación correcta. No se evaluó memoria ni se abrieron conjuntos sellados.
