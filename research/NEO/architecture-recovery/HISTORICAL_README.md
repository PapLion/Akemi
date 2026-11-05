# CryoCCM — Diagnóstico causal del contenido de Hielo

Rama `cryo-value-representation-v1`, origen198b681. Código y resultados nuevos en [`value-study/`](value-study/README.md). Los archivos heredados de `selective-memory/`, `mechanism-study/` y `vendor/` se preservan; checkpoints originales se leen desde el worktree anterior y se verifican por SHA-256.

Se ejecutaron probes lineales/MLP sobre modelos congelados, controles explícitos/presencia/permutación/inicialización, panel balanceado, trazas de estados e intervenciones emparejadas. No GPU, servicios pagos, pretraining ni evaluaciones selladas.

**Resultado:** presencia robustamente decodificable, valores parciales y dependientes de estructura. Ninguno de los nueve modelos sigue correctamente el cambio de valor vigente al recibir el estado real de su donante emparejado. No se ha demostrado que guardar valores ya funcione y falle exclusivamente el lector.

- [Estado real y extracción](STATE_EXTRACTION.md).
- [Datos y oráculos](CONTROLLED_DATA.md).
- [Decodificación](VALUE_DECODING.md) y [resumen por semillas](value-study/REPRESENTATION_SUMMARY.md).
- [Intervenciones causales](CAUSAL_INTERVENTIONS.md).
- [Escritura](WRITE_PATH.md), [lectura](READ_PATH.md), [filtro](FILTER_DIAGNOSTICS.md).
- [Causa y límites](ROOT_CAUSE.md), [única intervención siguiente](NEXT_DECISION.md).

Reproducción: `bash value-study/run.sh`. Artefactos pesados locales ignorados porGit, con hashes en `value-study/SHA256SUMS.json`; métricas/predicciones/curvas, tests y negativos conservados. El piloto de supervisión auxiliar end-to-end se propone, no se declara ejecutado.
