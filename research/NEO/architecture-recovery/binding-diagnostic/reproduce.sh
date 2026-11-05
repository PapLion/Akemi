#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if test -e binding-diagnostic/results/short-17.pt || test -e binding-diagnostic/results/short-resume.pt; then
  echo 'Refusing to overwrite results. Use a fresh worktree and an empty binding-diagnostic/results directory.' >&2
  exit 1
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
"$PY" binding-diagnostic/experiment.py
"$PY" binding-diagnostic/audit.py
"$PY" binding-diagnostic/tests.py
