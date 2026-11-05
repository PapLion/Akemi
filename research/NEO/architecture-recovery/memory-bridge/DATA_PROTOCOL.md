# Datos y objetivo congelados

protocol.json se fijó antes del microfit: CPU FP32, semilla17, batch8, AdamW(.003, betas .9/.95, weight_decay .01), clipping1, modelo width32/chunk16.400updates por brazo principal como máximo;200updates de microfit independiente, sin reutilizar sus pesos en brazos principales. Selección de checkpoint: último paso fijo, sin elección por dev.

Los programas se generan por producto cartesiano de dos entidades, cuatro valores independientes, dos idiomas, ambos órdenes, condición inicial/corrección y tres transiciones no idénticas. Se consulta a ambas entidades; la corrección afecta una y la otra debe conservarse. Ninguna etiqueta, nombre de entidad oracular o valor esperado se pasa como índice al modelo: recibe exclusivamente tokens de hechos, distractores y pregunta. Los nombres son texto normal tokenizado por V3.

- Train: pares Nora–Iris y Mira–Luna, redacción0, distancias96/128;2048respuestas/1024programas.
- Dev combinaciones: Nora–Mira e Iris–Luna, redacción0, distancia96;1024respuestas/512programas.
- Dev estructuras: pares de train, redacciones1/2 y distancia160;2048respuestas/1024programas. Aquí cambian conjuntamente redacción y distancia: no atribuir un efecto exclusivamente a una.
- Microfit separado: Nora–Iris, EN,16pares de valores y ambas consultas, sin corrección,32respuestas. Su cometido es memorizar la tarea antes de estudiar generalización. No es un dev independiente.
- Confirmatorio: pares reservados Nora–Luna e Iris–Mira, redacciones1/2, distancia192,1024ejemplos. Cuerpo escrito en sealed/CONFIRMATORY.jsonl con permisos0400 y hash calculado al escribir; no se cargó ni evaluó. La receta usa enumeración cartesiana, sin muestreo RNG; el número de semilla reservado en metadatos no se utilizó para generación.

Cada respuesta es una palabra de un token: EN red/white/black/gold; ES rojo/azul/verde/negro. Son etiquetas lingüísticas distintas por idioma, no traducción uno a uno. Igual presupuesto de respuestas y targets elimina confusión de longitud de respuesta. Se conserva la palabra completa, sin recodificar a IDs DSL ni limitar el vocabulario de salida.

Se comprueba balance exacto de cuatro respuestas condicionado por pregunta/entidad/idioma; tablas desde los targets reales en data-manifest.json. Todos los pares valor–valor están presentes; queries de train/dev son disjuntas por programa/pares/layout. Los hechos completos preceden al menos16tokens neutrales; se añaden frases neutrales completas y padding byte-espacio hasta frontera96/128/160, nunca se recorta un hecho ni un documento externo. Es una conveniencia de ingeniería declarada, no extracción de acontecimientos semánticos.

El distractor es contenido neutro más la asociación de otra entidad; no se cubre todavía una tercera entidad adversarial ni lenguaje libre. Textos sintéticos compuestos durante esta sesión por el generador, procedencia en código/hashes. Ninguna fuente externa, documento privado, Chinchilla ni evaluación histórica. Datos de borrador previos al freeze de entrenamiento quedan preservados en results/draft-v0, excluidos de los resultados y de git. No se ajustó ningún dato después de observar el microfit.
