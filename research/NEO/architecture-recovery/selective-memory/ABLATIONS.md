# Ablaciones de escritura desde entrenamiento

Delta elegido en el piloto por17/45 frente a16/45Event; diferencia exploratoria de un ejemplo. Misma inicialización, foreground, IDs, receta y1000updates. Sin lectura equivale al control entrenado noHielo bajo las ecuaciones y tolerancias verificadas; no se duplican sus tres entrenamientos. Reset/intercambio son intervenciones de inferencia, no entrenamientos sin memoria.

|Política|Semilla|Train|IID|IID fuera|Estructural fuera|Correcciones puras correctas /42|Segundos updates|
|---|---:|---:|---:|---:|---:|---:|---:|
|always|17|76.04|69.58|48.33|45.00|0|74.1|
|always|29|73.33|70.42|50.83|51.67|0|74.0|
|always|43|73.75|68.33|46.67|52.50|0|79.9|
|random|17|72.08|67.92|35.83|30.83|0|74.4|
|random|29|65.00|58.75|32.50|36.67|0|75.8|
|random|43|64.38|58.33|30.83|30.83|0|74.8|

Always fuerza solo el coeficiente aditivo de escritura a1; retención/borrado y recuperación siguen aprendiendo. No se llama eliminación de todo Trapos. En Delta las filas de control de escritura quedan sin gradiente de datos (32×33=1056parámetros), aunque comparten tensor optimizable con retención/borrado y pueden variar por weight decay. Se conservan para cambiar una sola política, no se cuentan como parámetros funcionales útiles.

Random, si se ejecutó, usa Bernoulli por ejemplo/fragmento compartida entre características, con media fijada desde gates del piloto. Iguala coeficiente aditivo esperado, no varianza/amplitud de estado, borrado ni FLOPs omitidos. Todos los candidatos se calculan incluso con coeficiente0. La evaluación contrafactual random fija RNG991, conserva tamaño/posición de batches y usa las mismas máscaras para original/twins/reset. Es una realización de evaluación; no certifica promedios sobre infinitas máscaras.

Los resultados mixtos borrado→escritura permanecen en diagnostics; la tabla aquí exige correcciones de VALOR sin cambiar operación. Ninguna pequeña diferencia global basta para acreditar selección aprendida.
