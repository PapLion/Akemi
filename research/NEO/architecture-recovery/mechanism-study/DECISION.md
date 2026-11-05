# Decisión experimental

El experimento anterior no aislaba un mecanismo único: cambiaban foreground, inicialización, normalización y cabeza además de memoria. La diferencia0% frente a60% no demuestra superioridad HRM. Esta investigación descarta errores triviales de evaluación y produce controles que sí aprenden, pero todavía no identifica una causa única de toda la diferencia.

|Brazo|Dev media ± SD (puntos)|Semillas17/29/43|
|---|---:|---|
|intact|60.12 ± 10.53|49.11/61.16/70.09|
|transformer|38.39 ± 14.10|22.32/48.66/44.20|
|capacity_transformer|52.68 ± 11.15|43.75/49.11/65.18|
|no_ice|63.84 ± 7.46|57.14/71.88/62.50|
|no_filter|42.56 ± 36.87|0.00/62.95/64.73|
|depth1|46.43 ± 39.03|1.79/74.11/63.39|
|detach|55.95 ± 26.81|25.00/71.88/70.98|
|event|44.35 ± 14.97|29.02/58.93/45.09|
|delta|51.49 ± 14.13|35.27/61.16/58.04|
|event_matched|32.29 ± 26.81|1.34/47.32/48.21|
|delta_matched|41.37 ± 35.87|0.00/60.27/63.84|
|chunk2|40.03 ± 26.34|66.52/39.73/13.84|
|event_fast|60.12 ± 4.90|54.46/62.95/62.95|
|delta_fast|62.65 ± 7.59|70.09/54.91/62.95|

Tres semillas, mismo millar de updates, orden de muestras y receta. No igualdad de FLOPs. No hay prueba confirmatoria de superioridad ni margen de equivalencia preregistrado. La dispersión entre semillas es importante; se conservan todos los fracasos.

## Qué queda demostrado

1. Los modelos originales con0% sí optimizan: todos memorizan el microbatch diagnóstico al100%. Sus predicciones dev son dígitos válidos pero pares entidad–valor vistos en train. El split composicional explica qué falla, no prueba por sí solo la causa del fallo.
2. El histórico sin Hielo alcanza63,84%. Dos refinamientos rápidos normalizados sobre foreground con atención completa son suficientes en este panel. Su logit de respuesta y todos los gradientes son equivalentes a refinar solamente el hidden final de consulta. No hace falta recurrencia temporal para este resultado particular.
3. Un Transformer de capacidad activa comparable alcanza52,68%. Event/Delta con foreground histórico también aprenden en varias semillas; la inicialización de la nueva cabeza cambia mucho el resultado. No se aisló RoPE, FFN, normalización o profundidad individualmente.
4. Gate fijo y profundidad reducida pueden aprender, con inestabilidad en una semilla. No se puede llamar necesarios al gate o a dos pasos en todos los casos. Cortar BPTT no elimina el aprendizaje en dos semillas.
5. EventFast y DeltaFast conservan foreground, readout rápido y memorias editables por chunks; obtienen60,12% y62,65%. La medición CPU muestra menor coste que el histórico; no requieren quitar Hielo/Trapos. Son candidatos de investigación, no arquitectura oficial.

## El promedio oculta el fallo central

El histórico solo alcanza4,17% en corrección y2,08% en hipótesis. EventFast:3,12%/2,08%; DeltaFast:3,12%/7,29%. El primer registro siempre contiene el hecho inicial de la entidad consultada y es respuesta suficiente en cinco de siete tareas. Los modelos aprovechan fuertemente ese atajo.

Prueba causal dirigida: se modifica solo el valor inicial obsoleto, conservando la corrección posterior y la respuesta del oráculo. En corrección, histórico cambia su predicción en93,75% de los casos; EventFast93,75% y DeltaFast92,71%. Histórico sigue el valor obsoleto en ambas versiones en70,83%. Por tanto el éxito medio no acredita actualización selectiva ni protección útil frente a interferencia. Ver `stale_fact_probe.py`, panel y predicciones completas.

Suprimir lectura de Hielo durante inferencia cambia algunas predicciones de los híbridos; su contribución es funcional pero no beneficia consistentemente a todas las semillas. No equivale a entrenar un brazo sin memoria. Sensibilidad de gates/estados tampoco demuestra utilidad.

## Recomendación

Conservar el foreground histórico y el refinamiento rápido normalizado como control positivo, y EventFast/DeltaFast como injertos mínimos funcionales. No promover un ganador ni ampliar modelos todavía. La afirmación más fuerte es suficiencia de un conjunto de mecanismos de atención/readout, no identificación del componente causal único ni prueba de memoria selectiva aprendida.

No se abandona la hipótesis de aislamiento: este panel permite releer todo el prefijo y está dominado por un atajo. No era una prueba adecuada de Hielo fuera de la ventana. El siguiente experimento debe romper ese atajo y separar los factores; `NEXT_EXPERIMENT.md` fija el diseño mínimo recomendado. Sin gasto GPU ni pretraining lingüístico en esta sesión.
