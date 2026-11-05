# Asociación, conservación y actualización

Misma capacidad de Hielo:256floats,1KiB FP32 por secuencia, sin crecimiento con longitud. Es una memoria asociativa distribuida, no256slots discretos.

Formación:100% de ambas asociaciones en train y layouts. Retención tras chunks rechazados:100%; la escritura se omite determinísticamente, no hay selección aprendida.

Panel de correcciones controlado:640casos (preservar/corregir y afectar cada entidad), generados después del entrenamiento como diagnóstico no usado para ajustar. Tras corrección:75% conjunta; cada rol87,5%; entidad efectivamente modificada75%, no modificada100%. Respuesta normal87,5%. Por tanto no está resuelta la actualización semántica fiable.

Diagnóstico de mecanismo: en640eventos, la clave vuelve a leer el vector latente recién escrito con error máximo 4.76837158e-07. Es evidencia de reemplazo algebraico del vector, no de que v codifique correctamente el valor simbólico. Cambiar el operador de corrección `!` por `=` equivalente conserva75%/100%; la novedad de `!` por sí sola no explica el fallo. Permanecen extracción/representación de valor en nuevos contextos y lectura/generalización como explicaciones no aisladas.

El otro panel heredado con escritura inicial desplazada y evento en posición distinta alcanza56,25% conjunta inicial y75% posterior: ver main-corrections.json. No ocultarlo detrás del layout dev perfecto. Las estructuras nuevas afectan el resultado.
