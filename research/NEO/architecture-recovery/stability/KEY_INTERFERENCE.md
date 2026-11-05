# Interferencia y coste

Cada *-metrics.json conserva la matriz Gram de claves A–E y errores condicionados por par. interference-diagnostics.json registra gradientes de respuesta por rol, cosenos entre ellos y cambios de la lectura kᵀH después de actualizar otra entidad. Se usa el checkpoint final congelado; cero updates diagnósticos.

Una correlación entre cosenos y errores no prueba causalidad. Un cambio de vector leído tampoco demuestra pérdida semántica por sí solo. Las exactitudes normales emparejadas y contrafactuales son el criterio funcional. Los gradientes diagnósticos de 32 ejemplos por rol son descriptivos, no una estimación exhaustiva de entrenamiento.

- B-17: 23.093 s de entrenamiento, 292067 parámetros, RSS pico del proceso 849904 KiB.
- B-29: 26.363 s de entrenamiento, 292067 parámetros, RSS pico del proceso 956452 KiB.
- B-43: 26.007 s de entrenamiento, 292067 parámetros, RSS pico del proceso 956452 KiB.
- C-17: 26.260 s de entrenamiento, 292067 parámetros, RSS pico del proceso 956452 KiB.
- C-29: 25.288 s de entrenamiento, 292067 parámetros, RSS pico del proceso 956452 KiB.
- C-43: 25.689 s de entrenamiento, 292067 parámetros, RSS pico del proceso 957864 KiB.

Se conserva número y dimensiones de parámetros. C introduce más acontecimientos aceptados y modifica layouts, pero la implementación calcula candidatos en todas las posiciones en ambos brazos. Igual número de IDs/targets no implica igualdad exacta de FLOPs útiles o trayectoria de memoria. No se midió GPU ni se extrapola aceleración. No se separaron causalmente capacidad de claves, extracción de valores y lectura.

| Semilla | cos(A,C), B | cos(A,C), C |
|---|---:|---:|
| 17 | 0.686071 | -0.003102 |
| 29 | 0.199499 | 0.007389 |
| 43 | 0.211949 | 0.004108 |

A–C es el par reservado. Estos cambios son compatibles con menor interferencia de direccionamiento, pero la intervención fue sobre datos, no sobre el coseno. No se ha aislado el efecto de cobertura de pares del de layouts y distractores.
