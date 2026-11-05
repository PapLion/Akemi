# Conteo V3 exhaustivo de la selección candidata

| Split | Idioma | Documentos | IDs texto | Targets BOS-texto-EOS | Bytes texto |
|---|---|---:|---:|---:|---:|
| train | es | 726 | 2506094 | 2506820 | 8248388 |
| train | en | 1230 | 2498829 | 2500059 | 7987568 |
| dev | es | 30 | 107303 | 107333 | 323030 |
| dev | en | 40 | 104732 | 104772 | 336368 |

Fingerprint V3: 813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b. Artefacto sin modificaciones. Cada documento se tokenizó, se comprobó round-trip Unicode y codificación repetida idéntica; la caché registra SHA del texto y fingerprint. Los tests verifican longitudes de arrays para todos los seleccionados.

Son **5.006.879 targets train candidatos** y **212.105 dev candidatos**, no aprobados. Tokens de texto = targets menos un EOS supervisado por documento. BOS es entrada, no target inicial. No se predicen transiciones entre documentos. Ventanas de T tokens con stride T-1 mantienen cada target una vez, incluido EOS; padding ignorado. Las cifras se refieren a posiciones tokenizadas en documentos distintos, no a vocablos únicos ni a exposiciones repetidas.

Conteo de la selección completo, corpus maestro completo NO contado. Certificados reanudables counts.sqlite y IDs uint16 locales; hash de certificados en LOCAL_SHA256SUMS.json. Tiempo de adquisición+preparación+conteo: 77.22s; no es benchmark puro de tokenización. Aprobado sigue siendo 25.355 train / 8.637 dev.
