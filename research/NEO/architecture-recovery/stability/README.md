# Addressable V1.2 — estabilidad/plasticidad

Contraste CPU ejecutado en rama `cryo-addressable-stability-v1`, desde `74d8079`. Arquitectura Addressable V1 intacta. El piloto habilitó confirmaciones emparejadas.

Esta carpeta contiene datos, protocolo congelado antes de entrenar, tests, curvas, predicciones, estados reales, checkpoints completos y hashes. Los `.pt` se conservan localmente y se enumeran en SHA256SUMS. No se abrió ninguna evaluación sellada. Sin GPU, servicios de pago ni corpus lingüístico.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
"$PY" addressable/test_contracts.py
"$PY" stability/test_contracts.py
# Entrenamiento: SOLO en otro worktree limpio, sin artefactos stability/results/.
"$PY" stability/study.py
"$PY" stability/diagnostics.py
"$PY" stability/write_reports.py
```

El script rechaza sobrescribir FREEZE o checkpoints finales. No borrar los resultados para repetir. Dependencias y rutas de warmstart son las mismas de V1.1. Leer DECISION.md y PROTOCOL.md antes de interpretar los porcentajes.
