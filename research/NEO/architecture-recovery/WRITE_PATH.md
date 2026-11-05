# Localización por etapas de escritura

Semilla17 prefijada para etapas detalladas; media de logits no sustituye decodificación. Probe por entidad sobre pesos congelados. El readout auxiliar se entrena200updates; el readout original no se modifica. Las proyecciones de candidato se reconstruyen mediante los mismos módulos congelados aplicados a las características observadas, sin sintetizar memoria.

|Modelo|Etapa|Objetivo|Dev lineal|Dev MLP|
|---|---|---|---:|---:|
|intact|after_first|old|30.00|40.00|
|intact|pooled_write|value|25.00|25.00|
|intact|write_value|value|27.50|24.06|
|intact|post_write|value|28.12|32.19|
|intact|memory|value|32.50|34.69|
|event_fast|after_first|old|50.00|45.00|
|event_fast|pooled_write|value|35.00|34.69|
|event_fast|write_value|value|33.75|38.75|
|event_fast|post_write|value|25.31|25.94|
|event_fast|memory|value|33.44|33.13|
|delta_fast|after_first|old|50.00|40.00|
|delta_fast|pooled_write|value|23.44|39.06|
|delta_fast|write_value|value|34.69|31.56|
|delta_fast|post_write|value|28.44|29.69|
|delta_fast|memory|value|30.63|27.50|

El primer valor y el vigente son variables distintas en correcciones; no comparar sus porcentajes como si midieran el mismo objetivo. Los híbridos escriben por8IDs: post_write incluye el fragmento completo donde cae la corrección, no una actualización ficticia por token. No se ha entrenado una política de escritura nueva ni se ha inyectado memoria explícita en el modelo para afirmar compatibilidad.

## Suplementos: frontera de entrada y correcciones genuinas

El punto de entrada usa posición oracular del valor: acceso adicional para localizar, no un mecanismo aprendido.

|Modelo|Origen|Decoder|Train|Dev|Estructural|
|---|---|---|---:|---:|---:|---:|
|intact|embedding|linear|100.00|100.00|100.00|
|intact|embedding|mlp|100.00|100.00|100.00|
|intact|token_hidden|linear|100.00|90.00|75.00|
|intact|token_hidden|mlp|100.00|80.00|75.00|
|event_fast|embedding|linear|100.00|100.00|100.00|
|event_fast|embedding|mlp|100.00|100.00|100.00|
|event_fast|token_hidden|linear|100.00|92.50|75.00|
|event_fast|token_hidden|mlp|100.00|87.50|75.00|
|delta_fast|embedding|linear|100.00|100.00|100.00|
|delta_fast|embedding|mlp|100.00|100.00|100.00|
|delta_fast|token_hidden|linear|100.00|60.00|60.00|
|delta_fast|token_hidden|mlp|100.00|57.50|60.00|
|intact|pooled_write|linear|80.00|25.83|25.00|
|intact|pooled_write|mlp|87.92|25.00|25.00|
|intact|post_write|linear|100.00|32.50|40.83|
|intact|post_write|mlp|100.00|39.17|30.83|
|intact|memory|linear|97.92|45.00|25.00|
|intact|memory|mlp|100.00|52.50|24.17|
|intact|read|linear|82.08|37.50|25.00|
|intact|read|mlp|95.42|44.17|26.67|
|event_fast|pooled_write|linear|100.00|65.00|30.00|
|event_fast|pooled_write|mlp|100.00|60.00|25.00|
|event_fast|post_write|linear|100.00|43.33|30.00|
|event_fast|post_write|mlp|100.00|51.67|30.00|
|event_fast|memory|linear|97.50|34.17|28.33|
|event_fast|memory|mlp|100.00|32.50|30.00|
|event_fast|read|linear|63.33|29.17|29.17|
|event_fast|read|mlp|85.83|35.00|25.00|
|delta_fast|pooled_write|linear|100.00|70.00|26.67|
|delta_fast|pooled_write|mlp|100.00|50.00|25.00|
|delta_fast|post_write|linear|100.00|42.50|29.17|
|delta_fast|post_write|mlp|100.00|45.83|21.67|
|delta_fast|memory|linear|98.75|44.17|21.67|
|delta_fast|memory|mlp|100.00|50.83|23.33|
|delta_fast|read|linear|48.75|45.00|22.50|
|delta_fast|read|mlp|55.00|42.50|21.67|
