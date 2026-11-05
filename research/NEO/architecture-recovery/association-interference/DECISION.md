# Decisión científica

|Condición|Aux train|CE|Respuesta original|Aux layout nuevo|Respuesta layout|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|A|45.59%|1.2182|99.22%|40.90%|67.50%|22.0|
|B|56.48%|1.0504|28.91%|51.21%|30.00%|22.0|
|C|54.26%|1.0540|41.09%|30.43%|25.62%|26.5|
|D|52.38%|1.0484|25.00%|38.28%|25.00%|24.8|

No se ha aislado una compuerta defectuosa ni justificado rediseñar la arquitectura. Revisar los contadores inicial/postevento: los fallos del decoder después de inicializar dos asociaciones ya limitan cualquier afirmación de interferencia causada exclusivamente por correcciones. Exactitud alta del lector original en condiciones sin corrección puede seguir un hecho inicial: no constituye evidencia de actualización. Las intervenciones vigentes/obsoletos y sus conjuntas son el criterio más fuerte.

No iniciar600updates. Intervención posterior mínima recomendada: un contraste emparejado de supervisión de dos asociaciones en chunk inicial únicamente frente a inicial+posterior, manteniendo mismos ejemplos e igual peso efectivo por target, para separar formación simultánea de bindings de interferencia de entrenamiento sobre etapas. No modificar escritura/lectura/compresión simultáneamente. Requiere autorización posterior.

Una semilla, microfit, layouts desplazados pero no corpus lingüístico. No demuestra utilidad lingüística ni superioridad de Cryo. No se abrió evaluación final.

Respuesta concreta: (1) no se identifica el efecto causal del número de targets anterior; aquí se controla entre cuatro condiciones. (2) La decodificación conjunta de ambas asociaciones iniciales solo alcanza15.3–30.9%, frente a6.25% de azar independiente; hay señal parcial pero no almacenamiento fiable. (3) Tras el evento queda20.3–25.0% conjunta, sin evidencia de preservación y actualización robustas. (4) Fallan representación/decodificación ya al inicio; además B/D fallan en uso funcional del valor vigente. (5) Hay degradación por etapa y layout, compatible con interferencia, pero también dificultad de optimización; una semilla y150updates no separan ambas. (6) No justificar otra arquitectura: aislar primero formación de dos asociaciones de supervisión de actualización. No ejecutar el siguiente contraste automáticamente.
