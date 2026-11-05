# NEO — índice de investigación para revisión

Este directorio reúne los informes, código de referencia y métricas agregadas de NEO/CryoCCM. Es una publicación de consulta del trabajo local, no el corpus ni un paquete completo de entrenamiento. **No supone que NEO comprenda lenguaje ni que F2 esté autorizado para entrenar.**

## Estado más reciente

- [Decisión: corpus recuperado y preparación F2](architecture-recovery/corpus-recovery-f2/DECISION.md).
- [Inventario y recuperación del corpus](architecture-recovery/corpus-recovery-f2/CORPUS_RECOVERY.md).
- [Derechos y fuentes pendientes](architecture-recovery/corpus-recovery-f2/LICENSE_AUDIT.md).
- [Conteos NeoToken V3: exactos parciales, no total certificado](architecture-recovery/corpus-recovery-f2/NEOTOKEN_V3_COUNTS.md).
- [Benchmark real F2 CPU](architecture-recovery/corpus-recovery-f2/F2_CPU_BENCHMARK.md).
- [Compuertas pendientes antes de F2](architecture-recovery/corpus-recovery-f2/TRAINING_READINESS.md).

**Resultado actual:** corpus bruto564.789BASE+765SFT; curado500M257.043BASE; curado1B555.914BASE. Nombres1B/500Mson objetivos históricos. Solo25.355targets train aprobados y libres de reservas en la selección preparada; no se ejecutó el entrenamiento5M. F2=2.082.176parámetros; nueve tests técnicosPASS.

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
- **foreground-binding**: [README.md](architecture-recovery/foreground-binding/README.md), [DECISION.md](architecture-recovery/foreground-binding/DECISION.md)
- **language-bridge**: [README.md](architecture-recovery/language-bridge/README.md), [DECISION.md](architecture-recovery/language-bridge/DECISION.md)
- **language-foundation**: [README.md](architecture-recovery/language-foundation/README.md), [DECISION.md](architecture-recovery/language-foundation/DECISION.md)
- **learning-diagnosis**: [README.md](architecture-recovery/learning-diagnosis/README.md), [DECISION.md](architecture-recovery/learning-diagnosis/DECISION.md)
- **mechanism-study**: [README.md](architecture-recovery/mechanism-study/README.md), [DECISION.md](architecture-recovery/mechanism-study/DECISION.md)
- **memory-bridge**: [README.md](architecture-recovery/memory-bridge/README.md), [DECISION.md](architecture-recovery/memory-bridge/DECISION.md)
- **multiwrite**: [README.md](architecture-recovery/multiwrite/README.md), [DECISION.md](architecture-recovery/multiwrite/DECISION.md)
- **order-curriculum**: [README.md](architecture-recovery/order-curriculum/README.md), [DECISION.md](architecture-recovery/order-curriculum/DECISION.md)
- **query-conditioning**: [README.md](architecture-recovery/query-conditioning/README.md), [DECISION.md](architecture-recovery/query-conditioning/DECISION.md)
- **selective-memory**: [README.md](architecture-recovery/selective-memory/README.md), [DECISION.md](architecture-recovery/selective-memory/DECISION.md)
- **stability**: [README.md](architecture-recovery/stability/README.md), [DECISION.md](architecture-recovery/stability/DECISION.md)
- **trapos**: [README.md](architecture-recovery/trapos/README.md), [DECISION.md](architecture-recovery/trapos/DECISION.md)
- **two-bindings**: [README.md](architecture-recovery/two-bindings/README.md), [DECISION.md](architecture-recovery/two-bindings/DECISION.md)
- **value-study**: [README.md](architecture-recovery/value-study/README.md), [ROOT_CAUSE.md](architecture-recovery/value-study/ROOT_CAUSE.md), [NEXT_DECISION.md](architecture-recovery/value-study/NEXT_DECISION.md)

[Manifiesto, hashes y procedencia](PUBLICATION_MANIFEST.json). Los experimentos negativos permanecen publicados. Hielo simbólico no se presenta como validación lingüística; Trapos aprendido continúa congelado.
