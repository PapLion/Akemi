# Corrección genuina de valores, sin cambio de operación

Se desagrega después del diagnóstico mixto; se conservan ambos resultados. El modelo debe acertar original, cambio del valor obsoleto y cambio del valor vigente. Solo replace/multiple fuera de ventana con inicial distinto del vigente; el contrafactual mantiene la operación. Los42programas se reutilizan entre semillas: no son126ejemplos independientes.24cambios dejan el par entidad–valor dentro del soporte train,18fuera.

|Modelo/ventana/modo|Semilla|Tres versiones correctas /42|Dentro de soporte /24|Fuera /18|
|---|---:|---:|---:|---:|
|delta_fast/16/normal|17|0|0|0|
|delta_fast/16/normal|29|0|0|0|
|delta_fast/16/normal|43|0|0|0|
|event_fast/16/normal|17|0|0|0|
|event_fast/16/normal|29|0|0|0|
|event_fast/16/normal|43|0|0|0|
|intact/16/normal|17|0|0|0|
|intact/16/normal|29|0|0|0|
|intact/16/normal|43|0|0|0|
|no_ice/16/normal|17|0|0|0|
|no_ice/16/normal|29|0|0|0|
|no_ice/16/normal|43|0|0|0|
|transformer/0/normal|17|0|0|0|
|transformer/0/normal|29|0|0|0|
|transformer/0/normal|43|0|0|0|
|transformer/16/normal|17|0|0|0|
|transformer/16/normal|29|0|0|0|
|transformer/16/normal|43|0|0|0|

Un cero no demuestra imposibilidad de aprender con otros datos/entrenamiento. Sí impide certificar edición fiable de valores en esta ejecución. Las métricas mixtas positivas por cambios borrado→escritura no se presentan como aprendizaje de valores.
