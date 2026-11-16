"""CPU verification adapter reusing the pending experiment's existing scientific validator."""
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'neo-binding-objective-contrast-v1'))
import gpu

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as td:
        # Safe extractor and CPU verification already used by the research controller.
        gpu.c.a.safe_extract(Path(sys.argv[1]),Path(td))
        results=gpu.verify(Path(td))
        if not results:raise ValueError('No actual model checkpoints found in recovered archive')
        print(json.dumps({'CPU_checkpoint_validation':True,'checkpoints':results}))
