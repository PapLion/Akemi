# Señal de entrenamiento

| Experimento | Updates | IDs de entrada procesados | Targets respuesta |
|---|---:|---:|---:|
| distribution-scaling/results/A-result.json | 400 | 380800 | 3200 |
| distribution-scaling/results/C-result.json | 400 | 380800 | 3200 |
| order-curriculum/results/direct.json | 700 | 666400 | 5600 |
| order-curriculum/results/curriculum.json | 700 | 666400 | 5600 |


Las cifras son por corrida, no un corpus acumulado de tokens nuevos. No se suman snapshots ni reproducciones como datos independientes. Los estudios de bindings supervisaban **1 respuesta por119 IDs de entrada (0,8403%)**, aunque softmax siempre cubría8192 clases. A tiene4 respuestas únicas, C8: en400updates cada ejemplo A se repite800 veces y C400. El currículo supervisa5600 respuestas sobre8 combinaciones, con frecuencias desiguales deliberadas. Su diversidad estructural es mínima; los devs cambian estructura y nombres, no son una muestra natural diversa.

La escalera previa (200/200/300/400 updates) demostró memorización de1,2,4 respuestas y fallo al ampliar a48. La intervención factual densa añadía11 targets de hechos con peso0,1 y falló; **no era modelado causal de todo el texto**. No se repite.

Language Bridge V1 sí utilizó next-token sobre secuencias:12537 targets expuestos por brazo, tres brazos64updates, datos reales+32 relatos sintéticos; una capa, local16 salvo baseline transformer. Redujo NLL, generación repetitiva y recuperación distante25%. Bridge V2 y diagnósticos posteriores se centraron en respuestas; control positivo fallido, Hielo no validado en lenguaje. No llamar a toda esta historia pretraining LM.

Este piloto vuelve al **LM causal continuo**: cada token válido predice el siguiente; BOS/EOS explícitos, sin cruce documental ni padding. Ventanas de128 con stride127 conservan cada posición objetivo exactamente una vez por recorrido; reinicio de contexto entre ventanas. Train25355 posiciones objetivo, dev8637;32433 targets expuestos por brazo,25355 posiciones distintas vistas,21,823% de exposiciones repetidas. Train tiene1265 tipos de ID (no1265 ejemplos independientes), solo3 archivos de una familia. Densidad por ventana completa127/128, no garantiza calidad ni binding. No se concluye que LM completo resuelva automáticamente asociaciones.


Los tres brazos de Foreground Contextual Binding también procesaron380800 IDs/3200 respuestas cada uno (400updates), con distinto número de parámetros. Ver additional-history.json para el inventario comprobado desde los batches registrados. Los millones de IDs repetidos de esta familia no equivalen a millones de posiciones de texto natural distintas. No se agrega una suma global engañosa de corridas y duplicaciones.
