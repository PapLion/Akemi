# Coste CPU medido

Microfit300updates:22.630s. Principal300updates:22.274s. RSS máximo acumulado:851188KiB; no memoria aislada por brazo.

Modelo292.067parámetros frente289.731del baseline; +2.336(0,81%). Entrenables284.096 frente285.539 porque proyecciones antiguas no usadas están congeladas. Decoder auxiliar5.140igual. La menor cantidad entrenable no implica menor capacidad equivalente. Estado256floats igual.

Medición acotada sin profiler,5updates tras2warmups: Addressable91.73ms/update, rango193.84ms. Son87,21/85,25targets de respuesta/s, con16targets auxiliares adicionales/update. La diferencia pequeña de esta muestra no demuestra aceleración estable. Incluye generación de logs y extracción de ambas etapas en pérdidas comunes.

Proxy aritmético nuevo: clave32→8 y lectura8×32 (~1.024FLOPs/token juntos), nueva proyección32→32 (~2.048/token), más valor32→32(~2.048/evento) y transición Delta O(8×32/evento); se excluyen normas,tanh,elementwise,foreground y backward. No es conteo FLOPs medido ni comparación iso-FLOPs. Escrituras reales2/fixture; rango1 actualizaba cada uno de8chunks. Comparación causal de mecanismos individuales pendiente. Sin medición GPU ni extrapolación CUDA.
