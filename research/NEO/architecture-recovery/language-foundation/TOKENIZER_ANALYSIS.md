# NeoToken V3

Artefacto BPE8192 provisional sin cambios; SHA 8489cd9a98fb4a7339fe802be74621774f2ee68b465cfb0b16846a07fe99a156. PAD256/BOS257/EOS258. IDs/JSON y fingerprint anteriores verificados, sin pickle. Se mantiene V1 exclusivamente en históricoA4.

Seis fixtures adicionales roundtrip exacto: vacío, acentos ES/EN, combinados/emoji/Unicode, código, LaTeX y controles. Roundtrip de todos los5 documentos fuente exacto. Panel concatenado85328bytes/33987 IDs: encode 0.088426s, decode 0.005904s en esta máquina, medición única sin intervalo. Artefacto80964bytes. Esto certifica funcionamiento de esta integración, no optimalidad lingüística ni paridad ES/EN.

1265 de8192 tipos aparecen en train:15,44%. La matriz sigue reservando262144 parámetros. Desconocidos Unicode tienen ruta byte-level; no se ha repetido toda certificación adversarial histórica. El contrato de causalidad del modelo se valida sobre IDs ya fijados. BPE sobre texto no garantiza estabilidad de segmentación de un prefijo al añadir caracteres: generación opera sobre IDs y detokeniza, no retokeniza targets futuros.

NeoToken es multiescala; este experimento usa solamente su núcleo BPE. Las vistas adicionales existen como sidecars en el trabajo V3, pero no se entregan al modelo ni se atribuye su potencial a este resultado. SPEC3.0 completa, cobertura lingüística y multidominio siguen experimentales según CERTIFICATION.md original.
