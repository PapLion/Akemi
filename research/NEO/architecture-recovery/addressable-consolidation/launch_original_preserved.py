"""Refuse main training if the preregistered code or protocol changed."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
freeze=json.loads((R/'results/FREEZE.json').read_text())
for rel,expected in freeze['files'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==expected,rel
import runner_v11
runner_v11.main()
