# Rendimiento CPU medido

N100, CPU FP32, un thread PyTorch/BLAS. Benchmark primario: cuatro modelos intercalados en orden aleatorio fijo, mismos IDs y semilla17; dos updates de warmup por modelo y diez mediciones por escenario. AdamW y clipping1 de la receta original incluidos. Datos crudos y orden: `results/benchmark-interleaved.json`. No se ejecutó aprendizaje del estudio simultáneamente; el sistema operativo no estaba aislado. Modelos inicializados, no checkpoints entrenados.

|Brazo|Contexto/batch|Update mediana ms|Forward ms|Backward ms|Answers/s|Speedup vs histórico|CV update|
|---|---|---:|---:|---:|---:|---:|---:|
|intact|64/8|137.87|51.25|82.89|58.02|1.00×|1.90%|
|capacity_transformer|64/8|43.96|16.83|23.73|181.98|3.14×|3.94%|
|event_fast|64/8|74.07|31.24|38.95|108.00|1.86×|4.70%|
|delta_fast|64/8|74.72|29.68|41.31|107.07|1.85×|3.62%|
|intact|128/1|190.71|71.53|115.05|5.24|1.00×|1.09%|
|capacity_transformer|128/1|23.47|12.02|7.67|42.60|8.12×|2.01%|
|event_fast|128/1|63.64|28.38|31.19|15.71|3.00×|1.26%|
|delta_fast|128/1|68.70|29.61|35.02|14.56|2.78×|1.33%|
|intact|256/1|488.06|142.20|341.35|2.05|1.00×|3.08%|
|capacity_transformer|256/1|40.31|22.36|14.32|24.81|12.11×|1.63%|
|event_fast|256/1|122.05|55.05|63.23|8.19|4.00×|2.02%|
|delta_fast|256/1|131.83|57.75|70.12|7.59|3.70×|1.38%|

Son targets de respuesta: uno por secuencia. No son targets LM densos ni capacidad lingüística. El API calcula logits8192 de todas las posiciones aunque solo se supervisa la última. `input_ids_per_s` mide entradas procesadas, no respuestas entrenadas. Contextos128/256 son fixtures de ingeniería sin experimento de generalización a esas longitudes.

## Parámetros y cómputo contabilizado

|Brazo|Total|Entrenables|No embedding entrenables|Forward FLOPs contabilizados 64/b8|Escrituras lentas/doc|
|---|---:|---:|---:|---:|---:|
|intact|285952|285952|23808|301,989,888|64|
|capacity_transformer|286880|286880|24736|301,989,888|0|
|event_fast|295425|291233|29089|301,498,368|8|
|delta_fast|289731|285539|23395|297,345,024|8|

FLOPs: hooks sobre Linear, proyección de salida atada y estimación de productos de atención. Excluyen normalización, activaciones, operaciones elementwise de memoria, backward y optimizador; no son FLOPs completos de hardware. Total incluye módulos históricos congelados de los injertos. Igualar parámetros no iguala cómputo; el embedding común domina el total.

La grilla secundaria `benchmark.json` cubre doce brazos y tres escenarios, dos warmups/cinco updates, SIN clipping: sirve para contabilidad y exploración, no se mezcla con la tabla primaria. RSS máximo primario es acumulado del proceso con cuatro modelos residentes: 785.5MiB. No se atribuye ese pico a un modelo individual.

EventFast/DeltaFast mantienen dos refinamientos rápidos y leen Hielo, pero vectorizan tokens dentro de cada chunk con memoria anterior y escriben cada8tokens. Es un cambio arquitectónico causal, no equivalencia exacta con histórico. Reduce llamadas Python y escrituras; no se midió la fracción causal del ahorro atribuible a cada factor. Gates soft no omiten escrituras. No hay medición CUDA nueva, compilación, Triton ni extrapolación fiable a12M/50M.

En64/b8 los híbridos conservan la media dev observada a menor coste de update. Eso permite seguir estudiándolos; no demuestra equivalencia estadística, ventaja de Hielo ni mejora en correcciones. El Transformer de capacidad comparable sigue siendo más rápido.
