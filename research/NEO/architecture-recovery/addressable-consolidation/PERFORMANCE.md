# Rendimiento CPU

|Brazo|Semilla|300 updates (s)|ms/update|Respuestas/s|
|---|---|---:|---:|---:|
|A|17|22.824|76.08|105.15|
|B|17|23.220|77.40|103.36|
|A|29|23.018|76.73|104.27|
|B|29|23.347|77.82|102.80|
|A|43|23.264|77.55|103.16|
|B|43|23.231|77.44|103.31|

Tiempo de actualizaciones medido total:138.904s. No incluye pruebas,evaluación,escritura de informes ni todo el tiempo de sesión. Tiempos incluyen extracción de pérdidas y logging de gradientes/exposiciones; no son benchmark puro de kernels. RSS de cada cost.json es máximo acumulado del proceso,no medida aislada de cada brazo.

Todos292.067parámetros;284.096entrenables más decoder5.140;Hielo8×32(1KiBFP32porsecuencia). Longitud64,batch8 y número de cálculos dense idénticosA/B: se ejecutan proyecciones y candidatos Delta incluso cuando accepted es falso. Más escrituras aceptadas no implica más operaciones omitidas/ejecutadas aquí; la política usa torch.where, no ahorra selectivamente cómputo. Se registran4800escrituras aceptadasA y6000B por brazo(1200correcciones adicionales). No hay medición de FLOPs por profiler; igualdad de formas y bucles no demuestra igualdad exacta de coste efectivo de autograd.

No se han hecho afirmaciones sobreGPU,modelos50M o calidad lingüística. Estados y logs completos tienen coste de disco medido en final-resources.json.
