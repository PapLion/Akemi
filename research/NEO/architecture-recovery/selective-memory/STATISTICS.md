# Comparaciones exploratorias emparejadas

Mismos programas y minibatches por semilla. Ganancias/pérdidas frente a histórico sin Hielo, solo IID fuera de ventana. Tres semillas originales; los120programas se reutilizan entre semillas y no son360muestras independientes. No se declaran p-values ni superioridad poblacional.

|Brazo|Semilla|N programas|Gana|Pierde|Diferencia pp|
|---|---:|---:|---:|---:|---:|
|delta_fast|17|120|29|15|+11.67|
|delta_fast|29|120|33|7|+21.67|
|delta_fast|43|120|28|8|+16.67|
|event_fast|17|120|25|15|+8.33|
|event_fast|29|120|37|10|+22.50|
|event_fast|43|120|26|8|+15.00|
|intact|17|120|29|19|+8.33|
|intact|29|120|19|16|+2.50|
|intact|43|120|11|8|+2.50|

La dispersión entre semillas aparece como desviación estándar muestral en RESULTS.md. El máximo de heurísticas por posición y la selección piloto entre híbridos son exploratorios; no constituyen evaluación final independiente. Una ventaja causal útil exige además contrafactuales correctos y degradación de exactitud al intervenir la memoria, no únicamente cambiar logits.
