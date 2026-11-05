#!/usr/bin/env bash
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
: "${1:?Usage: reproduce.sh NEW_EMPTY_OUTPUT_DIRECTORY}"
if [ -e "$1" ]; then echo 'Output must not already exist; preserve prior evidence.' >&2; exit 2; fi
mkdir -p -- "$1"
export NEO_BRIDGE_OUTPUT=$(realpath -- "$1")
mkdir "$NEO_BRIDGE_OUTPUT/results"
cp "$SCRIPT_DIR/protocol.json" "$NEO_BRIDGE_OUTPUT/protocol.json"
"$PY" "$SCRIPT_DIR/build_data.py" > "$NEO_BRIDGE_OUTPUT/results/data-build.log" 2>&1
"$PY" "$SCRIPT_DIR/extra_tests.py" > "$NEO_BRIDGE_OUTPUT/results/tests.log" 2>&1
"$PY" "$SCRIPT_DIR/engine.py" > "$NEO_BRIDGE_OUTPUT/results/training.log" 2>&1
"$PY" "$SCRIPT_DIR/evaluation.py" > "$NEO_BRIDGE_OUTPUT/results/evaluation.log" 2>&1
"$PY" "$SCRIPT_DIR/measure.py" > "$NEO_BRIDGE_OUTPUT/results/measure.log" 2>&1
"$PY" "$SCRIPT_DIR/final_checks.py" > "$NEO_BRIDGE_OUTPUT/results/final-checks.log" 2>&1
(cd "$NEO_BRIDGE_OUTPUT" && find results -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
echo "CPU smoke artifacts: $NEO_BRIDGE_OUTPUT"
