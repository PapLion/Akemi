# Resultados completos

CPU FP32. Porcentajes a corte final prefijado, sin elegir el mejor checkpoint. Diferencias de visibilidad y parámetros se informan; no son presupuestos FLOPs iguales. Las filas con una semilla no tienen dispersión estimable.

|Modelo/ventana/modo|Semillas|Train|IID|Composición|Estructura|Ambos|IID fuera|Estructura fuera|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|delta_fast/16/normal|17,29,43|75.28 ± 5.44|70.69 ± 4.74|10.21 ± 0.36|71.67 ± 3.15|10.00 ± 1.65|50.28 ± 4.74|52.50 ± 0.83|
|event_fast/16/normal|17,29,43|76.88 ± 2.05|69.31 ± 5.24|8.33 ± 3.44|68.47 ± 1.27|9.38 ± 1.65|48.89 ± 5.85|45.56 ± 3.76|
|intact/16/normal|17,29,43|73.75 ± 3.55|65.14 ± 7.17|9.17 ± 1.44|67.22 ± 7.92|9.17 ± 1.44|38.06 ± 9.14|41.39 ± 7.74|
|no_ice/16/normal|17,29,43|69.10 ± 1.77|64.31 ± 1.05|7.50 ± 4.33|63.33 ± 2.92|7.92 ± 5.05|33.61 ± 5.91|31.39 ± 2.68|
|transformer/0/normal|17,29,43|69.51 ± 7.18|56.53 ± 6.24|22.92 ± 23.46|54.86 ± 6.07|23.75 ± 27.62|40.83 ± 10.41|37.22 ± 10.08|
|transformer/16/normal|17,29,43|76.94 ± 1.27|67.92 ± 4.23|9.17 ± 1.57|64.31 ± 2.55|9.79 ± 1.91|40.28 ± 4.59|34.17 ± 2.89|
