# Atención real: embeddings, Q, K y logits

Se extraen tensores del modelo real, no estados simulados. inspect_attention reconstruye Q/K con RoPE desde los pesos y comprueba el resultado de la atención manual frente al input real de o en scaled_dot_product_attention (atol2e-6,rtol1e-5, fijadas antes de ejecutar). Se guardan embedding final, Q final, K de hechos, atención normalizada, masa por hecho/cabeza y logits en attention-before.pt/attention-after.pt. JSON de todos los paneles conserva diagnósticos por historia, no solo ejemplo favorable.

| Medida pareja Nora/Iris misma historia |A inicial|B inicial|A final|B final|
|---|---:|---:|---:|---:|
| Delta máximo Q |0|0.271961|0|0.777733|
| Delta K hechos |0|0|0|0|
| Delta atención factual relativa |2.23517e-08|0.00265335|1.49012e-08|0.146884|
| Delta logits |0.00414675|0.627946|1.62125e-05|0.220516|

Q distinta y atención distinta NO equivalen a recuperar correctamente un valor. B responde igual a ambas entidades entrenadas en24/24historias. En Nora/Mira da tokens diferentes según entidad pero0%conjunta: no demuestra binding, y CE sube9,53939. Es sensibilidad a identidad sin la relación correcta.

Orden real de operaciones: embedding → RMSNorm → Q/K/V por token → RoPE → atención causal → residual → MLP por token → dos refinamientos rápidos normalizados por token → slow_norm → LM head compartido con embedding. Hay UN bloque de atención; las operaciones posteriores no hacen otra atención entre posiciones. Al final B tiene identidad en Q, pero las K/V de un token de valor todavía no incorporan la entidad que lo precede. El Jacobiano de la K de un color respecto a embeddings de otros tokens es exactamente0 en ambos checkpoints (diagnóstico ejecutado). Esto caracteriza una restricción del mecanismo; no es prueba de incapacidad absoluta de mezclar información vía capas no lineales ni identifica una causa única del fallo.

Las consultas y hechos están causalmente antes del target. Las etiquetas no participan en el forward. La igualdad Q de A no impedía toda influencia de la consulta: había gradientes y pequeñas diferencias de logits. El experimento refuta que cambiar solo el token final sea suficiente bajo esta receta, no que el modelo nunca pueda aprender.
