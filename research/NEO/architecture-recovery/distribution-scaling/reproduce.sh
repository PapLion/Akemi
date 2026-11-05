#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
if [ -e distribution-scaling/results/primary-comparison.json ]; then
 echo 'Existing evidence preserved. Reproduce in a clean copy, removing only its distribution-scaling/results.' >&2
 exit 1
fi
"$PY" distribution-scaling/tests.py
"$PY" distribution-scaling/factorial.py
"$PY" distribution-scaling/audit.py
"$PY" distribution-scaling/write_reports.py
