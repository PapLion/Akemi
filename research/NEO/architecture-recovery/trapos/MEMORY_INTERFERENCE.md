# Conservación y contaminación

La formación, corrección y conservación se miden con respuestas normales por entidad y consultas emparejadas. No se entrenó un decoder auxiliar de valores. Los estados de los ocho primeros ejemplos por familia se conservaron por selección determinista, incluyendo aciertos y fallos. Las propuestas rechazadas tienen cambio H exactamente cero por contrato; no se interpreta distancia de estado como binding correcto.

- A-17: cambios de estado {"accepted": {"max": 9.424214363098145, "mean": 4.879908623049657, "n": 960}}; reset Hielo → 25.00% de respuestas; intercambio compatible sigue compañero 100.00%.
- B-17: cambios de estado {"accepted": {"max": 8.601873397827148, "mean": 4.737676212761392, "n": 727}, "rejected": {"max": 0.0, "mean": 0.0, "n": 233}}; reset Hielo → 25.00% de respuestas; intercambio compatible sigue compañero 66.67%.
- C-17: cambios de estado {"accepted": {"max": 7.705127716064453, "mean": 5.1283408855088055, "n": 768}, "rejected": {"max": 0.0, "mean": 0.0, "n": 192}}; reset Hielo → 25.00% de respuestas; intercambio compatible sigue compañero 100.00%.
- D-17: cambios de estado {"accepted": {"max": 8.039618492126465, "mean": 5.384521612690555, "n": 576}, "rejected": {"max": 0.0, "mean": 0.0, "n": 384}}; reset Hielo → 25.00% de respuestas; intercambio compatible sigue compañero 100.00%.

Los intercambios emparejan mismo objetivo, entidades y estructura, cambiando únicamente valor vigente. No se interpreta una perturbación arbitraria fuera de distribución como causalidad concluyente.


## Alcance de las consultas emparejadas

El entrenamiento consulta siempre la primera entidad del encabezado de objetivo. La segunda consulta de evaluación conserva ese encabezado y cambia solo el token de consulta: introduce una composición consulta/posición de objetivo no entrenada. Por tanto, la exactitud conjunta combina conservación y generalización de lectura; sus fallos no aíslan interferencia ni selección. Se conserva este resultado y no se reentrena para corregirlo. La respuesta normal al 100% tampoco acredita ambas asociaciones.
