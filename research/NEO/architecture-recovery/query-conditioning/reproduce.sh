#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if test -e query-conditioning/results/contracts.json || test -e query-conditioning/results/short-A-17.pt; then
 echo 'Refusing overwrite. Use a fresh worktree with an empty query-conditioning/results directory.' >&2
 exit 1
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
"$PY" query-conditioning/run.py
"$PY" query-conditioning/tests.py
"$PY" query-conditioning/diagnostics.py
"$PY" query-conditioning/report.py
