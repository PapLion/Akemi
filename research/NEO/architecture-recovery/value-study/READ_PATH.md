# Memoria y lectura congeladas

Semilla17 prefijada para etapas detalladas; media de logits no sustituye decodificación. Probe por entidad sobre pesos congelados. El readout auxiliar se entrena200updates; el readout original no se modifica. Las proyecciones de candidato se reconstruyen mediante los mismos módulos congelados aplicados a las características observadas, sin sintetizar memoria.

|Modelo|Etapa|Objetivo|Dev lineal|Dev MLP|
|---|---|---|---:|---:|
|intact|memory|value|32.50|34.69|
|intact|read|value|34.69|35.62|
|intact|local|value|25.00|25.00|
|event_fast|memory|value|33.44|33.13|
|event_fast|read|value|28.44|25.31|
|event_fast|local|value|25.00|25.00|
|delta_fast|memory|value|30.63|27.50|
|delta_fast|read|value|37.19|28.12|
|delta_fast|local|value|25.00|25.00|

El primer valor y el vigente son variables distintas en correcciones; no comparar sus porcentajes como si midieran el mismo objetivo. Los híbridos escriben por8IDs: post_write incluye el fragmento completo donde cae la corrección, no una actualización ficticia por token. No se ha entrenado una política de escritura nueva ni se ha inyectado memoria explícita en el modelo para afirmar compatibilidad.

## Vigente frente a obsoleto

Casos presente/corregido con inicial≠vigente, dev estructural. Exactitud de valor frente a copiar obsoleto; mismo decoder y semilla.

|Checkpoint|Decoder|Vigente probe|Obsoleto probe|Vigente modelo original|
|---|---|---:|---:|---:|
|delta_fast-17-normal-trained|linear|30.00|26.67|25.00|
|delta_fast-17-normal-trained|mlp|27.50|24.17|25.00|
|delta_fast-29-normal-trained|linear|31.67|26.67|19.17|
|delta_fast-29-normal-trained|mlp|26.67|25.00|19.17|
|delta_fast-43-normal-trained|linear|25.00|25.83|25.00|
|delta_fast-43-normal-trained|mlp|26.67|24.17|25.00|
|event_fast-17-normal-trained|linear|30.83|26.67|25.00|
|event_fast-17-normal-trained|mlp|31.67|25.83|25.00|
|event_fast-29-normal-trained|linear|35.00|25.83|25.00|
|event_fast-29-normal-trained|mlp|33.33|30.00|25.00|
|event_fast-43-normal-trained|linear|35.83|21.67|25.00|
|event_fast-43-normal-trained|mlp|30.83|24.17|25.00|
|intact-17-normal-trained|linear|35.83|22.50|25.00|
|intact-17-normal-trained|mlp|34.17|26.67|25.00|
|intact-29-normal-trained|linear|35.83|21.67|5.00|
|intact-29-normal-trained|mlp|32.50|22.50|5.00|
|intact-43-normal-trained|linear|26.67|25.00|20.00|
|intact-43-normal-trained|mlp|29.17|24.17|20.00|
