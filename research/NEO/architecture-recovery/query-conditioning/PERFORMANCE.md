# Coste CPU del contraste

|Formato|Tiempo200updates|Respuestas/s|IDs entrada/s|RSS pico proceso MiB|
|---|---:|---:|---:|---:|
|A|3.8560|414.94|49377.94|694.71|
|B|3.8721|413.21|49172.08|694.71|

284096parámetros asignados,280736entrenables; idénticos en A/B.1600respuestas/brazo,48ejemplos únicos (33ciclos completos y fracción). RAM es máximo acumulado de proceso, no asignación aislada. Medidas sin profiler, sin CUDA; no extrapolación GPU ni FLOPs medidos. Los snapshots de atención se toman fuera de entrenamiento. No hay evidencia de mejora de eficiencia, y no es el objetivo del contraste.
