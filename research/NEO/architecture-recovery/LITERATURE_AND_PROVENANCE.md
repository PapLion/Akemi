# Mecanismos consultados y decisiones de implementación

Consulta2026-10-31UTC, fuentes primarias. No se copiaron implementaciones externas. Los resultados citados son reportados por sus autores; no fueron reproducidos aquí. Ninguna comparación publicada demuestra que un modelo de ~280K deba ganar estas tareas.

| Trabajo primario | Mecanismo que informa el diseño | Límite para este prototipo |
|---|---|---|
| [Gated DeltaNet-2](https://arxiv.org/html/2605.22791v1),v1 | Separar borrado en claves y escritura en valores; actualización afín y organización por bloques | Paper evalúa1,3B/100B tokens; nuestro borrado es escalar y no implementa WY/backward del paper. No extrapolar sus resultados. Código oficial identificado con licencia NVIDIA Source Code License-NC: no se importa |
| [Gated DeltaNet](https://arxiv.org/abs/2412.06464),v3 | Olvido multiplicativo más edición delta, mejor que suma indiscriminada como hipótesis | La eficiencia publicada depende de algoritmos/kernels de entrenamiento, no de un loop PyTorch cualquiera |
| [Kimi Linear/KDA](https://arxiv.org/abs/2510.26692) | Control fino del olvido y combinación con atención | No se trasladan kernels, checkpoints, ni cifras de48B/MoE a modelos pequeños; retención por canal no implementada aquí |
| [Mamba-2/SSD](https://arxiv.org/abs/2405.21060) | Relación entre estructura algebraica y algoritmos por bloques | Nuestro scan es denso de referencia, no SSD; conservar matriz compacta no implica throughput alto |
| [Mamba-3](https://arxiv.org/abs/2603.15569) | Discretización más expresiva, rotaciones complejas y MIMO para estado/eficiencia | No se incorpora complejidad ni kernel sin necesidad medida; resultados de sus autores a escalas mayores, no reproducción independiente |
| [Nested Learning/HOPE](https://abehrouz.github.io/files/NL.pdf),NeurIPS2025 | Memorias con ritmos/contextos de actualización distintos | Aquí activaciones por secuencia, no optimización interna multinivel ni memoria de parámetros modificada durante inferencia |
| [Titans](https://arxiv.org/abs/2501.00663) | Lectura local más memoria asociativa y aprendizaje de qué conservar | No hacemos optimizador de test-time ni memoria neuronal profunda; evita costes/contratos de gradientes de segundo nivel |
| [MIRAS](https://arxiv.org/abs/2504.13173) | Descomponer sesgo asociativo, retención y algoritmo de actualización | Elegimos regla afín verificable, no combinación indiscriminada de todas las variantes |
| [xLSTM](https://arxiv.org/abs/2405.04517),v2 | Gates estabilizadas, estado matricial y formas paralelas | No se replica mLSTM ni se adoptan pesos/licencias de modelos. Un gate por sí solo no prueba selección semántica |
| [Skip RNN](https://arxiv.org/abs/1708.06834) | Diferenciar decisión de saltar y actualización realmente omitida | Event soft entrena todas las escrituras; hard solo es diagnóstico de inferencia, sin estimador discreto entrenado |

HRM/TRM no se reutilizan: el experimento actual mide conservación/edición contextual, no cómputo de razonamiento iterativo. No se considera una refutación de esas propuestas.

## Derechos y fuente del código

`results/literature-provenance.json` fija commits y SHA de licencias consultadas: GDN2 `de8476de...`, Mamba `e9594ce...`, xLSTM `ab22ead...`. Mamba y el repositorio xLSTM consultado muestran Apache-2.0; no se asume que kernels, pesos y repositorios auxiliares tengan idéntica licencia. La licencia del artículo y la del software son distintas. No hay código de esos repositorios en el prototipo, ni una declaración de asesoría legal/patentes.

`vendor/cryo_historical.py` es una copia sin cambios de la referencia experimental local del propietario; hash en SOURCE_MANIFEST.json. `vendor/next_training_v1.py` conserva exactamente el modelo de la primera ejecución de aprendizaje. Después se reforzó la identidad de sesiones y se corrigió el contador de operaciones candidatas sobre padding; no se cambiaron ecuaciones o pesos. Tests comparan la matemática actual contra ese snapshot.
