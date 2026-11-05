#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
NEO_PYTHON="${NEO_PYTHON:-/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python}"
"$NEO_PYTHON" -m unittest discover -s tests -v
# No learning or external resources started by this command.
