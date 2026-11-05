# Rendimiento CPU

Medición aislada posterior al aprendizaje: FP32,un thread,batch8,64IDs,8targets/update,4warmups+10mediciones. Inicializaciones desechables; mismas entradas. No hay profiler ni otros entrenadores simultáneos. AdamW incluye clipping; forward incluye preparación de máscaras. RAM es pico acumulado del proceso, no pico aislado del modelo.

|Modelo|Ventana|Parámetros totales/activos|Forward ms|Backward ms|Clip+AdamW ms|Update ms ±SD|Targets/s|
|---|---:|---:|---:|---:|---:|---:|
|intact|16|285952/285952|49.81|83.77|3.73|137.31 ± 1.65|58.26|
|no_ice|16|285952/280736|33.46|52.47|3.20|89.13 ± 1.98|89.76|
|transformer|16|286880/286880|13.87|23.81|3.48|41.16 ± 0.94|194.37|
|event_fast|16|295425/291233|27.94|37.80|3.85|69.58 ± 0.99|114.98|
|delta_fast|16|289731/285539|28.35|39.92|4.04|72.30 ± 1.05|110.64|
|transformer|0|286880/286880|13.73|23.22|3.49|40.43 ± 0.77|197.87|

Cada programa contiene64posiciones de entrada, pero UN target supervisado. Targets/s no equivale a throughput de un LM denso. El modelo calcula logits de todas las posiciones aunque la loss solo usa la última: coste común conservado para comparabilidad; no optimizado aquí. Atención en matrices densas con máscara local, no kernel disperso.

Los FLOPs de linear registrados son una cota parcial de forward. Se añade por separado el head funcional atado; quedan fuera atención, normas, no linealidades, backward y AdamW. No se afirma comparación a igual cómputo. Los híbridos ejecutan8actualizaciones de memoria por programa, el histórico64; gates blandos no ahorran esas operaciones.

## Coste real de las trayectorias primarias

|Modelo/ventana|Semilla|Updates|Respuestas|Segundos de updates|Media ms/update|
|---|---:|---:|---:|---:|---:|
|delta_fast/16|17|1000|8000|73.90|73.90|
|delta_fast/16|29|1000|8000|74.92|74.92|
|delta_fast/16|43|1000|8000|75.33|75.33|
|event_fast/16|17|1000|8000|70.48|70.48|
|event_fast/16|29|1000|8000|73.12|73.12|
|event_fast/16|43|1000|8000|72.51|72.51|
|intact/16|17|1000|8000|138.07|138.07|
|intact/16|29|1000|8000|138.90|138.90|
|intact/16|43|1000|8000|139.37|139.37|
|no_ice/16|17|1000|8000|92.12|92.12|
|no_ice/16|29|1000|8000|92.16|92.16|
|no_ice/16|43|1000|8000|92.46|92.46|
|transformer/0|17|1000|8000|41.18|41.18|
|transformer/0|29|1000|8000|41.59|41.59|
|transformer/0|43|1000|8000|41.58|41.58|
|transformer/16|17|1000|8000|41.51|41.51|
|transformer/16|29|1000|8000|41.02|41.02|
|transformer/16|43|1000|8000|40.89|40.89|

Suma de tiempo interno de updates primarios: 1381.12s. No incluye evaluaciones/checkpointing ni pilotos rechazados. Los tiempos aislados y los de trayectoria son mediciones diferentes; no sustituir unos por otros.
