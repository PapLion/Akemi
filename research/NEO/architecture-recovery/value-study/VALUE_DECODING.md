# Decodificación de Hielo con pesos originales congelados

Exactitud dev; train y estructural, curvas y predicciones completas en results/probes y CSV. Azar de valor25%, presencia/corregida50%. Cada decoder tiene cabezas separadas por entidad; no necesita inferir la consulta. No se selecciona el mejor hiperparámetro sobre dev. Se publican lineal y MLP32 fijados antes de medir.

|Estado|Tipo|Presencia lineal|Valor lineal|Valor MLP|Inicial lineal|Corregida lineal|
|---|---|---:|---:|---:|---:|---:|
|delta_fast-17-always-trained.pt|Hielo antes de consulta|100.00|27.19|27.19|26.88|51.25|
|delta_fast-17-normal-initial.pt|Hielo antes de consulta|100.00|34.06|34.69|40.62|50.31|
|delta_fast-17-normal-trained.pt|Hielo antes de consulta|100.00|30.63|27.50|33.75|53.91|
|delta_fast-17-random-trained.pt|Hielo antes de consulta|58.59|26.88|25.62|25.31|51.88|
|delta_fast-29-always-trained.pt|Hielo antes de consulta|100.00|25.31|28.44|27.81|67.03|
|delta_fast-29-normal-initial.pt|Hielo antes de consulta|100.00|41.87|40.00|45.31|59.38|
|delta_fast-29-normal-trained.pt|Hielo antes de consulta|95.31|31.56|29.06|37.50|58.91|
|delta_fast-29-random-trained.pt|Hielo antes de consulta|60.94|25.00|26.88|25.00|49.69|
|delta_fast-43-always-trained.pt|Hielo antes de consulta|100.00|27.81|25.94|30.63|68.59|
|delta_fast-43-normal-initial.pt|Hielo antes de consulta|100.00|37.81|37.19|45.63|60.16|
|delta_fast-43-normal-trained.pt|Hielo antes de consulta|100.00|25.94|25.31|25.00|48.28|
|delta_fast-43-random-trained.pt|Hielo antes de consulta|60.16|25.94|24.69|23.44|50.63|
|event_fast-17-normal-initial.pt|Hielo antes de consulta|100.00|54.37|32.50|25.31|83.91|
|event_fast-17-normal-trained.pt|Hielo antes de consulta|100.00|33.44|33.13|34.38|52.03|
|event_fast-29-normal-initial.pt|Hielo antes de consulta|100.00|57.50|42.50|25.00|85.62|
|event_fast-29-normal-trained.pt|Hielo antes de consulta|100.00|34.06|32.81|35.94|57.50|
|event_fast-43-normal-initial.pt|Hielo antes de consulta|100.00|43.13|36.88|25.00|66.41|
|event_fast-43-normal-trained.pt|Hielo antes de consulta|100.00|30.31|27.50|25.31|58.13|
|intact-17-normal-initial.pt|Hielo antes de consulta|100.00|27.50|27.50|25.00|61.87|
|intact-17-normal-trained.pt|Hielo antes de consulta|100.00|32.50|34.69|27.19|66.41|
|intact-29-normal-initial.pt|Hielo antes de consulta|100.00|22.50|25.00|25.00|66.25|
|intact-29-normal-trained.pt|Hielo antes de consulta|100.00|30.63|28.44|24.69|49.53|
|intact-43-normal-initial.pt|Hielo antes de consulta|100.00|37.50|35.00|25.00|66.25|
|intact-43-normal-trained.pt|Hielo antes de consulta|100.00|25.94|26.88|26.56|57.34|

## Controles

|Control|Tarea|Dev lineal|
|---|---|---:|
|explicit|presence|100.00|
|explicit|value|100.00|
|explicit|old|100.00|
|explicit|corrected|100.00|
|presence_only|presence|100.00|
|presence_only|value|25.00|
|presence_only|old|25.00|
|presence_only|corrected|50.00|

Etiquetas permutadas solo en TRAIN: control negativo sin alterar la verdad dev. Resultados por checkpoint en CSV; tasas altas en train no cuentan como generalización. Inicialización aleatoria comparte algoritmo y capacidad, no es una memoria nula. MLP y decoder condicional pueden extraer información que el modelo original nunca usa. Una exactitud cercana al azar no prueba ausencia de todo código no lineal.
