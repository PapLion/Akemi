# NEO — índice de investigación para revisión

Informes, código de referencia y métricas agregadas. Es una copia de consulta del trabajo local: corpus, pesos, tokens privados y conjuntos sellados quedan fuera.

## Estado más reciente: primer F2 GPU completado

- [Decisión del entrenamiento](architecture-recovery/neo-f2-gpu-training-v1/DECISION.md).
- [Resultados de entrenamiento](architecture-recovery/neo-f2-gpu-training-v1/TRAINING_RESULTS.md).
- [Comparación con Transformer](architecture-recovery/neo-f2-gpu-training-v1/BASELINE_COMPARISON.md).
- [Validación por idioma](architecture-recovery/neo-f2-gpu-training-v1/EVALUATION.md).
- [Generaciones completas, incluidas las repetitivas](architecture-recovery/neo-f2-gpu-training-v1/GENERATIONS.md).
- [Rendimiento y límites de medida](architecture-recovery/neo-f2-gpu-training-v1/GPU_PERFORMANCE.md).
- [Coste y cierre de Vast.ai](architecture-recovery/neo-f2-gpu-training-v1/COST_REPORT.md).
- [Configuración y alcance privado de los derechos](architecture-recovery/neo-f2-gpu-training-v1/TRAINING_CONFIG.md).

F2: 4,922,444 targets ES/EN; NLL dev 5.559083; PPL 259.585. Checkpoint final descargado y verificado localmente. GPU destruida y ausencia confirmada por API. Descenso de crédito observado USD 0.159799, sujeto a ajustes pendientes. Generaciones muy repetitivas; no demuestra capacidad conversacional. Hielo y Trapos OFF. Los límites documentales históricos del corpus se preservan; no hay aprobación general de publicación de pesos/corpus.

[Release histórico de datos](architecture-recovery/f2-corpus-release/DECISION.md): su clasificación CONDITIONAL no se sobrescribe. Esta ejecución documenta el uso privado concreto autorizado.

## Cómo analizarlo con otro modelo

Compartir el enlace a esteREADME y pedir: «Lee primero la decisión actual y sus compuertas; distingue mediciones, estimaciones y resultados históricos. Sigue después los enlaces al experimento que quieras analizar». Un asistente con acceso web/GitHub puede abrir los archivos de esta rama.

Los nombres de ramas/commits originales del manifiesto identifican la procedencia **local**: esos SHA no son commits publicados en Akemi. No se transfirió su historiaGit porque incluye artefactos que no deben publicarse. La historia de esta carpeta tendrá sus propios commitsGitHub.

Algunos enlaces históricos apuntan a artefactos excluidos o rutas de máquina. Se conserva su referencia, no se simula que estén disponibles. Las rutas locales exportadas usan `/PATH/TO/NEO_HOME`. Checkpoints, corpus, evaluaciones selladas, trazas y predicciones detalladas no se publican.

## Experimentos disponibles

- **addressable**: [README.md](architecture-recovery/addressable/README.md), [DECISION.md](architecture-recovery/addressable/DECISION.md)
- **addressable-consolidation**: [README.md](architecture-recovery/addressable-consolidation/README.md), [DECISION.md](architecture-recovery/addressable-consolidation/DECISION.md)
- **association**: [README.md](architecture-recovery/association/README.md), [DECISION.md](architecture-recovery/association/DECISION.md)
- **association-interference**: [README.md](architecture-recovery/association-interference/README.md), [DECISION.md](architecture-recovery/association-interference/DECISION.md)
- **association-repair**: [README.md](architecture-recovery/association-repair/README.md), [DECISION.md](architecture-recovery/association-repair/DECISION.md)
- **binding-diagnostic**: [README.md](architecture-recovery/binding-diagnostic/README.md), [DECISION.md](architecture-recovery/binding-diagnostic/DECISION.md)
- **chunk-boundary**: [README.md](architecture-recovery/chunk-boundary/README.md), [DECISION.md](architecture-recovery/chunk-boundary/DECISION.md)
- **contract-v2**: [README.md](architecture-recovery/contract-v2/README.md), [DECISION.md](architecture-recovery/contract-v2/DECISION.md)
- **corpus-recovery-f2**: [README.md](architecture-recovery/corpus-recovery-f2/README.md), [DECISION.md](architecture-recovery/corpus-recovery-f2/DECISION.md)
- **distribution-scaling**: [README.md](architecture-recovery/distribution-scaling/README.md), [DECISION.md](architecture-recovery/distribution-scaling/DECISION.md)
- **f2-corpus-release**: [README.md](architecture-recovery/f2-corpus-release/README.md), [DECISION.md](architecture-recovery/f2-corpus-release/DECISION.md)
- **foreground-binding**: [README.md](architecture-recovery/foreground-binding/README.md), [DECISION.md](architecture-recovery/foreground-binding/DECISION.md)
- **language-bridge**: [README.md](architecture-recovery/language-bridge/README.md), [DECISION.md](architecture-recovery/language-bridge/DECISION.md)
- **language-foundation**: [README.md](architecture-recovery/language-foundation/README.md), [DECISION.md](architecture-recovery/language-foundation/DECISION.md)
- **learning-diagnosis**: [README.md](architecture-recovery/learning-diagnosis/README.md), [DECISION.md](architecture-recovery/learning-diagnosis/DECISION.md)
- **mechanism-study**: [README.md](architecture-recovery/mechanism-study/README.md), [DECISION.md](architecture-recovery/mechanism-study/DECISION.md)
- **memory-bridge**: [README.md](architecture-recovery/memory-bridge/README.md), [DECISION.md](architecture-recovery/memory-bridge/DECISION.md)
- **multiwrite**: [README.md](architecture-recovery/multiwrite/README.md), [DECISION.md](architecture-recovery/multiwrite/DECISION.md)
- **neo-f2-gpu-training-v1**: [README.md](architecture-recovery/neo-f2-gpu-training-v1/README.md), [DECISION.md](architecture-recovery/neo-f2-gpu-training-v1/DECISION.md)
- **order-curriculum**: [README.md](architecture-recovery/order-curriculum/README.md), [DECISION.md](architecture-recovery/order-curriculum/DECISION.md)
- **query-conditioning**: [README.md](architecture-recovery/query-conditioning/README.md), [DECISION.md](architecture-recovery/query-conditioning/DECISION.md)
- **selective-memory**: [README.md](architecture-recovery/selective-memory/README.md), [DECISION.md](architecture-recovery/selective-memory/DECISION.md)
- **stability**: [README.md](architecture-recovery/stability/README.md), [DECISION.md](architecture-recovery/stability/DECISION.md)
- **trapos**: [README.md](architecture-recovery/trapos/README.md), [DECISION.md](architecture-recovery/trapos/DECISION.md)
- **two-bindings**: [README.md](architecture-recovery/two-bindings/README.md), [DECISION.md](architecture-recovery/two-bindings/DECISION.md)
- **value-study**: [README.md](architecture-recovery/value-study/README.md), [ROOT_CAUSE.md](architecture-recovery/value-study/ROOT_CAUSE.md), [NEXT_DECISION.md](architecture-recovery/value-study/NEXT_DECISION.md)

[Manifiesto, hashes y procedencia](PUBLICATION_MANIFEST.json). Los experimentos negativos permanecen publicados. Hielo simbólico no se presenta como validación lingüística; Trapos aprendido continúa congelado.
