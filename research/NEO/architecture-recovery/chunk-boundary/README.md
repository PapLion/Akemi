# Cryo: límite de chunk y dos asociaciones

Origen1376df2; rama/worktree cryo-chunk-boundary-v1. DeltaFast17 inmutable, CPU FP32, dos brazos150updates. Sin GPU, gastos, corpus, A4, tokenizer ni finales sellados.

|Condición / split|Entidad A|Entidad B|Conjunta|Producto marginales|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|---:|
|same / train|25.00%|25.00%|6.25%|6.25%|1.3857|1.3900|25.00%|
|same / dev|25.00%|25.00%|6.25%|6.25%|1.3861|1.3902|25.00%|
|separate / train|53.12%|52.50%|21.88%|27.89%|1.2257|1.2134|30.00%|
|separate / dev|52.50%|50.62%|20.62%|26.58%|1.2422|1.2304|30.00%|

Las escrituras separadas mejoran respecto a agruparlas, pero ambos fallan el criterio de microfit fiable y la prueba fuerte de intercambio de valores. La diferencia es exploratoria de una semilla; no prueba causa única ni incapacidad de Hielo. Se cierra la serie de microfits equivalentes bajo esta receta. Ver DECISION.md.

Código: chunk_study.py (contratos/control/entrenamiento), analyze_chunks.py, report_chunks.py. Artefactos completos, checkpoints y estados reales en results/.
