# Análisis factorial descriptivo

|Métrica|B−A valores/1 orden|C−A orden/2 valores|D−B orden/4 valores|D−C valores/2 órdenes|Interacción D−B−C+A|
|---|---:|---:|---:|---:|---:|
|accuracy|-0.250000|-0.500000|-0.395833|-0.145833|0.104167|
|joint_accuracy|-0.500000|-1.000000|-0.500000|0.000000|0.500000|
|ce_over_label_entropy|0.223723|1.000006|0.714699|-0.061584|-0.285307|
|accuracy_normalized_above_chance|-0.333333|-1.000000|-0.527778|0.138889|0.472222|

La penalización del segundo orden se compara con el mismo azar marginal dentro de A/C y B/D: −50 y−39,58 puntos de accuracy, respectivamente. Aumentar valores con un orden cuesta25 puntos; con dos órdenes cuesta14,58 puntos brutos, pero el azar cambia50%→25%. Sobre azar normalizado, D incluso supera C (0,138889 frente a0), por lo que no debe interpretarse esa caída bruta como efecto puro adverso de valores.

Caso3 bajo el gate fijo: solo A pasa; B muestra aprendizaje parcial importante. El obstáculo más claro es la variación de orden, no una causa exclusiva del número de colores. Hay no aditividad descriptiva: interacción de accuracy+10,42pp, conjunta+50pp y CE/H−0,285307. Su signo depende de la métrica, pisos y cambio de entropía; no demuestra sinergia ni interacción poblacional con una semilla.

Azar marginal:2 valores50%,4 valores25%; H(etiqueta)=ln2/ln4. CE real usa8192 logits, no renormalización al soporte. B reduce CE frente a H en77,63%; C no reduce frente a ln2; D solo6,16%.

Control con acceso a hechos: escoger primero/último siempre da50% marginal y0% conjunta para TODOS los brazos, aunque haya4 valores posibles. Uniformar sobre los dos valores presentes da CE ln2 y50% en todos. Son referencias distintas del prior marginal; D35,42% está por debajo de esa heurística visible. Oráculo por entidad100%, identificado solo como diagnóstico. No sobrevalorar mejora sobre25% cuando un atajo alcanza50%.

Factores inseparables: número de ejemplos, exposiciones por ejemplo y estructura de minibatches también cambian. C tiene todos sus8 ejemplos y balance exacto en cada batch, aun así colapsa; por tanto un simple desequilibrio marginal de minibatch no explica por sí solo el efecto del orden. A/B fracasan frente al orden invertido no visto, consistente con una solución posicional, pero sin afirmar su mecanismo neuronal único. No se ha demostrado incapacidad representacional absoluta.
