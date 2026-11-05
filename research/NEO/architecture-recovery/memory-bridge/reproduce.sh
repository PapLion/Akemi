#!/usr/bin/env bash
set -euo pipefail
: "${1:?Usage: reproduce.sh NEW_EMPTY_OUTPUT_DIRECTORY}"
if [ -e "$1" ]; then echo 'Output exists; refusing to overwrite evidence.' >&2; exit 2; fi
mkdir -p -- "$1"
export NEO_MEMORY_OUTPUT=$(realpath -- "$1")
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
DIR=$(cd -- "$(dirname -- "$0")" && pwd)
mkdir "$NEO_MEMORY_OUTPUT/results"
cp "$DIR/protocol.json" "$NEO_MEMORY_OUTPUT/protocol.json"
"$PY" "$DIR/data.py" > "$NEO_MEMORY_OUTPUT/results/data-build.log" 2>&1
"$PY" "$DIR/tests.py" > "$NEO_MEMORY_OUTPUT/results/tests.log" 2>&1
"$PY" "$DIR/positive_controls.py" > "$NEO_MEMORY_OUTPUT/results/positive-controls.log" 2>&1
"$PY" "$DIR/intervention_tests.py" > "$NEO_MEMORY_OUTPUT/results/intervention-tests.log" 2>&1
"$PY" "$DIR/runner.py" > "$NEO_MEMORY_OUTPUT/results/training.log" 2>&1
# This protocol stops here if the prerequisite microfit fails. Never force400-step runs.
"$PY" "$DIR/diagnostics.py" > "$NEO_MEMORY_OUTPUT/results/diagnosis.log" 2>&1
"$PY" "$DIR/final_metrics.py" > "$NEO_MEMORY_OUTPUT/results/final-metrics.log" 2>&1
"$PY" "$DIR/seal.py" > "$NEO_MEMORY_OUTPUT/results/seal.log" 2>&1
(cd "$NEO_MEMORY_OUTPUT" && find results -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
echo "Bounded CPU experiment complete: $NEO_MEMORY_OUTPUT; inspect micro-gate.json. No pretraining authorized."
