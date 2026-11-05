# F2 BLOQUEADO — no listo para autorización de entrenamiento

Se avanzó materialmente: clasificación individual de31.447artículos Wikipedia, identidad de card HF cerrada byte a byte, atribución por artículo candidato, conteo exacto bilingüe y lector aprobado con reanudación exacta. Los candidatos suman5.006.879targets train +212.105dev. No son datos aprobados. La selección aprobada permanece en25.355train +8.637dev; faltan4.974.645targets independientes aprobados.

No se convirtió una licencia genérica en aprobación por documento, ni se resolvió por suposición una cuestión jurídica sobre modelos. Wikipedia sigueCONDITIONAL por excepciones/atribución externa y alcance del uso; otras familias web/math siguenQUARANTINED; CPythonEXCLUDED por reserva; SFT separado. Se preservaron todos los originales y no se entrenó F2.

La barrera principal ahora es documental/de derechos, seguida de congelar la selección aprobada y certificar su lector escalado. No faltan5Mtokens candidatos, otro tokenizer, otro modelo ni una auditoría integral repetida. El conteo exhaustivo del maestro no es necesario para este piloto si se cierra el release seleccionado. No se afirma READY ni comprensión lingüística.

El siguiente trabajo mínimo es resolver condiciones para estos artículos concretos, no descargar más datos. Tras resolverlas, aplicar el corte presupuestario y completar lector/evaluación; después solicitar autorización para entrenar. Ver REMAINING_BLOCKERS.md y results/gates.json para cada compuerta.
