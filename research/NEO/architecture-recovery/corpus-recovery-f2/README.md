# NEO — Corpus Recovery & F2 Readiness V1

**Corpus recuperado; F2 técnicamente verificado; entrenamiento5M BLOQUEADO por selección aprobada insuficiente.** Rama `neo-corpus-recovery-f2-readiness-v1`, origen6115bb6. Ningún entrenamiento completo, GPU, descarga de corpus o gasto.

| Vista | BASE docs | BASE bytes UTF-8 | SFT separados | JSONL bytes almacenados |
| --- | --- | --- | --- | --- |
| raw1b | 564789 | 2501209022 | 765 | 3378133963 |
| curated500 | 257043 | 1219334156 | 765 | 1805875914 |
| curated1b | 555914 | 2349726579 | 765 | 3603101026 |

Los nombres1B/500M son objetivos históricos, no conteosV3. Vistas solapadas, nunca sumarlas. Se verificaron todos los shards de estas tres vistas por SHA, JSON, campos, bytes y texto; resultados en [integrity.json](results/integrity.json). Los originales no se modificaron. Se reutilizó la curación y sus índices en lectura, sin reiniciar trabajadores.

Selección admisible sin reservas de test: **25,355 train / 8,637 dev targets**, tres archivosClick y dosRequests. No basta para5M ni para un piloto bilingüe diverso. CPython tiene evidencia de licencia, pero se excluye del train por reserva histórica de familia D0test. Wikipedia/web/math/OASST no se promueven automáticamente desde sus estados pendientes.

F2=2.082.176 parámetros, baseline=2.032.768, Hielo/Trapos OFF. Tests, checkpoint/RNG/cursor, generación técnica y benchmark CPU ejecutados. Ver [DECISION](DECISION.md), [inventario](SOURCE_INVENTORY.md), [conteos](NEOTOKEN_V3_COUNTS.md), [benchmark](F2_CPU_BENCHMARK.md), [compuertas](TRAINING_READINESS.md).

Reproducción: `bash corpus-recovery-f2/reproduce.sh` desde este worktree. Solo verificación/benchmark corto; jamás lanza5M. Gate explícito: `python corpus-recovery-f2/selection.py --check-training-gate` debe rechazar el entrenamiento. CachésSQLite y checkpoints quedan locales excluidos deGit; hashes y metadatos se conservan. No se copió el texto bruto aGit ni se abrieron evaluaciones selladas.
