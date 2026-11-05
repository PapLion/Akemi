# Contrafactuales y uso funcional

|Semilla|Brazo|Familia|Pareja obsoleto correcta|Invariancia obsoleto|Pareja vigente correcta|Invariancia vigente|
|---|---|---|---:|---:|---:|---:|
|17|A|correction_fixed|78.33%|97.19%|63.02%|9.48%|
|17|A|correction_layout|100.00%|100.00%|100.00%|0.00%|
|17|B|correction_fixed|97.29%|97.50%|96.88%|1.56%|
|17|B|correction_layout|100.00%|100.00%|100.00%|0.00%|
|29|A|correction_fixed|76.67%|90.94%|61.56%|19.06%|
|29|A|correction_layout|100.00%|100.00%|100.00%|0.00%|
|29|B|correction_fixed|88.75%|96.46%|84.69%|11.15%|
|29|B|correction_layout|100.00%|100.00%|100.00%|0.00%|
|43|A|correction_fixed|60.42%|85.62%|50.31%|19.38%|
|43|A|correction_layout|95.00%|95.00%|91.67%|3.33%|
|43|B|correction_fixed|91.25%|98.02%|87.50%|10.83%|
|43|B|correction_layout|100.00%|100.00%|100.00%|0.00%|

Cada pareja altera solo el hecho obsoleto o el vigente y reconstruye el target con el oráculo. Si se corrige la otra entidad, el vigente de la consulta sigue siendo su escritura inicial: modificarlo debe cambiar la respuesta. Se reportan acierto conjunto e invariancia separadamente; no confundir cambiar de predicción con cambiar a la correcta.

Intercambios de formación:120parejas de valores distintos por modelo. Los JSON contienen criterio estricto de bindings y de respuestas normales, no solo marginales. Consultar ambas entidades separadamente también se registra.

Ablaciones de inferencia:reset y swap compatible antes del último chunk. El compañero mantiene entidades,orden,layout y valor de otra entidad,pero cambia el valor consultado al siguiente. Sin acceso al prefijo en foreground: máscara local16,consulta enIDs60..63,correcciones de familias principales≤43 y demás hechos previos a48. No KV cache ni estados entre llamadas. Las consultas dependen del estado declarado. Se conservan métricas de exactitud,de cambio de predicción y de seguir al compañero.

No se usa el decoder auxiliar en estas respuestas normales. No se atribuye filtrado aprendido a la escritura sintáctica determinista.
