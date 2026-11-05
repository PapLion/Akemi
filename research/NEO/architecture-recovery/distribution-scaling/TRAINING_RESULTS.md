# Ajuste del fixture

|Brazo|Valores/órdenes|Respuestas únicas|Accuracy|Conjunta|Intercambios|CE|CE/H(etiqueta)|Azar marginal|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|A|2/1|4|100.00%|100.00%|1/1|0.000007|0.000010|50%|
|B|4/1|24|75.00%|50.00%|3/6|0.310159|0.223733|25%|
|C|2/2|8|50.00%|0.00%|0/2|0.693158|1.000016|50%|
|D|4/2|48|35.42%|0.00%|0/12|1.300943|0.938432|25%|

|Brazo|Por entidad 0/1|Predicciones idénticas|Colores predichos|P correcta media|Clipping|
|---|---|---:|---|---:|---:|
|A|100.00% / 100.00%|0/2|{'2426': 2, '5927': 2}|0.999993|16.00%|
|B|75.00% / 75.00%|2/12|{'2426': 12, '5927': 6, '3973': 6}|0.770746|90.75%|
|C|50.00% / 50.00%|4/4|{'2426': 8}|0.499998|11.75%|
|D|33.33% / 37.50%|16/24|{'5074': 28, '5927': 20}|0.279735|87.75%|

A aprende ambos valores en ambas consultas y el intercambio de su único par. B aprende tres valores (red/white/black100%) y falla gold0%; son6 errores de24, no azar uniforme. C predice red en8/8 consultas; su softmax sigue casi uniforme entre red/white (P correcta media0,499998), por tanto es colapso de argmax sin confianza informativa, no certeza de que todo sea red. D predice solo black/gold, con16/24 historias de respuesta idéntica.

Curvas de ajuste completo: A alcanza100% en el corte150 y se mantiene; B sube de25% (200) a50% (250/300) y75% (350/400); C permanece50% en todos los cortes50–400; D solo mejora de25% a35,42% al final. No se extiende el presupuesto para seguir las curvas. Gradientes por tensor antes de clipping y CE minibatch se guardan en cada update; métricas completas post-update cada50 con logits completos.

No confundir CE minibatch previa al update con evaluación completa posterior. Resultados finales fijos, sin selección de checkpoint por dev. Una semilla; sin intervalos de robustez entre semillas ni prueba estadística de superioridad.
