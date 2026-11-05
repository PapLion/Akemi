# Requisitos concretos restantes

1. Resolver para Wikipedia el alcance de uso/licencia previsto y las excepciones/atribuciones externas de los artículos candidatos. Se dispone de URL, título, ID, shard/fila, hash y revisión HF; falta evidencia histórica por artículo o una revisión documentada suficiente que determine qué avisos externos se requieren. No basta marcar una casilla genérica por dominio. Si no puede recuperarse esa evidencia, excluir el documento afectado y reemplazarlo por otro ya existente y revisable. La decisión sobre obligaciones de modelos/redistribución no la inventa el agente.
2. Tras ello, registrar aprobación individual y conservar créditos/licencia/modificaciones. El déficit aprobado actual es4.974.645targets; el volumen candidato supera ese déficit. No hace falta descargar otro corpus ni terminar el conteo maestro V3 para evaluar este subconjunto.
3. Revisar near-duplicates/contaminación de la selección ya identificada sin abrir conjuntos sellados y congelar splits admitiendo las limitaciones de EN/ES relacionadas. No repetir la auditoría de integridad original.
4. Con el manifest aprobado, certificar streaming del lector a esa escala y corte exacto máximo5M, fijar frecuencia de evaluación/checkpoints y presupuesto global. El lector aprobado pequeño ya tiene reanudación exacta certificada; no atribuir esa prueba automáticamente a millones de tokens candidatos.

Web/FineMath exigen evidencia por fuente subyacente y OASST exige trabajo de transformación/privacidad; no son el camino mínimo para cerrar el déficit. No iniciar otro ciclo de recopilación.
