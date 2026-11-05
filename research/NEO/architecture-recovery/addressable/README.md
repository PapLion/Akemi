# CryoCCM-Addressable V1

Implementación y experimento CPU FP32 ejecutados. Asociación inicial y respuesta normal 100% en train/layout; corrección incompleta. **Éxito parcial de asociación; no certificado de filtrado ni de lenguaje.**

Origen: cryo-multiwrite-v1, 3950afc. Rama aislada cryo-addressable-memory-v1. Sin GPU, gastos, corpus, tokenizer ni evaluaciones selladas.

Artefactos: `results/`; datos, curvas de 300 updates, predicciones completas, estados reales, checkpoints, AdamW/RNG/cursor, controles, tests y hashes. `.pt` se conserva localmente y está ignorado por Git. No publicar solo el código y asumir que los checkpoints viajan con Git.

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/test_contracts.py
# Entrenamiento: requiere results/ nuevo; rehúsa sobrescribir microfit.pt.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/run_addressable.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/analyze_addressable.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/generalization.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/latent_update_check.py
```

Para repetir entrenamientos, usar otro worktree con esta versión y carpeta results vacía. El checkpoint histórico fuente se encuentra en el worktree selective-memory original; no se descarga ni altera. Consultar REPRODUCIBILITY.md y DECISION.md.
