# Intercambio causal de estados emparejados

120programas dev con corrección real (inicial distinto del vigente), iguales salvo un valor. Se conserva presencia, estructura y último bloque visible. Donante real del mismo modelo/entidad/layout, no código artificial. Estado tras token55. Sham exacto. Histórico: intervención completa sobre slow antes56; híbridos: sustituir memoria de lectura del último fragmento, cuya escritura posterior no afecta respuestas.

|Modelo|Seed|Cambio|Distancia relativa media|Predicción original cambia al inyectar|Acierta donante antes/después|L2 logits5|
|---|---:|---|---:|---:|---:|---:|
|delta_fast|17|obsolete|0.075183|0.00%|25.00% / 25.00%|0.035379|
|delta_fast|17|valid|0.168705|0.00%|25.00% / 25.00%|0.224181|
|delta_fast|29|obsolete|0.160964|10.00%|19.17% / 19.17%|0.502448|
|delta_fast|29|valid|0.198308|14.17%|20.00% / 19.17%|0.686991|
|delta_fast|43|obsolete|0.013735|0.00%|25.00% / 25.00%|0.016931|
|delta_fast|43|valid|0.024299|0.00%|25.00% / 25.00%|0.036722|
|event_fast|17|obsolete|0.021395|0.00%|25.00% / 25.00%|0.030498|
|event_fast|17|valid|0.079596|0.00%|25.00% / 25.00%|0.108312|
|event_fast|29|obsolete|0.021107|0.00%|25.00% / 25.00%|0.068891|
|event_fast|29|valid|0.105045|0.00%|25.00% / 25.00%|0.276468|
|event_fast|43|obsolete|0.018363|0.00%|25.00% / 25.00%|0.081748|
|event_fast|43|valid|0.051989|0.00%|25.00% / 25.00%|0.079999|
|intact|17|obsolete|0.007924|0.00%|25.00% / 25.00%|0.013886|
|intact|17|valid|0.032619|0.00%|25.00% / 25.00%|0.031610|
|intact|29|obsolete|0.001714|0.00%|5.00% / 5.00%|0.001043|
|intact|29|valid|0.126891|0.00%|5.00% / 5.00%|0.074014|
|intact|43|obsolete|0.002639|0.00%|20.00% / 20.00%|0.000746|
|intact|43|valid|0.026599|0.00%|20.00% / 20.00%|0.006239|

Distancia positiva acredita sensibilidad representacional, no asociación correcta. El par original debe ser correcto y la intervención seguir el nuevo vigente; joint_value_follow se registra aparte en JSON. Cambiar el obsoleto debería preservar el vigente: que cambien logits no basta para declarar un fallo si la respuesta sigue correcta. Estados reales emparejados reducen, pero no eliminan, el riesgo de incompatibilidad al combinar estados con un receptor; no se declara causalidad universal fuera del alcance de la intervención.
