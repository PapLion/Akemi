# Resultados

|Brazo / split|Inicial rol A|Inicial rol B|Conjunta inicial|Conjunta posterior|Conjunta retenida|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A / train|40.00%|43.75%|16.25%|13.75%|13.75%|35.94%|
|A / dev-layout|43.12%|41.88%|14.37%|14.69%|12.50%|35.94%|
|B / train|44.38%|47.50%|15.00%|15.00%|11.56%|32.81%|
|B / dev-layout|45.62%|45.62%|14.37%|13.75%|11.88%|31.56%|

Todos los entrenamientos150updates,1200secuencias muestreadas con reemplazo;640instancias de targets iniciales por fixture,1280incluyendo etapa posterior; no son640 asociaciones independientes únicas. Son programas sintéticos correlacionados, no1200ejemplos independientes nuevos. Curvas y normas por tensor en A/B-curves.json; modelos/AdamW/RNG/cursor en checkpoints0/75/150. CE inicial rolA/rolB train: A (1.2744988948106766, 1.2868228999897837); B (1.2606934728100896, 1.2829170774668455).

Tiempos de entrenamiento sin evaluación: A 10.949622639000154s; B 12.439758657998027s. No son benchmarks CPU extensos. Confusiones por entidad y valor, predicciones por documento, CE individual y métricas preserve/correct completas en *evaluation.json.
