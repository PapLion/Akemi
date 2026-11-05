"""Atomic symbolic fixtures. No tokenizer changes, no sealed evaluation reads."""
import random,json,hashlib,copy,collections,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TASKS=['retain','replace','multiple','other','similar','irrelevant','discard','goal']
ENTITIES='ABCDE'
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def heldout_pair(e,a):return (ENTITIES.index(e)+a)%5==4
def oracle(ops,query):
 state={};goal=None
 for op,e,v in ops:
  if op in ['=','!']:state[e]=int(v)
  elif op=='-':state.pop(e,None)
  elif op=='>':goal=e
 q=goal if query=='*' else query
 return state.get(q,4)
def reverse_oracle(ops,query):
 if query=='*':query=next((e for op,e,v in reversed(ops) if op=='>'),None)
 for op,e,v in reversed(ops):
  if e==query:
   if op=='-':return 4
   if op=='=' or op=='!':return int(v)
 return 4
def encode(ops,query):return [ord(c) for op,e,v in ops+[[('*' if query=='*' else '?'),('_' if query=='*' else query),'_']] for c in op+e+str(v)+';']
def make_record(ops,query,task,split):
 e=next(e for op,e,v in reversed(ops) if op=='>') if query=='*' else query
 ans=oracle(ops,query);family=digest([(op,'Q' if ent==e else 'D') for op,ent,val in ops]+[query=='*']);bucket=int(family[:8],16)%10
 ids=encode(ops,query);latest=max((i for i,(op,ee,v) in enumerate(ops) if ee==e and op in '=!-'),default=-1)
 return dict(id=digest(ids),task=task,split=split,ops=ops,query=query,entity=e,answer=ans,label=48+ans,ids=ids,family=family,family_bucket=bucket,last_valid_record=latest,outside_window=latest<12)
def sample(rng,task,e,ans,split,recent):
 other=(ENTITIES[(ENTITIES.index(e)+1)%5] if task=='similar' else rng.choice([x for x in ENTITIES if x!=e]));old=rng.choice([x for x in range(4) if x!=ans]);chain=[['=',e,str(old)]]
 if task=='goal':chain=[['>',other,'_']]+chain
 if task=='multiple':chain += [['!',e,str((old+1)%4)]]
 if task=='discard' and ans!=4:chain += [['-',e,'_']]
 if ans==4:chain += [['-',e,'_']]
 else:chain += [['!',e,str(ans)]]
 if task in ['retain','other','similar','irrelevant'] and ans!=4:chain=[['=',e,str(ans)]]
 if task=='goal':chain += [['>',e,'_']]
 # Accepted state updates are ordered, positions are randomized. Last accepted update may be recent.
 n=len(chain);positions=sorted(rng.sample(range(10),n))
 if recent:
  # Final event refers to goal in goal task; place actual value update at14 and goal before it.
  if task=='goal':chain[-2],chain[-1]=chain[-1],chain[-2]
  positions=sorted(rng.sample(range(10),n-1))+[12]
 ops=[];pending=dict(zip(positions,chain))
 for i in range(15):
  if i in pending:ops.append(pending[i]);continue
  ee=rng.choice(ENTITIES);op=rng.choice(['=','!','~','x'])
  if ee==e and op in '=!':op=rng.choice(['~','x'])
  ops.append([op,ee,str(rng.randrange(4))])
 ops[13]=['!',other,str(rng.randrange(4))]
 ops[14]=[rng.choice(['~','x']),e,str(rng.randrange(4))]
 r=make_record(ops,'*' if task=='goal' else e,task,split)
 assert r['answer']==ans
 return r
def generate(split,per_cell=4,training_templates=None):
 if split not in ['train','iid','compositional','structural','both','final']:raise ValueError(split)
 if split in ['iid','compositional']:return seen_structure(split,per_cell,training_templates)
 rng=random.Random({'train':1701,'iid':2901,'compositional':4301,'structural':7101,'both':9701,'final':13001}[split]);rows=[];seen=set()
 for task in TASKS:
  for e in ENTITIES:
   for ans in range(5):
    want_hold=split in ['compositional','both']
    if split!='final' and heldout_pair(e,ans)!=want_hold:continue
    for k in range(per_cell):
     for attempt in range(100000):
      r=sample(rng,task,e,ans,split,recent=k%2==1)
      bucket=r['family_bucket'];ok=bucket<6 if split in ['train','iid','compositional'] else (bucket in [6,7] if split in ['structural','both'] else bucket>=8)
      if ok and r['id'] not in seen:break
     else:raise RuntimeError('Unable to obtain independent family')
     seen.add(r['id']);rows.append(r)
 return rows
def seen_structure(split,per_cell,templates=None):
 templates=generate('train',per_cell) if templates is None else templates
 rng=random.Random(2901 if split=='iid' else 4301);out=[];seen={r['id'] for r in templates}
 for task in TASKS:
  for e in ENTITIES:
   for ans in range(5):
    if heldout_pair(e,ans)!=(split=='compositional'):continue
    for k in range(per_cell):
     pool=[r for r in templates if r['task']==task and (r['answer']==4)==(ans==4) and r['outside_window']==(k%2==0)]
     # Tiny unit-test panels have only far examples; same contract at that scope.
     if not pool:pool=[r for r in templates if r['task']==task and (r['answer']==4)==(ans==4)]
     for attempt in range(1000):
      src=rng.choice(pool);mapping={src['entity']:e};old=[x for x in ENTITIES if x!=src['entity']];new=[x for x in ENTITIES if x!=e];rng.shuffle(new);mapping.update(zip(old,new))
      ops=[[op,mapping[ee],str(rng.randrange(4)) if v!='_' else '_'] for op,ee,v in src['ops']]
      last=src['last_valid_record']
      if ans!=4:ops[last][2]=str(ans)
      q='*' if src['query']=='*' else e;r=make_record(ops,q,task,split)
      assert r['family']==src['family'] and r['answer']==ans
      if r['id'] not in seen:break
     else:raise RuntimeError('No fresh instantiation')
     seen.add(r['id']);out.append(r)
 return out

def counterfactual(r,kind):
 q=copy.deepcopy(r);e=r['entity'];ops=q['ops'];valid=[i for i,(op,ee,v) in enumerate(ops) if ee==e and op in '=!-'];last=valid[-1]
 if kind=='obsolete':
  choices=[i for i in valid if i<last and ops[i][0]!='-']
  if not choices:return None
  i=choices[0];ops[i][2]=str((int(ops[i][2])+1)%4)
 elif kind=='valid':
  if ops[last][0]=='-':ops[last]=['!',e,'0']
  else:ops[last][2]=str((int(ops[last][2])+1)%4)
 else:raise ValueError(kind)
 q=make_record(ops,q['query'],q['task'],q['split']);assert reverse_oracle(ops,q['query'])==q['answer'];return q
def heuristic(r,kind):
 oo=r['ops'];e=r['entity']
 if kind=='first':return next((int(v) for op,ee,v in oo if op in '=!'),4)
 if kind=='last':return next((int(v) for op,ee,v in reversed(oo) if op in '=!'),4)
 if kind=='entity_last_any':return next((4 if op=='-' else int(v) for op,ee,v in reversed(oo) if ee==e and op in ['=','!','~','x','-']),4)
 if kind=='entity_valid':return reverse_oracle(oo,r['query'])
 raise ValueError(kind)
def load(split):
 if split=='final':raise ValueError('Final sealed: not accessible to training/evaluation runner')
 return [json.loads(s) for s in (ROOT/'data-v4'/f'{split}.jsonl').read_text().splitlines()]
def build():
 d=ROOT/'data-v4';d.mkdir(exist_ok=True);manifest={'version':'selective-v4','atomic_ids':'Unicode ASCII fixture; no learned tokenizer modified','splits':{}};sets={};audit={}
 for split in ['train','iid','compositional','structural','both','final']:
  rows=generate(split,4 if split=='train' else 2,sets.get('train'));sets[split]=rows
  for r in rows:assert oracle(r['ops'],r['query'])==reverse_oracle(r['ops'],r['query'])==r['answer']
  p=d/('sealed-final.jsonl' if split=='final' else split+'.jsonl')
  if p.exists():raise FileExistsError(p)
  p.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));manifest['splits'][split]={'n':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'families':len({r['family'] for r in rows}),'answers':dict(collections.Counter(r['answer'] for r in rows))}
  if split=='final':p.chmod(0);continue
  audit[split]={'n':len(rows),'outside_window':sum(r['outside_window'] for r in rows),'heuristics':{h:sum(heuristic(r,h)==r['answer'] for r in rows)/len(rows) for h in ['first','last','entity_last_any','entity_valid']},'by_task':{t:{h:sum(heuristic(r,h)==r['answer'] for r in rows if r['task']==t)/sum(r['task']==t for r in rows) for h in ['first','last','entity_last_any']} for t in TASKS}}
 for i,a in enumerate(sets):
  for b in list(sets)[i+1:]:assert not {r['id'] for r in sets[a]}&{r['id'] for r in sets[b]},(a,b)
 (ROOT/'results/panel-v4-audit.json').write_text(json.dumps(audit,indent=2));(d/'manifest.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':build()
