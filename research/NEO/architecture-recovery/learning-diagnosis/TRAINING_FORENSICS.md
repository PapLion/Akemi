# Forense de entrenamiento histórico

Se cargaron en modo weights_only los checkpoints inicial/final de A/B/C, sin modificar sus pesos. Logits completos8192 por respuesta de train y ambos devs se guardan en forensic-*.pt; resumen por respuesta con los cuatro logits/probabilidades válidos en forensics.json.

|Brazo histórico|CE inicial→final train|P correcta media final|Masa media en cuatro valores|Predicciones finales por ID|
|---|---:|---:|---:|---|
|A|8.989491 → 1.232938|0.323283|0.998450|{'5927': 14, '3973': 24, '5074': 10}|
|B|8.994885 → 1.300943|0.279735|0.999447|{'5074': 28, '5927': 20}|
|C|8.989097 → 1.182794|0.333903|0.999220|{'5927': 24, '3973': 24}|

La pérdida disminuye sustancialmente, principalmente aprendiendo a concentrar masa en valores válidos; esto no certifica asociación condicionada. B termina prediciendo solo2 valores; A3, C2. Las dos consultas ya generan logits distintos: máximos por historia B entre0,558955 y3,703584. Diferencias numéricas no garantizan respuestas correctas.

Último minibatch B antes del update400: CE1,174197; mismo batch después:1,193752. Train completo después:1,300943. Media de los últimos6 minibatches, medidos con pesos cambiantes:1,260101. No son medidas equivalentes. La evaluación completa coincide con la media de seis batches evaluados con pesos fijos; no hay discrepancia de modo dropout (0).

Cobertura AdamW exacta en los tres brazos; LR y decay correctos; todos los activos reciben gradientes. El target es el siguiente token después de la consulta, no entra al forward. CE se promedia sobre respuestas, no sobre8192 tokens ni sobre el prefijo.

No existen checkpoints históricos intermedios con logits completos: no es posible reconstruir su trayectoria sin reentrenar. Se preservan curvas históricas CE/gradientes, y la escalera nueva guarda logits completos en updates1, cada25 y final. Deltas de todos los parámetros, gradientes iniciales/finales y configuración AdamW están registrados. No se declara causa de aprendizaje por descarte.
