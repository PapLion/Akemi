# Foreground Distribution Scaling V1

Contraste factorial ejecutado: cuatro brazos de400 updates, seed17, CPU FP32, mismo foreground de dos capas, inicialización, tokenizer, pérdida original y AdamW. Sin Hielo/Trapos.

|Brazo|Valores/órdenes|Respuestas únicas|Accuracy|Conjunta|Intercambios|CE|CE/H(etiqueta)|Azar marginal|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|A|2/1|4|100.00%|100.00%|1/1|0.000007|0.000010|50%|
|B|4/1|24|75.00%|50.00%|3/6|0.310159|0.223733|25%|
|C|2/2|8|50.00%|0.00%|0/2|0.693158|1.000016|50%|
|D|4/2|48|35.42%|0.00%|0/12|1.300943|0.938432|25%|

**Decisión: solo A supera el microfit; la variación de orden es el obstáculo más claro bajo esta receta. B aprende parcialmente.** No demuestra causalidad exclusiva ni incapacidad del modelo. Ver DECISION.md y FACTORIAL_ANALYSIS.md.

D reproduce exactamente pesos y AdamW del nivel4 histórico; A en300 reproduce nivel3. No se ejecutaron nuevas recetas, semillas ni entrenamientos después del factorial. Tres tests CPU PASS; checkpoints completos, logits/predicciones, curvas, frecuencias, auditoría y hashes conservados. Reproducción en copia limpia mediante reproduce.sh; el script rechaza sobrescribir resultados. Origen17111e7; datos sintéticos EN controlados, sin evaluaciones selladas.
