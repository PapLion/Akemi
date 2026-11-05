# Foreground Learning Diagnosis V1

Resultado: frontera de aprendizaje localizada en ampliar el fixture, no en memorizar una respuesta ni en distinguir dos consultas. La misma arquitectura de dos capas aprende los cuatro casos contrafactuales, pero falla la distribución balanceada de48 respuestas bajo la receta fijada. Una única intervención de supervisión factual más densa tampoco resuelve el fallo. No se identificó una causa única de optimización ni un bug funcional.

|Nivel|Respuestas únicas|Updates|Accuracy train|CE train|Probabilidad correcta mínima|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|1|1|200|100.00%|0.000188|0.999812|6.26|
|2|2|200|100.00%|0.000532|0.999463|6.27|
|3|4|300|100.00%|0.000095|0.999892|9.42|
|4|48|400|35.42%|1.300943|0.148044|13.56|

CPU FP32, seed17, batch8, AdamW LR0,003, betas0,9/0,95, decay0,01, clip1. Cada nivel parte de la misma inicialización B original; no hay currículo acumulado. Trapos/Hielo OFF. Sin GPU, gastos, Chinchilla o conjuntos sellados.

Ver DECISION.md y los seis informes de diagnóstico. Configuraciones prospectivas: PROTOCOL.json y DENSE_PROTOCOL.json. Código, tests, logits completos, parámetros de optimizador/RNG/cursor, curvas, datos y hashes quedan en results/. Reproducción mediante reproduce.sh en copia limpia; nunca sobrescribir históricos.
