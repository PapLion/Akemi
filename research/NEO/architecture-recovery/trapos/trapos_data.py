"""Causal DSL: goal + two contextual bits + proposal. No oracle in normal forward."""
import json,hashlib,random,collections,copy,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'stability'))
import study as S
D=S.D
ENT='ABCDE';OPS='=!~^+';MODES='$#%&'
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def make(q,other,va,vb,delta,role,kind,layout,order,surface,noise,tag):
 # All proposals share the same extraction grammar; opcode does not decide truth.
 goal=q+other;third=next(e for e in ENT if e not in goal)
 facts=[(q,va,1,0,'initial'),(other,vb,1,0,'initial')]
 if order:facts.reverse()
 affected=q if role==0 else other
 val=( (va if role==0 else vb)+delta)%4
 challenge=(affected,val,1,0,'correction') if kind=='correction' else (affected,va if role==0 else vb,1,0,'repeat')
 badtypes=[(q,(va+1)%4,0,0,'hypothesis'),(other,(vb+2)%4,1,1,'negated'),(third,noise,1,0,'out_of_goal'),(q,(va+3)%4,0,1,'quoted')]
 bad1=badtypes[noise%4];bad2=badtypes[(noise+1)%4]
 patterns={0:[facts[0],facts[1],bad1,challenge,bad2],1:[bad1,facts[0],facts[1],bad2,challenge],2:[facts[0],bad1,facts[1],challenge,bad2],3:[bad2,facts[1],facts[0],bad1,challenge]}
 events=patterns[layout];records=[];labels=[];metadata=[];state={}
 for j,(e,v,confirmed,negated,typ) in enumerate(events):
  # Surface aliases have identical declared grammar; truth requires both bits AND goal membership.
  prefix=MODES[surface%4];op=OPS[(surface+j+order)%len(OPS)]
  records.extend([f'@{goal};',f'{prefix}{confirmed}{negated};',f'{op}{e}{v};','_x0;'])
  accept=bool(confirmed and not negated and e in goal)
  before=copy.deepcopy(state)
  if accept:state[e]=v
  labels.append(accept);metadata.append({'entity':e,'value':v,'type':typ,'confirmed':confirmed,'negated':negated,'accepted':accept,'before':before,'after':copy.deepcopy(state),'record':4*j+2})
 records.extend([f'@{goal};','_x0;','_x0;',f'?{q}?;'])
 ids=list(''.join(records).encode('ascii'));assert len(ids)==96
 return {'id':hashlib.sha256(bytes(ids)).hexdigest(),'ids':ids,'q':q,'other':other,'goal':goal,'label':48+state[q],'other_label':48+state[other],'labels':labels,'events':metadata,'kind':kind,'affected':affected,'layout':layout,'surface':surface,'initial_values':[va,vb],'tag':tag}
def oracle(row):
 # Independent parser, no access to metadata/labels.
 st={};goal='';confirmed=negated=None;out=[]
 for pos in range(0,96,4):
  op,e,v,end=map(chr,row['ids'][pos:pos+4]);assert end==';'
  if op=='@':goal=e+v
  elif op in MODES:confirmed=int(e);negated=int(v)
  elif op in OPS:
   a=confirmed==1 and negated==0 and e in goal;out.append(a)
   if a:st[e]=int(v)
 return st,out

def train(seed):
 rng=random.Random(seed);rr=[]
 # 2400 paired examples, half corrections; equal affected/preserved query roles.
 for k in range(2400):
  q=ENT[rng.randrange(5)];choices=[e for e in ENT if e!=q and tuple(sorted((e,q)))!=('A','C')];other=choices[rng.randrange(len(choices))]
  va,vb=rng.randrange(4),rng.randrange(4);delta=1+rng.randrange(3);role=(k//2)%2;kind='correction' if k%2 else 'repeat'
  rr.append(make(q,other,va,vb,delta,role,kind,rng.randrange(2),rng.randrange(2),rng.randrange(2),rng.randrange(4),'train'))
 return rr

def dev():
 out={}
 for family in ['contaminated_pair','layout','surface','clean']:
  rows=[]
  for k in range(192):
   q='AC'[k%2];other='C' if q=='A' else 'A';va=(k//2)%4;vb=(k//8)%4;delta=1+(k//32)%3;role=(k//96)%2
   layout=2+(k%2) if family=='layout' else (k//16)%2;surface=2+k%2 if family=='surface' else (k//8)%2
   r=make(q,other,va,vb,delta,role,'correction',layout,k//4%2,surface,(k//3)%4,family)
   if family=='clean':
    # No invalid proposals in the clean reference: replace them with valid repeats.
    for ev in r['events']:
     if ev['accepted']:continue
     pos=ev['record']*4;entity=q;value=va
     # Initial repeats must not alter a later correction: use prefix oracle's valid value.
     partial=copy.deepcopy(r);partial['ids']=r['ids'][:pos]+list(('_x0;'*((96-pos)//4)).encode());st,_=oracle(partial);value=st.get(entity,va)
     r['ids'][pos:pos+4]=list(f'={entity}{value};'.encode());r['ids'][pos-4:pos]=list('$10;'.encode())
    st,labs=oracle(r);r.update(label=48+st[q],other_label=48+st[other],labels=labs,id=hashlib.sha256(bytes(r['ids'])).hexdigest())
    for j,ev in enumerate(r['events']):ev.update(type='clean_repeat',accepted=labs[j])
   rows.append(r)
  out[family]=rows
 return out

def other_query(r):
 z=copy.deepcopy(r);z['q'],z['other']=r['other'],r['q'];z['label']=r['other_label'];z['other_label']=r['label'];z['ids'][-4:]=list(f'?{z["q"]}?;'.encode());z['id']=hashlib.sha256(bytes(z['ids'])).hexdigest();return z

def counterfactual(row,kind):
 z=copy.deepcopy(row);positions=[4*j+2 for j in range(5)];target=z['q']
 if kind=='invalid':
  for j,p in enumerate(positions):
   if not z['labels'][j]:z['ids'][p*4+2]=48+(z['ids'][p*4+2]-48+1)%4
 else:
  # Current: last accepted query write. Obsolete: earlier accepted write of same query, only when replaced later.
  ix=[(j,p) for j,p in enumerate(positions) if z['labels'][j] and chr(z['ids'][p*4+1])==target]
  if kind=='obsolete' and len(ix)<2:return None
  j,p=ix[-1] if kind=='current' else ix[0];z['ids'][p*4+2]=48+(z['ids'][p*4+2]-48+1)%4
 st,labs=oracle(z);z.update(label=48+st[z['q']],other_label=48+st[z['other']],labels=labs,id=hashlib.sha256(bytes(z['ids'])).hexdigest());return z

def frequencies(rr):
 cc=collections.Counter();targets=collections.Counter();heur=collections.Counter();ops=collections.defaultdict(collections.Counter)
 for r in rr:
  for j,p in enumerate([2,6,10,14,18]):
   flag=r['labels'][j];cc['accept' if flag else 'reject']+=1;op=chr(r['ids'][p*4]);ops[op][str(flag)]+=1
  targets[r['q'],r['label']-48]+=1
  writes=[(chr(r['ids'][p*4+1]),r['ids'][p*4+2]-48) for p in [2,6,10,14,18]];y=r['label']-48
  for name,v in [('first',next(v for e,v in writes if e==r['q'])),('last_global',writes[-1][1]),('last_entity',next(v for e,v in reversed(writes) if e==r['q'])),('presence',0)]:heur[name]+=v==y
 return {'records':len(rr),'input_ids':96*len(rr),'answer_targets':len(rr),'proposal_targets':5*len(rr),'selection_counts':dict(cc),'targets':[{'entity':e,'value':v,'n':n} for (e,v),n in sorted(targets.items())],'opcode_labels':dict(ops),'heuristics':{k:v/len(rr) for k,v in heur.items()},'unique':len({r['id'] for r in rr})}
