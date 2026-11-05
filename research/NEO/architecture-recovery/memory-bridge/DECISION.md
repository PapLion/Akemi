# Decisión cerrada

**Resultado: inconcluso sobre memoria lingüística de Hielo; fallo de la precondición neuronal de recuperación.** Clasificación A del protocolo: el foreground de contexto completo no aprende suficientemente la tarea elemental bajo el presupuesto fijado. No es un resultado negativo de Hielo entrenado: ese entrenamiento no llegó a ejecutarse.

Hechos demostrados:
1. Los datos y el control explícito permiten recuperar exactamente los valores; priors de pregunta/presencia solo25%.
2. La pérdida siguiente-token recibe el prefijo correcto, sin answer en el forward, con gradientes finitos y parámetros actualizados. Full-context tiene acceso efectivo al hecho; no está ejecutándose accidentalmente con ventana16.
3. El microfit completo llega a50% respuesta y18.75% conjunta, CE1.04552; responde igual a ambas entidades en16/16historias y resuelve 0/6 intercambios estrictos. No certifica recuperación por entidad.
4. Los estados de Hielo V1 persisten, la lectura está conectada y las intervenciones afectan logits, pero eso no demuestra utilidad funcional ni entrenamiento V2.
5. Se respeta el fallo prospectivo: sin brazos400, sin confirmaciones29/43, sin retocar umbrales, LR, capacidad, tokenizer o arquitectura.

No hay base para concluir «Hielo no puede guardar lenguaje» ni «el único fallo está en Delta/Trapos/reader». El bloqueo observable actual es la adquisición de la asociación pregunta–entidad–valor en la receta de entrenamiento/foreground completo. No se aislaron capacidad, optimización y dependencia posicional como causas excluyentes. El fallo al acortar el contexto sin reentrenar tampoco las distingue.

Siguiente contraste mínimo, pendiente de decisión explícita: certificar un control de recuperación con contexto corto y la MISMA arquitectura/receta y respuestas balanceadas, frente al contexto completo de distancia96, manteniendo un presupuesto fijado antes de ejecutar. Solo debe cambiar la distribución/distancia, sin nuevas memorias ni tokenizador. Si ese control no aprende, localizar condicionamiento por consulta/representación y señal de aprendizaje antes de entrenar Hielo; si aprende, recién estudiar distancia y transporte con un control positivo válido. No se ejecuta automáticamente aquí.

Se conserva Addressable V1.2, Trapos congelado y todos los negativos. No se autoriza pretraining, GPU ni transición a lenguaje abierto. El conjunto confirmatorio nuevo permanece sellado. La infraestructura V2 está implementada, los contratos pasan y la pregunta central permanece abierta por una compuerta real, no por falta de ejecución del piloto.
