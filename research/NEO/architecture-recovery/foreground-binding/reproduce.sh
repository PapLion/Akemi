#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
if [ -e foreground-binding/results/primary-comparison.json ]; then
 echo 'Existing results preserved; reproduce in a clean copy, never overwrite historical evidence.' >&2
 exit 1
fi
mkdir -p foreground-binding/results
"$PY" foreground-binding/tests.py
"$PY" foreground-binding/run_experiment.py
"$PY" foreground-binding/contextualization.py
"$PY" foreground-binding/write_reports.py
