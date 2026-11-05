# CPU

| Brazo | Tiempo train s | ms/update | Parámetros | Entrenables | RSS pico KiB |
|---|---:|---:|---:|---:|---:|
| A-17 | 41.775 | 139.251 | 292612 | 284096 | 1048704 |
| C-17 | 42.255 | 140.849 | 292612 | 284641 | 799136 |

La cabeza sigue teniendo545 parámetros. A la conserva congelada y C la entrena. Los rechazos evitan la modificación de Hielo, pero el código aún calcula proyecciones y candidato Delta; no se afirma ahorro computacional. RSS es máximo acumulado del proceso, no medición aislada por brazo. No se midió CUDA.

Curvas SVG autocontenidas en results/learning-curves.svg; incluyen valores crudos por microbatch, sin suavizado ni selección del mejor checkpoint. No representan exactitud del corpus train completo.
