# Contrafactuales e intervenciones

Medias de tres semillas; IID + estructural. Ambos correctos exige acertar original y contrafactual. Cambiar el hecho vigente fuera de ventana deja los últimos16IDs idénticos. Un control sin memoria no puede acertar ambas versiones. No usar sensibilidad sola como prueba de utilidad.

|Modelo/ventana|N pares fuera por semilla: vigente/obsoleto|Vigente ambos correctos|Vigente sensibilidad|Obsoleto ambos correctos|Obsoleto sensibilidad|
|---|---:|---:|---:|---:|---:|
|delta_fast/16|240/144|4.86|18.33|55.79|2.08|
|event_fast/16|240/144|4.17|16.39|52.08|1.62|
|intact/16|240/144|2.22|6.39|43.98|0.69|
|no_ice/16|240/144|0.00|0.00|33.56|0.00|
|transformer/0|240/144|3.33|16.39|40.97|6.02|
|transformer/16|240/144|0.00|0.00|37.73|0.00|

## Prueba crítica conjunta de corrección

Solo replace/multiple fuera de ventana con valor inicial distinto del vigente. Hay que acertar original + cambio obsoleto + cambio vigente en el MISMO ejemplo. Separa contrafactual vigente dentro/fuera del soporte visto por entidad.

|Modelo/ventana|N tripletes por semilla (todos/visto)|Exactitud tres versiones, todos|Exactitud tres versiones, par visto|
|---|---:|---:|---:|
|delta_fast/16|54/32|4.32|7.29|
|event_fast/16|54/32|6.17|10.42|
|intact/16|54/32|0.62|1.04|
|no_ice/16|54/32|0.00|0.00|
|transformer/0|54/32|3.70|6.25|
|transformer/16|54/32|0.00|0.00|

## Intervenciones de inferencia, después del entrenamiento

Reset/intercambio se aplica al estado justo antes del último fragmento de8IDs. El query no atiende a los outputs híbridos previos: fuera de ventana, reset elimina su ruta declarada de acceso al prefijo. El intercambio usa el vecino del batch y no garantiza respuesta distinta; interpretar como perturbación, no un oráculo contrafactual.

|Modelo|Semilla|Intervención|N fuera|Exactitud base|Exactitud intervenida|Predicciones cambiadas|
|---|---:|---|---:|---:|---:|---:|
|delta_fast|17|reset/outside|240|52.08|37.08|21.25|
|delta_fast|17|swap/outside|240|52.08|27.92|34.17|
|delta_fast|29|reset/outside|240|53.75|36.25|35.83|
|delta_fast|29|swap/outside|240|53.75|26.25|50.00|
|delta_fast|43|reset/outside|240|48.33|34.58|21.67|
|delta_fast|43|swap/outside|240|48.33|30.83|30.83|
|event_fast|17|reset/outside|240|45.00|32.50|27.50|
|event_fast|17|swap/outside|240|45.00|26.25|37.92|
|event_fast|29|reset/outside|240|50.42|29.58|36.67|
|event_fast|29|swap/outside|240|50.42|22.50|40.00|
|event_fast|43|reset/outside|240|46.25|34.17|29.17|
|event_fast|43|swap/outside|240|46.25|27.50|39.17|

**Advertencia de cierre:** los cambios de operación borrado→escritura inflan parte de las métricas mixtas anteriores. [VALUE_BINDING.md](VALUE_BINDING.md) desagrega correcciones genuinas de valor manteniendo la operación:0/42 en los18modelos primarios. [ABLATION_VALUE_BINDING.md](ABLATION_VALUE_BINDING.md):0/42 en las seis ablaciones adicionales. No interpretar los porcentajes mixtos como edición fiable de valores.
