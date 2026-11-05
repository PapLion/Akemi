# Reproducibilidad

Desde chunk-boundary/: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python chunk_study.py`; después analyze_chunks.py y report_chunks.py con el mismo entorno. El entrenador rechaza results existente: usar copia/worktree nuevo, nunca borrar estas evidencias para repetir.

Código histórico se importa del worktree versionado; checkpoint fuente de ../../cryo-selective-memory-study/selective-memory/results/extend/delta_fast-normal-w16-17.pt, solo lectura y weights_only=True. Sin pickle genérico ni descargas. No reentrenar el control positivo con Hielo. protocol.json, frecuencias, visibilidad y certificación documentan contratos.

Checkpoints .pt quedan locales, ignorados por Git pero incluidos en SHA256SUMS; copia preservando sus paths si se transfiere. Verificar `sha256sum -c SHA256SUMS`.
