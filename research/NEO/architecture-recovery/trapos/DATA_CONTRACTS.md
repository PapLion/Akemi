# Datos

96 IDs ASCII por secuencia, 24 registros de cuatro IDs. Cinco bloques contienen objetivo @XY;, dos bits de confirmación/negación, una propuesta y relleno. El sexto bloque contiene la consulta. Todos los hechos relevantes terminan antes de la ventana activa final IDs 80–95; no hay KV cache ni lectura oculta.

Cada secuencia contiene dos asociaciones válidas, un evento de corrección o repetición y dos propuestas inválidas. Estas últimas incluyen hipótesis, citas no confirmadas, negaciones y afirmaciones fuera del objetivo. El objetivo es causal y explícito; cambia entre secuencias, no durante una secuencia. Semántica de objetivo dinámico queda pendiente. Cada opcode candidato aparece tanto en casos aceptados como rechazados: un único opcode no basta. No se afirma eliminar todos los atajos posibles en un DSL tan pequeño.

Train excluye por completo el par A–C. Dev usa A–C: layout conocido, layouts nuevos 2/3, aliases de marcador de modo %/& no entrenados y escenario limpio. Los cinco opcodes =!~^+ se comparten en la gramática; los aliases nuevos mantienen los mismos campos y bits. No se exige inferir el significado arbitrario de tokens sin contrato: se prueba transferencia de framing declarado, no comprensión libre.

Los conteos reales, targets, duplicados exactos, distribución entidad/valor, tasas de aceptación y heurísticas primera/última global/última por entidad/presencia están en frequencies-*.json. La distribución de roles y longitud se fija; las celdas finitas entidad/valor no son todas exactamente iguales. El panel dev no se considera estadísticamente independiente por cada fila: comparte símbolos y estructuras. No se abrió ningún conjunto sellado.

El oráculo independiente vuelve a interpretar los IDs y valida targets/etiquetas. Un diccionario explícito con la misma semántica resuelve 100%; es solo control de realizabilidad, no prueba de aprendizaje de Hielo. Las etiquetas supervisan BCE, pero no llegan al forward normal.


## Alcance de las consultas emparejadas

El entrenamiento consulta siempre la primera entidad del encabezado de objetivo. La segunda consulta de evaluación conserva ese encabezado y cambia solo el token de consulta: introduce una composición consulta/posición de objetivo no entrenada. Por tanto, la exactitud conjunta combina conservación y generalización de lectura; sus fallos no aíslan interferencia ni selección. Se conserva este resultado y no se reentrena para corregirlo. La respuesta normal al 100% tampoco acredita ambas asociaciones.
