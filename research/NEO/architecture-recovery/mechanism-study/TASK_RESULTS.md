# Exactitud por tarea

Media de tres semillas a1000updates; cada tarea tiene32ejemplos dev por semilla.

|Brazo|constraint|correction|entities|goal|hypothesis|irrelevance|retention|
|---|---:|---:|---:|---:|---:|---:|---:|
|intact|91.67%|4.17%|78.12%|90.62%|2.08%|79.17%|75.00%|
|no_filter|57.29%|1.04%|61.46%|58.33%|3.12%|55.21%|61.46%|
|detach|79.17%|3.12%|80.21%|72.92%|4.17%|75.00%|77.08%|
|transformer|62.50%|3.12%|45.83%|71.88%|2.08%|42.71%|40.62%|
|depth1|62.50%|6.25%|62.50%|63.54%|2.08%|63.54%|64.58%|
|event|70.83%|5.21%|50.00%|76.04%|2.08%|53.12%|53.12%|
|delta|80.21%|1.04%|65.62%|79.17%|2.08%|66.67%|65.62%|
|chunk2|56.25%|3.12%|53.12%|56.25%|3.12%|52.08%|56.25%|
|no_ice|93.75%|4.17%|86.46%|96.88%|4.17%|80.21%|81.25%|
|capacity_transformer|77.08%|0.00%|78.12%|76.04%|4.17%|70.83%|62.50%|
|event_matched|52.08%|0.00%|42.71%|60.42%|0.00%|38.54%|32.29%|
|delta_matched|64.58%|1.04%|52.08%|65.62%|2.08%|55.21%|48.96%|
|delta_fast|83.33%|3.12%|87.50%|82.29%|7.29%|89.58%|85.42%|
|event_fast|82.29%|3.12%|85.42%|89.58%|2.08%|82.29%|76.04%|

Predicción del primer hecho, incluido cuando contradice la respuesta correcta: ver JSON. La media global no demuestra corrección de información.
