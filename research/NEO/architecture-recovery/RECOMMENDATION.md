# Decisión de continuación

Los dos prototipos existen y cumplen contratos mecánicosCPU. En1.000updates, Event/Delta obtienen0%dev en las tres semillas, frente a60,12%±10,53puntos de CryoTiny de referencia. B0full nuevo también obtiene0%. Este contraste no puede omitirse: la rapidez de los candidatos no compensa una capacidad contextual aún no demostrada. Ninguno se promueve como arquitectura oficial ni como alternativa lingüística demostrada aTransformer. El resultado de aprendizaje completo, incluidas tres semillas y ablaciones, se conserva en LEARNING_RESULTS.md; no basta con reducir loss.

## Qué representa mejor cada candidato

**Event** expresa directamente slots latentes y señales de conservación/borrado/escritura/recuperación condicionadas por el estado anterior. Se aproxima más a la formulación conceptual Trapos/Hielo, pero los nombres no garantizan que aprenda relevancia o contradicción. Sus gates dependen del estado y mantienen una cadena secuencial por fragmento. El modo hard omite candidatos reales, aunque fue más lento en el controlCPU y no se entrenó una política discreta de ahorro.

**Delta** separa retención, borrado dirigido y escritura sobre asociaciones. La regla afín admite composición paralela porque sus coeficientes dependen únicamente del fragmento local. Tiene una justificación algebraica más clara para una futura implementación por bloques; el scan denso actual no es un kernel eficiente. La retención impuesta a<0,99 produce olvido, no aislamiento perfecto. Es candidato de ingeniería para investigar, no ganador de capacidad.

En ambos, escribir una vez por fragmento evita reconstruir Hielo en cada token. El estado es acotado en tamaño y la causalidad está probada. La representación de cada token sí sigue procesándose y leyendo memoria; no se obtiene cómputo gratuito.

## Respuestas que permite la evidencia

- Puede conservarse estado y transportarlo sin reconstrucción por token: **sí, mecánicamente**.
- Puede editarse una asociación anterior: **sí en la ecuación/test de edición**, no equivale a haber aprendido a corregir hechos en general.
- Puede influir el segundo plano sobre el primero: **sí**, intervenciones y gradientes lo demuestran.
- Puede Trapos aprender qué conservar/descartar: **no demostrado por este ensayo**. Gates entrenables y valores diferentes no bastan.
- Superioridad frente aB0 con acceso visible equivalente: **no demostrada**. No usar soloB0local, privado del antecedente, como prueba.
- Candidato más rápidoCPU entre Event/Delta en256/b4: Event en la medición realizada. No prueba mejor escaladoGPU o mejor calidad.
- Paso aCUDA: solo como benchmark de ingeniería autorizado posteriormente. Primero conviene una calibración de aprendizajeCPU que pueda discriminar mecanismos; no gastar por una victoria sintética inexistente.

## Limitaciones identificadas, no ocultas

1. Dataset formal de448train/224dev, con generalización conjunta de estructura y combinación entidad/valor. Un lookup condicionado por entidad/consulta fracasa por construcción; los modelos pueden aprender atajos de ese tipo. Es una explicación candidata, no una causa neuronal demostrada.
2. “Hipótesis” no identifica el efecto del borrado: sustituir la hipótesis por una nueva da la misma respuesta aunque se ignore el evento de eliminación. `baseline-diagnostics.json` comprueba esta falta de identificabilidad. No permite afirmar aprendizaje de descarte.
3. No hay lenguaje natural ES/EN, conversación abierta ni evaluación fuera de este DSL. Las siete etiquetas de tarea no constituyen siete facultades independientes.
4. No se igualó entrenamiento porFLOPs; variantes tienen diferentes parámetros/operaciones. Tres semillas pequeñas no bastan para medir ventajas sutiles.
5. No hay feedback de la lectura hacia el resumen que escribe: la adaptación deliberada favorece verificabilidad/scan y puede limitar computación activa.
6. No hay certificadoCUDA/BF16, streaming parcial, memoria externaPA ni entrenamiento del corpus. Ningún resultado hereda certificados de los modelos antiguos.

## Siguiente experimento mínimo, no ejecutado automáticamente

Congelar un **protocolo nuevo** conservando todo este ensayo. Primero añadir como control la clase `Baseline` histórica con exactamente el backbone de CryoTiny, sin cambiar sus pesos ni entrenamientos ya registrados: la diferencia de foreground/FFN/posición impide atribuir el resultado del histórico a su memoria. Ese control aún no se entrenó. Antes de ampliar arquitectura, calibrar B0full y los dos candidatos en un problema de copia asociativa sencillo con combinaciones equilibradas, primero sin distractores. Separar tres evaluaciones: estructuras nuevas con combinaciones vistas; combinaciones nuevas; y ambas nuevas. Mantener las tres semillas, mismos tokens/targets, un baseline simbólico y un control con contexto completo.

Incluir consultas explícitas de ausencia tras borrado, correcciones y correcciones de correcciones; así ignorar un descarte produce una respuesta verificablemente errónea. Cambiar un solo hecho debe cambiar la respuesta correcta y se exige acertar ambos miembros. No retocar este dev para escoger arquitectura.

Presupuesto inicial propuesto: máximo20.000targets por brazo/semilla, tres semillas, seis brazos prioritarios (B0local, B0full, Baseline histórico, Event, Delta, Event sin persistencia, fijado para aislar el transporte de slots). Estimar primero el coste con un preflight, limitarCPUwall a1hora y registrar los brazos omitidos si no cabe. Criterio de instrumentación antes de escalar: B0full debe superar90% en la calibración elemental independiente; si no, investigar tarea/optimización/capacidad antes de atribuir fracaso aHielo. No usar ese90% como certificado lingüístico.

Para afirmar retención útil: comparar contra ablations entrenadas y contexto visible equivalente, publicar exactitud por tarea/semilla, ambas respuestas contrafactuales correctas, coste por respuesta y FLOPs. Exigir reproducción en una segunda familia de datos antes de lenguaje natural. Ampliar después a antecedentes naturales ES/EN con fuentes independientes y contratos del corpus, sin abrir evaluaciones selladas.

No se ejecuta otra extensión de este ensayo ni se alquilaGPU. La hipótesis de aislamiento sigue abierta; sus mecanismos pueden estudiarse sin conservar los errores ni la organización de CryoTiny.

El DSL utiliza solo34IDs distintos y0IDs de merges≥512. Verificar el artefactoV3 y su vocabulario de8192 no significa evaluar sus ventajas lingüísticas ni multiescala en este ensayo. Los fixtures Unicode/conversación solo son tests mecánicos.
