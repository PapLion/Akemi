"""Seven executable symbolic tasks; no natural-language capability claim."""
from pathlib import Path
import sys,json,hashlib,random
from functools import lru_cache
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent
FP='813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b'
TASKS=['goal','retention','correction','irrelevance','constraint','entities','hypothesis']
@lru_cache(maxsize=1)
def load_tokenizer():
 # Read-only reuse of already installed, pinned tokenizer backend; never modifies it.
 sys.path.append(str(PARENT/'neotoken-v3/.venv/lib/python3.11/site-packages'))
 sys.path.insert(0,str(PARENT/'neotoken-v3'))
 from core import NeoTokenizer
 return NeoTokenizer.load(PARENT/'neotoken-v3/artifacts/bpe-8192.json',expected_fingerprint=FP)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def oracle(records,query,entity):
 fact={};goal={};constraint={};hyp={}
 for op,e,v in records:
  if op in ['!','=']:fact[e]=v
  elif op=='+':goal[e]=v
  elif op=='$':constraint[e]=v
  elif op=='^':hyp[e]=v
  elif op=='-':hyp.pop(e,None)
 return {'?':fact,'>':goal,'<':constraint,'/':hyp}[query][entity]
def build_panel(train_per_task=64,dev_per_task=32):
 tok=load_tokenizer();out=[];seen=set()
 for task in TASKS:
  for split,n in [('train',train_per_task),('dev',dev_per_task)]:
   rng=random.Random(20261101+TASKS.index(task)*100+(split=='dev'));accepted=0;attempt=0
   while accepted<n:
    attempt+=1
    if attempt>100000:raise RuntimeError('Insufficient independent structures')
    e=rng.choice('ABCDEFGH');v=str(rng.randrange(8));ei=ord(e)-65
    if ((ei+int(v))%4==3)!=(split=='dev'):continue
    old=str((int(v)+rng.randrange(1,8))%8);other=rng.choice([x for x in 'ABCDEFGH' if x!=e])
    op={'goal':'+','constraint':'$','hypothesis':'^'}.get(task,'!');query={'goal':'>','constraint':'<','hypothesis':'/'}.get(task,'?')
    core=[(op,e,old if task in ['correction','hypothesis'] else v)]
    if task=='correction':core.append(('=',e,v))
    if task=='hypothesis':core.extend([('-',e,old),('^',e,v)])
    if task=='irrelevance':core.append(('~',e,old))
    if task=='entities':core.append(('!',other,old))
    noise=[]
    for _ in range(7-len(core)):
     nop=rng.choice([':', ';', '#', '%','!']);ne=rng.choice([x for x in 'ABCDEFGH' if x!=e]);noise.append((nop,ne,str(rng.randrange(8))))
    # Preserve meaningful edit order, vary number/location and kinds of distractors.
    records=[core[0]];rest=core[1:];events=noise[:]
    for item in rest:events.insert(rng.randrange(len(events)+1),item)
    # Corrections/hypothesis updates remain ordered relative to one another.
    if task=='hypothesis':
     events=[x for x in events if x not in rest];at=rng.randrange(len(events)+1);events[at:at]=rest
    records+=events
    structure=task+'|'+','.join(op+('T' if ent==e else 'O') for op,ent,val in records)+'|'+query
    if (int(digest(structure)[:8],16)%5==0)!=(split=='dev'):continue
    answer=oracle(records,query,e);assert answer==v
    lines=[op+ent+val+''.join(str(rng.randrange(10)) for _ in range(4))+'\n' for op,ent,val in records]
    lines.append(query+e+'0'+''.join(str(rng.randrange(10)) for _ in range(4))+'\n')
    text=''.join(lines);h=digest(text)
    if h in seen:continue
    ids=tok.encode(text);assert len(ids)==64,(text,ids)
    seen.add(h);out.append({'id':f'{split}-{task}-{accepted:04d}','task':task,'split':split,'family':'program-'+digest(structure)[:16],'structure':structure,'combination':e+':'+v,'text':text,'ids':ids,'answer':answer,'label':tok.encode(answer)[0],'hash':h,'source':'original-executable-DSL-v1','semantics':records,'query':query,'entity':e});accepted+=1
 return out
if __name__=='__main__':
 rows=build_panel();p=ROOT/'results/panel.jsonl';p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 tok=load_tokenizer();manifest={'version':'symbolic-v1','seed':20261101,'tokenizer_fingerprint':tok.fingerprint,'tokenizer_sha256':hashlib.sha256((PARENT/'neotoken-v3/artifacts/bpe-8192.json').read_bytes()).hexdigest(),'records':len(rows),'train':sum(r['split']=='train' for r in rows),'dev':sum(r['split']=='dev' for r in rows),'panel_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'input_tokens':sum(len(r['ids']) for r in rows),'targets':len(rows),'oracle':'tasks.oracle','limitation':'Symbolic typed records, not Spanish/English or broad language; split by queried entity/value combinations and structural program families, not every incidental context pair.'}
 (ROOT/'results/panel-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
