# Decisión: factorial cerrado

**Solo A supera el gate; la variación de orden es el obstáculo más claro bajo la receta actual, con aprendizaje parcial al ampliar valores.**

|Brazo|Valores/órdenes|Respuestas únicas|Accuracy|Conjunta|Intercambios|CE|CE/H(etiqueta)|Azar marginal|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|A|2/1|4|100.00%|100.00%|1/1|0.000007|0.000010|50%|
|B|4/1|24|75.00%|50.00%|3/6|0.310159|0.223733|25%|
|C|2/2|8|50.00%|0.00%|0/2|0.693158|1.000016|50%|
|D|4/2|48|35.42%|0.00%|0/12|1.300943|0.938432|25%|

1. **Factor principal observado:** añadir segundo orden con dos valores basta para pasar de100% a50%, conjunta100%→0%, CE≈ln2. Con cuatro valores, el segundo orden reduce75%→35,42%. Aumentar valores sin cambiar orden permite75% y50% conjunta; no es un fracaso total.
2. **Interacción:** existe no aditividad descriptiva, no una interacción causal general demostrada. Pisos, azar y diversidad cambian; no atribuir exclusivamente a número de ejemplos o colores.
3. **Pérdida y colapso:** B aprende parcialmente y deja gold sin recuperar; C mantiene distribución binaria prácticamente uniforme y argmax siempre red; D concentra argmax en dos colores y obtiene poca ganancia de información.
4. **Ajuste/generalización:** C/D fallan en train; B aprende parcialmente; A sobreajusta. A obtiene0% al invertir orden y no generaliza al layout alternativo. No tenemos control positivo neuronal de binding independiente de estructura.
5. **Única modificación de receta recomendada, NO ejecutada:** currículo de orden a dos valores: primero aprender el fixture de un orden y luego introducir la distribución mixta ya definida, sin cambiar arquitectura, LR, pérdida o dimensión. Contrastar prospectivamente contra C desde cero, controlar presupuesto/exposición y exigir ambos órdenes al final. La hipótesis es facilitar salir del régimen simétrico/informativamente plano; no se ha probado que lo resuelva. Cambiar solo balance marginal no es explicación suficiente: C ya tenía balance exacto en cada minibatch. No recomendar aumentar escala por esta evidencia.
6. **Cerrar:** ampliaciones ciegas de capas/dimensiones, formatos de consulta, microfits de chunks/escrituras y uso de estos porcentajes para volver a Hielo/Trapos. La clasificación sintética aquí no autoriza memoria lingüística ni pretraining. No se ejecutan nuevos entrenamientos en esta fase.

A300/D400 reproducen exactamente pesos, AdamW y RNG Torch históricos; la diferencia de RNG Python global no utilizado está documentada. No hubo cambio oculto de distribución, tokenizer ni optimizador. Históricos intactos. Resultado limitado a semilla17 y plantillas EN con extracción sintáctica fija; no capacidad lingüística general.

Archivos de decisión y efectos guardan el negativo. No nuevas semillas, pérdidas, GPU, gastos, Chinchilla, A4 ni evaluaciones selladas.
