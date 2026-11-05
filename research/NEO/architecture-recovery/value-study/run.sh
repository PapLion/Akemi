#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec 9>value-study/.run.lock
flock -n 9 || { echo "Another value-study run holds the lock" >&2; exit 1; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# Do not run alongside another value-study worker.
$PY value-study/extract.py >value-study/results/extraction.log 2>&1
$PY -m unittest discover -s value-study/tests -v >value-study/results/tests.log 2>&1
$PY value-study/probes.py >value-study/results/probes.log 2>&1
$PY value-study/intervene.py >value-study/results/interventions.log 2>&1
$PY value-study/composition.py >value-study/results/composition.log 2>&1
$PY value-study/entry_features.py >value-study/results/entry-boundaries.log 2>&1
$PY value-study/correction_stages.py >value-study/results/correction-stages.log 2>&1
$PY value-study/filter_diagnostics.py >value-study/results/filter.log 2>&1
$PY value-study/validity_report.py >value-study/results/validity.log 2>&1
$PY value-study/report.py >value-study/results/report.log 2>&1
$PY value-study/validate.py >value-study/results/validation.log 2>&1
$PY value-study/summarize.py >value-study/results/summary.log 2>&1
