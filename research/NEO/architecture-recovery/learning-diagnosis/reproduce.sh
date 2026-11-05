#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
if [ -e learning-diagnosis/results/forensics.json ]; then
 echo 'Evidence exists: use a clean copy and remove only its learning-diagnosis/results before reproducing.' >&2
 exit 1
fi
"$PY" learning-diagnosis/diagnose.py forensic
"$PY" learning-diagnosis/tests.py
"$PY" learning-diagnosis/diagnose.py ladder
if "$PY" -c 'import json; assert json.load(open("learning-diagnosis/results/ladder-decision.json"))["first_failed_level"]=="4"'; then
 "$PY" learning-diagnosis/optimization.py
 # DENSE_PROTOCOL is frozen; no outcome-dependent modification.
 "$PY" learning-diagnosis/dense.py
 "$PY" learning-diagnosis/final_checks.py
 "$PY" learning-diagnosis/gradient_routes.py
 "$PY" learning-diagnosis/write_reports.py
fi
