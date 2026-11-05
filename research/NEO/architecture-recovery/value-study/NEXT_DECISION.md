# Decisión técnica mínima

**Conservar las arquitecturas y los checkpoints. Priorizar la supervisión de asociación en la ruta de escritura/conservación. No añadir recuperación asociativa nueva ni cambiar simultáneamente compresión, borrado y atención.**

Razón: los valores existen en la entrada, el resumen híbrido conserva parte de ellos, pero la decodificación de memoria no es robusta y la lectura original no sigue estados contrafactuales. Un readout nuevo por sí solo no resuelve las pruebas estructurales. Las compuertas actuales tampoco tienen evidencia de selección útil de valores.

## Un solo piloto correctivo propuesto, no ejecutado

Usar dos copias descartables del mismo checkpoint DeltaFast semilla17. Mismo panel balanceado, programas/órdenes,600updates máximos,batch8,CPU,lr0.003,clip1; control con pérdida final original y tratamiento con **única diferencia de supervisión**: pérdida auxiliar de valor vigente por entidad después de una escritura aceptada. Decoder lineal condicionado por entidad de capacidad prefijada, idéntico en ambos brazos; en control queda fuera de la pérdida original, se audita cobertura/freeze explícito. No añadir un módulo al forward de inferencia.

`L = L_respuesta + 0.1 * L_asociación`, sin escoger lambda según dev. Etiquetas auxiliares de oráculo causal de prefijo, jamás estado final/futuro sobre un fragmento anterior. Ausencia usa máscara o clase explícita fijada antes; no mezclar ambos. Los ejemplos de corrección genuina y parejas obsoleto/vigente se mantienen agrupados por split. El primer microfit limitado debe acreditar almacenamiento de cuatro valores para cada entidad antes de ampliar.

Medir primero estado después de escritura y antes de consulta, contrafactuales genuinos, exactitud por tarea y coste; comparar lectura original y probe congelado con el mismo presupuesto. Éxito exige que **el modelo original**, no solo el decoder auxiliar, responda a cambios válidos sin seguir obsoletos, en ambos splits estructurales. Si mejora únicamente el probe, se habrá enseñado almacenamiento y seguirá pendiente lectura. Si no mejora escritura, revisar representación/compresión bajo ese resultado; no añadir otra arquitectura como reacción automática.

Parada: NaN/Inf, gradientes ausentes, causalidad rota, o microfit que no reduce pérdida auxiliar de forma verificable. No ejecutar600updates a ciegas si falla la compuerta mecánica. Una semilla identifica un mecanismo candidato, no superioridad estadística; confirmar luego con semillas nuevas solo si supera controles. El final sellado permanece intacto.

Esta sesión no ejecutó ese piloto porque las causas escritura/representación/generalización siguen parcialmente mezcladas. Se han ejecutado decoders y controles reales, no se ha simulado que la supervisión auxiliar ya funciona. El siguiente experimento cambia exclusivamente esa señal de aprendizaje y puede responder una pregunta concreta: ¿la falta de presión explícita para conservar bindings explica el fracaso end-to-end?
