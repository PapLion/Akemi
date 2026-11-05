"""V2: the pair is retention scope; the first member is causal current focus.
Both members remain eligible. A change of focus within that pair does not erase Hielo.
"""
import json,hashlib,random,collections,copy,sys,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v1_data_reference',R.parent/'trapos/trapos_data.py');V1=importlib.util.module_from_spec(spec);spec.loader.exec_module(V1)
S=V1.S;D=S.D;ENT=V1.ENT;OPS=V1.OPS;MODES=V1.MODES;digest=V1.digest
INVALID=[(c,n,s) for c in (0,1) for n in (0,1) for s in (0,1) if (c,n,s)!=(1,0,1)]
def oracle(row):return V1.oracle(row)
def refresh(r):
 st,labs=oracle(r);r.update(labels=labs,label=48+st[r['q']],other_label=48+st[r['other']],id=hashlib.sha256(bytes(r['ids'])).hexdigest());return r

def make(q,other,va,vb,delta,role,kind,layout,order,surface,noise,tag):
 goal=q+other;third=next(e for e in ENT if e not in goal);facts=[(q,va,1,0,'initial'),(other,vb,1,0,'initial')]
 if order:facts.reverse()
 affected=goal[role];old=va if role==0 else vb
 change=(affected,(old+delta)%4 if kind=='correction' else old,1,0,kind)
 bad=[]
 for j in range(2):
  c,n,scope=INVALID[(noise+j*3)%7];e=goal[(noise+j)%2] if scope else third;v=(va+vb+noise+j)%4
  typ='out_of_goal' if not scope else 'negated' if n and c else 'quoted' if n else 'hypothesis'
  bad.append((e,v,c,n,typ))
 patterns={0:[facts[0],facts[1],bad[0],change,bad[1]],1:[bad[0],facts[0],facts[1],bad[1],change],2:[facts[0],bad[0],facts[1],change,bad[1]],3:[bad[1],facts[1],facts[0],bad[0],change]}
 events=patterns[layout];records=[];metadata=[];state={}
 for j,(e,v,c,n,typ) in enumerate(events):
  records.extend([f'@{goal};',f'{MODES[surface%4]}{c}{n};',f'{OPS[(surface+j+order)%5]}{e}{v};','_x0;'])
  accept=bool(c and not n and e in goal);before=copy.deepcopy(state)
  if accept:state[e]=v
  metadata.append({'entity':e,'value':v,'type':typ,'confirmed':c,'negated':n,'in_scope':e in goal,'accepted':accept,'before':before,'after':copy.deepcopy(state),'record':4*j+2})
 records.extend([f'@{goal};','_x0;','_x0;',f'?{q}?;'])
 r={'ids':list(''.join(records).encode()),'q':q,'other':other,'goal':goal,'events':metadata,'kind':kind,'affected':affected,'layout':layout,'surface':surface,'initial_values':[va,vb],'tag':tag,'initial_focus':q}
 return refresh(r)

def focus_query(row,which):
 r=copy.deepcopy(row);q=which;other=next(e for e in row['goal'] if e!=q);r.update(q=q,other=other)
 r['ids'][-16:-12]=list(f'@{q}{other};'.encode());r['ids'][-4:]=list(f'?{q}?;'.encode());return refresh(r)
def other_query(r):return focus_query(r,r['other'])

def train(seed):
 rng=random.Random(seed);rows=[]
 for k in range(1200):
  q=ENT[k%5];others=[e for e in ENT if e!=q and tuple(sorted((e,q)))!=('A','C')];other=others[rng.randrange(len(others))]
  r=make(q,other,(k//5)%4,(k//20)%4,1+(k//80)%3,(k//2)%2,'correction' if k%2 else 'repeat',rng.randrange(2),rng.randrange(2),rng.randrange(2),k%7,'train')
  a=focus_query(r,q);b=focus_query(r,other)
  rows.extend([a,b] if k%2 else [b,a])
 return rows

def dev():
 out={}
 for family in ['contaminated_pair','layout','surface','clean','focus_change']:
  rows=[]
  for k in range(192):
   q='AC'[k%2];other='C' if q=='A' else 'A'
   r=make(q,other,(k//2)%4,(k//8)%4,1+(k//32)%3,(k//96)%2,'correction',2+k%2 if family=='layout' else (k//16)%2,k//4%2,2+k%2 if family=='surface' else (k//8)%2,k%7,family)
   if family=='clean':
    for ev in r['events']:
     if ev['accepted']:continue
     p=ev['record']*4;prefix=copy.deepcopy(r);prefix['ids']=r['ids'][:p]+list(('_x0;'*((96-p)//4)).encode());st,_=oracle(prefix);e=q;v=st.get(e,r['initial_values'][0]);r['ids'][p:p+4]=list(f'={e}{v};'.encode());r['ids'][p-4:p]=list('$10;'.encode());ev.update(entity=e,value=v,type='clean_repeat',confirmed=1,negated=0,in_scope=True,accepted=True)
    refresh(r)
   r=focus_query(r,other if family=='focus_change' or (k//2)%2 else q);rows.append(r)
  out[family]=rows
 return out
counterfactual=V1.counterfactual

def frequencies(rr):
 out=V1.frequencies(rr);cross=collections.Counter();slot=collections.Counter();cond=collections.Counter();correct=collections.Counter();tot=0
 for r in rr:
  slot[r['goal'].index(r['q'])]+=1
  for j,ev in enumerate(r['events']):
   p=ev['record']*4;mode=r['ids'][p-4:p];c=mode[1]==49;n=mode[2]==49;s=chr(r['ids'][p+1]) in r['goal'];y=r['labels'][j];cross[c,n,s,y]+=1;cond[chr(r['ids'][p+1]),r['ids'][p+2]-48,y]+=1
   preds={'all':True,'confirmed':c,'goal':s,'confirmed_nonnegated':c and not n,'conjunction':c and not n and s}
   for name,a in preds.items():correct[name]+=a==y
   tot+=1
 out.update(query_slot=dict(slot),factorial=[{'confirmed':c,'negated':n,'in_scope':s,'accepted':y,'n':v} for (c,n,s,y),v in sorted(cross.items())],entity_value_acceptance=[{'entity':e,'value':v,'accepted':a,'n':n} for (e,v,a),n in sorted(cond.items())],heuristic_selection_accuracy={k:v/tot for k,v in correct.items()})
 return out
