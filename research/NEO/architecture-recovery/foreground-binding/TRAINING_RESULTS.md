# Resultados de entrenamiento

Semilla 17; CPU FP32, un thread; 400 updates finales fijos por brazo, batch 8, LR 0,003, clipping 1. Sin Hielo ni Trapos.

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

48 respuestas/24 historias por panel. Conjunta exige ambas consultas correctas; intercambio estricto exige cuatro respuestas correctas en historia y contrafactual. Los checkpoints finales400 son los únicos seleccionados. Curvas y gradientes de cada update en *-training.json; predicciones completas por panel. No hay aprendizaje de train suficiente para certificar memorización del fixture, por tanto no atribuimos el fallo exclusivamente a generalización. Una semilla no permite inferencia estadística poblacional.
