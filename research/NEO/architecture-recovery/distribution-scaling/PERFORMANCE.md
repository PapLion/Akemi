# Coste CPU

|Brazo|Updates/supervisión|Segundos updates|Targets/s|RAM pico proceso MiB|
|---|---|---:|---:|---:|
|A|400 /3200|12.168|262.99|703.34|
|B|400 /3200|12.052|265.52|707.95|
|C|400 /3200|11.924|268.36|710.34|
|D|400 /3200|11.891|269.11|719.35|

Mismo modelo299.520 parámetros totales,296.160 activos; contexto train119 IDs válidos/padding128;380.800 IDs de entrada por brazo y un target por respuesta. Normas de gradientes registradas dentro del timing, evaluación y checkpoints fuera de seconds_train_updates_only. El tiempo con evaluación de curvas también se registra. RAM es high-water de un proceso secuencial, no pico aislado comparable por brazo. Sin mediciones CUDA ni extrapolación de costes de pretraining.

Igual número de targets/updates y longitud de entrada no significa igual diversidad ni iguales pasadas por cada ejemplo. No se intentó amortizar cómputo con modificaciones del modelo.
