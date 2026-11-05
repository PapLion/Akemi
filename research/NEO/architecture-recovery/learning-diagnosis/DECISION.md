# Decisión científica

**Caso D: aprende cuatro casos contrafactuales, pero falla al ampliar la distribución.** No se ha identificado un bug de entrenamiento ni una causa única; tampoco incapacidad representacional absoluta.

- Memorizar una respuesta: sí,100%, CE0,000188.
- Dos respuestas según consulta: sí,100%, CE0,000532.
- Cuatro consultas con bindings invertidos según historia: sí,100%, CE0,000095.
- Distribución48 respuestas: no,35,42%, CE1,300943, conjunta train0%, intercambios0/12.
- Única supervisión factual adicional: no resuelve;25% respuesta train, CE1,394328, intercambios0/12.

La frontera más temprana demostrada aquí es extensión desde dos valores/dos entidades/un orden en cuatro respuestas hacia cuatro valores/dos órdenes en48 respuestas. Esos factores cambian juntos: no podemos atribuir el fallo exclusivamente a cantidad de ejemplos, número de valores, orden, optimizador o señal dispersa. Nivel3 prueba capacidad de aprendizaje contextual en train, no control positivo generalizable.

La CE histórica cae principalmente concentrando probabilidad en cuatro colores, con colapso parcial de argmax. Queries y hechos tienen acceso causal y gradientes; ambos bloques se actualizan. La distinción de logits no basta para recuperar valores correctos. Clipping, competencia de targets y saturación son observaciones, no explicaciones causales ya aisladas.

Siguiente decisión técnica: cerrar cambios arquitectónicos y no retomar Hielo. Si se autoriza otro estudio, separar una única expansión de distribución (cuatro valores manteniendo un orden, frente a dos órdenes manteniendo dos valores) antes de escoger una receta nueva. Es una propuesta de contraste de aprendizaje, no ejecución automática ni rediseño de memoria. No hay fundamento para tercera capa, nuevo tokenizer o regularización arbitraria.

Resultados limitados a seed17, CPU y plantillas EN controladas. No hay validación lingüística general ni autorización de pretraining. Históricos, tokenizer, Hielo, Trapos, A4, corpus y conjuntos sellados permanecen intactos. Se conservan resultados positivos de microfit y negativos de extensión/tratamiento, sin selección de checkpoints favorables.
