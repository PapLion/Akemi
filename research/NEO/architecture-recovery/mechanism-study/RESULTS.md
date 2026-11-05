# Resultados de ablación

Todos los finales a1000updates; no mejor checkpoint. Control intacto reproducido desde evidencia original. Semillas faltantes se mantienen pendientes.

| Brazo |17|29|43|Media dev|SD pp|Train media|
|---|---:|---:|---:|---:|---:|---:|
|intact|49.11%|61.16%|70.09%|60.12%|10.53|75.37%|
|chunk2|66.52%|39.73%|13.84%|40.03%|26.34|66.29%|
|delta|35.27%|61.16%|58.04%|51.49%|14.13|72.32%|
|depth1|1.79%|74.11%|63.39%|46.43%|39.03|65.62%|
|detach|25.00%|71.88%|70.98%|55.95%|26.81|69.79%|
|event|29.02%|58.93%|45.09%|44.35%|14.97|73.81%|
|no_filter|0.00%|62.95%|64.73%|42.56%|36.87|55.43%|
|no_ice|57.14%|71.88%|62.50%|63.84%|7.46|70.98%|
|transformer|22.32%|48.66%|44.20%|38.39%|14.10|77.46%|
|capacity_transformer|43.75%|49.11%|65.18%|52.68%|11.15|78.42%|
|delta_fast|70.09%|54.91%|62.95%|62.65%|7.59|69.57%|
|event_fast|54.46%|62.95%|62.95%|60.12%|4.90|68.08%|
|delta_matched|0.00%|60.27%|63.84%|41.37%|35.87|64.14%|
|event_matched|1.34%|47.32%|48.21%|32.29%|26.81|64.06%|

`results/summary.json`, `curves.csv`, checkpoints y predicciones completas permiten inspeccionar cada caso. Dev es generalización composicional simbólica, no lenguaje natural. SD es entre tres semillas, no intervalo de confianza sobre otros corpus.
