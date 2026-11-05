# Decisión de ingeniería

**Cerrar definitivamente los microfits de bindings y currículos de orden. El siguiente trabajo es datos y aprendizaje causal de texto diverso, no otra memoria.**

Tenemos un foreground causal técnicamente entrenable y reproducible, con296160 parámetros activos,262144 en vocabulario y solo34016contextuales/noembedding. No hay evidencia de capacidad suficiente para una base lingüística general. Hielo simbólico estable se conserva, Trapos congelado, V3BPE8K provisional sin cambios.

El piloto de texto real admisible demuestra descenso dev8,9941→5,7674 y ventaja frente a unigram6,2673. Hay señal de transferencia entre repositorios, **no solamente memorización de train**; con2archivos dev de código no demuestra generalización lingüística amplia. Generación repetitiva y una sola semilla. Baseline5,8379 no establece superioridad del foreground.

Recomendación única de continuidad: preparar corpus piloto bilingüe/diverso con derechos verificados y dev por familias, y entonces presupuestar F2~2,08M/5Mtargets contra Transformer comparable. F8~8,20M/50Mtargets es segunda opción condicionada, no un entrenamiento autorizado. Datos actuales no alcanzan ese escalón; no compensar ciclando cientos de veces. Costes y límites explícitos en SCALING_PROPOSAL.md.

| Modelo | Parámetros activos | NLL train final | NLL dev inicial → final | PPL dev | Targets/s | RAM MiB |
|---|---:|---:|---:|---:|---:|---:|
| foreground | 296160 | 4.8493 | 8.9941 → 5.7674 | 319.71 | 5638.3 | 773.1 |
| baseline | 293024 | 4.8721 | 8.9901 → 5.8379 | 343.05 | 4943.5 | 773.1 |


Trainer CPU listo para ingeniería; faltan datos representativos, calidad de generación, presupuesto/benchmark a escala y validación lingüística. No se implementan configuraciones nuevas ni se inicia pretraining significativo. Sin GPU, Vast, Chinchilla, A4, cambios de tokenizer o acceso sellado. Artefactos negativos y positivos preservados.
