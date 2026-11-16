"""CPU verification adapter reusing the pending experiment's existing scientific validator."""
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
# Reuse the existing V3 dependency environment, as the historical CPU commands do.
# The lifecycle service itself deliberately uses stdlib-only Python.
dependencies=ROOT.parent/'neotoken-v3/.venv/lib/python3.11/site-packages'
if dependencies.is_dir():sys.path.insert(0,str(dependencies))
sys.path.insert(0,str(ROOT/'neo-binding-objective-contrast-v1'))
import gpu

if __name__=='__main__':
    if sys.argv[1:] == ['--import-check']:
        print(json.dumps({'scientific_validator_imports':'PASS','existing_V3_dependencies':str(dependencies)}))
        raise SystemExit(0)
    with tempfile.TemporaryDirectory() as td:
        # Safe extractor and CPU verification already used by the research controller.
        gpu.c.a.safe_extract(Path(sys.argv[1]),Path(td))
        results=gpu.verify(Path(td))
        if not results:raise ValueError('No actual model checkpoints found in recovered archive')
        print(json.dumps({'CPU_checkpoint_validation':True,'checkpoints':results}))
