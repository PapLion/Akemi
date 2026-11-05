# Evaluación F2 congelada antes del entrenamiento

Estado: el entrenamiento completo NO está autorizado ni ejecutado. Checkpoint final fijo a5.000.000 targets; no elegir por muestras de generación. F2 y Transformer usan los mismos IDs BPE8K, documentos, orden, posiciones supervisadas y presupuesto. Contexto inicial128; sensibilidad128/256 evaluada con las mismas posiciones de texto y máscaras. Hielo/Trapos OFF. Semilla17; CPU FP32 como referencia.

- NLL/exp(NLL) ponderadas por targets válidos, train/dev y por idioma, dominio, fuente. Publicar denominadores; no crear una cifra de español si no existe dev aprobado en español.
- Curvas a0/1M/2M/3M/4M/5M targets vistos, mismos puntos para ambos modelos. Registrar targets únicos y exposiciones separadamente. Dev sin gradientes; no usar su contenido para escribir/train.
- Splits por documento y familia; no partir un documento entre train/dev. Heredar reservas históricas de evaluación. Deduplicar contenido exacto/normalizado y near-duplicates/versiones antes de exportar; conservar evidencia de decisiones.
- Reportar gap train/dev, overlap por shingles y continuaciones copiadas largas contra train; son indicadores, no garantía de ausencia de memorización. Referencias de benchmarks no certificadas mantienen su propia compuerta.
- Prompts fijos: «La historia de la ciudad», «El agua y la energía», «The purpose of this function», «def calculate_total(». Greedy y sampling temperatura0.8/top-k40 con seed17,64 tokens, sin elegir mejores ejemplos. Publicar todas las salidas, diversidad de2/3-gramas, repeticiones y EOS.
- Medir targets/s, tiempo, RAM, checkpoint/restore e I/O por modelo. Parámetros diferentes y FLOPs heurísticos declarados; presupuesto igual de targets no significa cómputo igual.

Las regresiones simbólicas anteriores no son el criterio principal de calidad. Los conjuntos sellados históricos y confirmatorios permanecen cerrados. Este protocolo no promete capacidad conversacional ni comprensión general.
