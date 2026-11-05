# Reproducción

Desde two-bindings/, usar Python `/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python`, OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1. En orden: `two_bindings.py`, `diagnostics.py`, `verify_outputs.py`, `make_report.py`. Entrenador rechaza results existente; no borrar evidencia: usar copia nueva/worktree y conservar resultados actuales.

Depende del checkpoint original solo lectura `../../cryo-selective-memory-study/selective-memory/results/extend/delta_fast-normal-w16-17.pt` (resuelto por extract.py). Código histórico versionado en el worktree; no descarga datos ni usa pickle genérico. Artefactos torch cargados weights_only=True. Hash del checkpoint original incluido en provenance.json. Certificados limitados a CPU FP32 monoproceso.

Para verificar integridad ejecutar `sha256sum -c SHA256SUMS`. Los .pt permanecen locales e ignorados por Git, todos incluidos en SHA256SUMS. Los resultados negativos se preservan.
