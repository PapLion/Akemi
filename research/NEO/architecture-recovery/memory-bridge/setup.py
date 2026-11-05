"""V2 experiment imports the frozen V1 implementation, without editing it."""
from pathlib import Path
import sys,os,json,hashlib,random,time,math,resource,itertools
CODE=Path(__file__).resolve().parent
BASE=CODE.parent
sys.path.insert(0,str(BASE/'language-bridge'))
from model import LanguageBridge,Session,create,optimizer
from common import tokenizer,FP,ARTIFACT
import torch
import torch.nn.functional as F
OUT=Path(os.environ.get('NEO_MEMORY_OUTPUT',str(CODE)))
(OUT/'results').mkdir(parents=True,exist_ok=True)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
def file_sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_json(name,x):
 p=OUT/'results'/f'{name}.json'
 if p.exists():raise FileExistsError(f'Preserve evidence: {p}')
 p.write_text(json.dumps(x,indent=2,ensure_ascii=True)+'\n')
def read(name):return json.loads((OUT/'results'/f'{name}.json').read_text())
torch.set_num_threads(1)
