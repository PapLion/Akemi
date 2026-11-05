#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# Requires fresh results paths. Never overwrite archived evidence.
"$PY" distribution-scaling/tests.py
"$PY" order-curriculum/run.py
"$PY" order-curriculum/report.py
"$PY" order-curriculum/verify.py
