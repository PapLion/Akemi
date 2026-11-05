from pathlib import Path
import sys,json,hashlib,os
CODE_ROOT=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('NEO_BRIDGE_OUTPUT',str(CODE_ROOT))).resolve()
(ROOT/'results').mkdir(parents=True,exist_ok=True)
PROJECT=CODE_ROOT.parent.parent
# Reuse installed Python3.11 backends read-only; no package installation or venv modification.
V3=PROJECT/'neotoken-v3';SITE=V3/'.venv/lib/python3.11/site-packages'
sys.path.insert(0,str(SITE));sys.path.insert(0,str(V3));sys.path.insert(0,str(CODE_ROOT.parent))
from core import NeoTokenizer,SPECIALS,StreamingEncoder,StreamingDecoder
ARTIFACT=V3/'artifacts/bpe-8192.json'
FP='813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b'
def tokenizer():return NeoTokenizer.load(ARTIFACT,expected_fingerprint=FP)
def sha(x):return hashlib.sha256(x).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=True).encode())
def dump(n,x):(ROOT/'results'/(n+'.json')).write_text(json.dumps(x,indent=2,ensure_ascii=True)+'\n')
