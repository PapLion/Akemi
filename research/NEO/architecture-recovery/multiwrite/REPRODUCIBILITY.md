# Reproducción y artefactos

Desde multiwrite/, usar `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python mw_run.py`; después mw_analyze.py, mw_checks.py, write_cost.py, causality_edges.py y mw_report.py. El entrenador rechaza results existente: repetir en copia nueva, preservando estos resultados.

Checkpoint histórico solo lectura y weights_only; origen ../../cryo-selective-memory-study/selective-memory/results/extend/delta_fast-normal-w16-17.pt. Código histórico versionado en este worktree. Nuevos checkpoints incluyen K, receta, datos hash,modelo/decoder/AdamW/RNG/cursor. El estado Hielo por documento se reconstruye en forward y no persiste de un batch a otro. .pt locales ignorados por Git pero incluidos en SHA256SUMS.

Verificar `sha256sum -c SHA256SUMS`. No se usó GPU, corpus, pickle genérico ni evaluaciones selladas. Históricos verificados mediante hashes sin escribirlos.
