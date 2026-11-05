# CryoCCM — Query Conditioning V1

Contraste ejecutado en CPU FP32, dos brazos de200updates, semilla17. Único cambio: mover los dos IDs de la entidad desde el medio al final de la consulta. Misma historia, multiconjunto de tokens, longitud, posición de predicción, target, inicialización, receta y orden. Sin Hielo ni Trapos; foreground y V3 intactos.

| Formato | Train respuesta/conjunta | Dev pares nuevos | Dev layout nuevo | Swaps estrictos dev |
|---|---|---|---|---|
| A: token final común |25% /0%|25% /0%|25% /0%|0/12|
| B: entidad final |25% /0%|12,5% /0%|25% /0%|0/12|

**La intervención cambia Q y atención, pero no enseña binding funcional. Compuerta FAIL; distancia larga NO EJECUTADA.** No semillas adicionales, no aumentos de capacidad ni updates. Se cierra esta familia de microfits y se detiene la investigación de Hielo lingüístico hasta disponer de un foreground con recuperación certificada.

Ver DECISION.md, QUERY_DIAGNOSTICS.md y COMPARISON.md. Datos, curvas, logits/Q/K reales, predicciones y checkpoints guardados en results/. Archivos .pt locales (no versionados) identificados en SHA256SUMS/ARTIFACT_MANIFEST.json. Código y pruebas reproducibles, no publicaciones ni merge automático.

Pruebas sin nuevos entrenamientos principales: usar el Python local de reproducibilidad para ejecutar query-conditioning/tests.py. Reproducción completa: bash query-conditioning/reproduce.sh en worktree nuevo con results vacío; se rechaza sobrescribir. El procedimiento respeta el gate y no ejecuta largo si B falla. No abrir el confirmatorio V2.
