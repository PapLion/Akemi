#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# Use a clean output copy/worktree: scripts refuse existing evidence.
"$PY" language-foundation/pilot.py
"$PY" language-foundation/analysis.py
"$PY" language-foundation/checks.py
"$PY" language-foundation/diagnostics.py
"$PY" language-foundation/reports.py
