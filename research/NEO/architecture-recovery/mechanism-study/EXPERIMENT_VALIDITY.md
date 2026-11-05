# Validez del experimento original

La evaluación se reprodujo desde quince checkpoints originales con `torch.load(weights_only=True)`, carga estricta y CPU. `results/original-audit.json` y `original-logits.jsonl` conservan los resultados y ocho logits superiores por caso. No se editaron pesos originales.

## Contrato comprobado

672 programas simbólicos,448train/224dev, siete tareas;64IDs por entrada y un único target por ejemplo. La respuesta se predice desde la posición63: no está añadida como respuesta teacher-forced. Sí aparecen valores legítimos y distractores dentro del prefijo. El argmax usa los8192IDs, sin restringirlo a ocho dígitos. El atajo de evaluación coincide con el último logit del forward completo. Las predicciones reproducen exactamente las guardadas. El oráculo ejecutable concuerda con todas las etiquetas; hashes y familias train/dev son distintos.

Semillas17/29/43;1000updates×batch8; orden `Random(seed+5000)` idéntico entre brazos. AdamW lr.003,betas(.9,.95),decay.01,clip1,dropout0. Embeddings compartidos por semilla entre brazos; salida atada. Esto iguala ejemplos y targets, no FLOPs ni arquitectura.

## Qué significa el0%

Dev excluye deliberadamente pares consultados entidad–valor mediante `(entidad+valor)%4==3`, además de excluir familias estructurales. En B0 local/full,Event yDelta todas las predicciones dev son dígitos válidos y el100% corresponde a pares vistos en train. La etiqueta correcta queda típicamente alrededor del rango7–9. Por tanto el0% mide un fracaso de generalización bajo desplazamiento composicional; no demuestra imposibilidad de optimización, ni incapacidad lingüística general.

Sobreajuste controlado:16registros train fijos, dos por valor,semilla17,batch16,200updates, misma receta. Los cinco brazos alcanzan100% sobre ese subconjunto; NLL final0.00131–0.00163. `microfit.json` guarda cada update y predicciones. La selección ordenada produjo ejemplos de la primera tarea; es un diagnóstico sencillo de memorización, no cobertura de las siete tareas. No se ajustó la receta al observar dev.

## Confusiones históricas que permanecían

- Histórico: atención causal completa GQA/RoPE,FFN4d,inicialización.02 y cabeza rápida/lenta recurrente. Nuevo: atención local o completa, posición sinusoidal,FFN2d,inicialización.05 y otra memoria. No era una ablación de Hielo.
- Vocabulario8192,pero estos programas usan34IDs de entrada; embeddings dominan los ~0.28M parámetros. Igualar parámetros totales no iguala capacidad computacional útil.
- Dev tiene desplazamiento simultáneo de combinaciones y estructura; no separa esas dos dificultades.
- La tarea hipótesis siempre sustituye una hipótesis borrada: no identifica por separado la capacidad de borrar.
- El contrafactual histórico cambia el valor sumando1; puede devolverlo al soporte train. No es una prueba simétrica de generalización fuera de soporte.
- No hay español/inglés natural, generación libre, memoria fuera de toda atención visible ni evidencia de superioridad sobre Transformers generales.

Las ablaciones nuevas mantienen estos datos para aislar arquitectura. No se reescribe la evidencia negativa ni se llama bug al diseño deliberado del split. Un panel factorial posterior debe distinguir soporte de valores y familias por separado.

## Atajo identificado después de las ablaciones

El primer registro siempre es el hecho inicial de la entidad consultada. En cinco de siete tareas puede copiarse su valor; en corrección/hipótesis ese valor es obsoleto. El histórico alcanza solo4,17%/2,08% en esas dos tareas. Cambiar únicamente ese valor obsoleto sin cambiar el oráculo altera93,75% de sus predicciones de corrección. Los híbridos mantienen el mismo problema. Esto limita la interpretación del60%: sí hay aprendizaje composicional parcial, pero no evidencia de actualización selectiva correcta. `TASK_RESULTS.md` y `DECISION.md` incluyen los resultados negativos.

La prueba posterior `support_probe.py` rota todos los valores semánticos globalmente para desplazar el soporte entidad–valor, con oráculo y familias conservados. No es un holdout IID ni permite atribuir todo el error al split; es un control adicional, con todas las predicciones conservadas y sin reentrenar.
