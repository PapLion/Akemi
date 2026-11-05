#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python corpus-recovery-f2/catalog.py
python corpus-recovery-f2/recover.py
"$PY" corpus-recovery-f2/count_v3.py --seconds 120
python corpus-recovery-f2/selection.py
"$PY" corpus-recovery-f2/f2.py
"$PY" corpus-recovery-f2/real_preflight.py
"$PY" corpus-recovery-f2/benchmark_isolated.py
"$PY" -m unittest discover -s corpus-recovery-f2 -p 'test_*.py'
python corpus-recovery-f2/finalize.py
python corpus-recovery-f2/reports.py
python corpus-recovery-f2/hashes.py
python corpus-recovery-f2/verify_hashes.py
# Never launches corpus training. Gate is available separately in selection.py.
