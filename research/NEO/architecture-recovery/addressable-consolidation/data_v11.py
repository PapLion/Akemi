"""Controlled exposure only. No architecture edits and no sealed-data reader."""
import sys,copy,itertools,hashlib,json,collections
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'addressable'))
import address_model as A
C=A.C;T=A.T;P=A.P

def oracle(ops,entity):
 state={}
 for op,e,v in ops:
  if op in ['=','!']:state[e]=int(v)
  elif op=='-':state.pop(e,None)
 return state.get(entity,4)

def recode(row,ops,tag='v11'):
 r=copy.deepcopy(row);z=P.make_record(ops,r['q'],tag,'diagnostic');r.update(ops=ops,ids=z['ids'],label=z['label'],id=z['id']);return r

def move(row,initial=(2,3),correction=8,distractor=None):
 r=copy.deepcopy(row);facts=[op for op in r['ops'] if op[0]=='='];assert len(facts)==2
 events=[op for op in r['ops'] if op[0]=='!'];assert len(events)<=1
 ops=[['~',r['q'],'0'] for _ in range(15)]
 for p,f in zip(initial,facts):ops[p]=f
 if events:ops[correction]=events[0]
 if distractor:
  pos,entity,value=distractor;assert pos not in initial and (not events or pos!=correction)
  ops[pos]=['=',entity,str(value)]
 r=recode(r,ops);r.update(stages=[max(initial)//2,correction//2],positions=list(initial),event=correction if events else None)
 return r

def control():return C.data('same')
def treatment():
 rows=[]
 for base in control():
  # Alternating slots: 50% literal unchanged original, 50% valid corrections.
  for variant in range(12):
   r=copy.deepcopy(base);role=(variant//2)//3;delta=1+(variant//2)%3
   if variant%2:
    affected=[r['q'],r['other']][role];old=oracle(r['ops'],affected);ops=copy.deepcopy(r['ops']);ops[8]=['!',affected,str((old+delta)%4)];r=recode(r,ops)
    r.update(kind='correct',affected=affected,event=8,stages=[1,4])
   r.update(base_index=len(rows)//12,variant=variant)
   rows.append(r)
 return rows

def query_other(row):
 r=copy.deepcopy(row);r['q'],r['other']=row['other'],row['q'];return recode(r,r['ops'],'other_query')
def transform(row,kind):
 r=copy.deepcopy(row);ops=r['ops']
 if kind=='swap':
  ix=[i for i,(op,e,v) in enumerate(ops) if op=='='];assert len(ix)==2
  ops[ix[0]][2],ops[ix[1]][2]=ops[ix[1]][2],ops[ix[0]][2]
 elif kind=='obsolete':
  e=r['affected'];ix=next(i for i,(op,ee,v) in enumerate(ops) if op=='=' and ee==e);ops[ix][2]=str((int(ops[ix][2])+1)%4)
 elif kind=='current':
  e=r['q'];ix=max(i for i,(op,ee,v) in enumerate(ops) if op in '=!' and ee==e);ops[ix][2]=str((int(ops[ix][2])+1)%4)
 return recode(r,ops,kind)

def dev_sets():
 corr=[r for r in treatment() if r['kind']=='correct']
 formation=C.data('same',True)
 novel=[]
 for r in formation:
  qi='ABCDE'.index(r['q'])
  for distance in [2,3,4]:
   z=copy.deepcopy(r);new='ABCDE'[(qi+distance)%5];ops=[[op,new if e==r['other'] else e,v] for op,e,v in r['ops']];z['other']=new;novel.append(recode(z,ops,'novel_pair'))
 fixed_novel=[]
 for r in corr:
  z=copy.deepcopy(r);new='ABCDE'[('ABCDE'.index(r['q'])+2)%5];ops=[[op,new if e==r['other'] else e,v] for op,e,v in r['ops']];z['other']=new
  if z['affected']==r['other']:z['affected']=new
  fixed_novel.append(recode(z,ops,'fixed_novel_pair'))
 return dict(formation=formation,novel_pairs=novel,correction_fit=corr,correction_fixed=fixed_novel,
             correction_layout=[move(r,(6,7),10) for r in corr],
             correction_alternate=[move(r,(4,5),10) for r in corr],
             correction_distractor=[move(r,(6,7),10,(8,'ABCDE'[('ABCDE'.index(r['q'])+2)%5],(i//12)%4)) for i,r in enumerate(corr)])

def position_variant(row,step,slot):
 # Data-only third arm. Both factors fixed before inspecting model results.
 initial=[(0,1),(2,3),(4,5)][(step+slot)%3]
 corr=[6,8,10][(step//3+slot)%3]
 return move(row,initial,corr)

def grid():
 # Balanced subsample: q=A/B/C/D/E, all value pairs, one fixed order (80 cases/cell).
 base=[r for r in treatment() if r['kind']=='correct' and r['variant']==1 and r['write_order']==0]
 cells={}
 for initial in [(0,1),(2,3),(4,5),(6,7),(0,3),(3,6)]:
  for corr in [4,5,6,8,9,10,11,12]:
   if corr//2<=max(initial)//2 or corr in initial:continue
   for reverse in [False,True]:
    rr=[move(r,initial,corr) for r in base]
    if reverse:
     rr=[recode(r,[op for op in r['ops']]) for r in rr]
     for r in rr:
      ops=copy.deepcopy(r['ops']);ops[initial[0]],ops[initial[1]]=ops[initial[1]],ops[initial[0]];z=recode(r,ops);r.update(z)
    cells[f'initial{initial[0]}-{initial[1]}_corr{corr}_reverse{int(reverse)}']=rr
 return cells

def sealed():
 # Separate structural family: noncyclic pair, separated initial writes,
 # third entity accepted distractor, rejected proposal to another entity.
 rows=[]
 for r in [r for r in treatment() if r['kind']=='correct']:
  z=copy.deepcopy(r);new='ABCDE'[('ABCDE'.index(r['q'])+3)%5];ops=[[op,new if e==r['other'] else e,v] for op,e,v in r['ops']];z['other']=new
  if z['affected']==r['other']:z['affected']=new
  z=recode(z,ops,'sealed_confirmation');third='ABCDE'[('ABCDE'.index(z['q'])+1)%5]
  z=move(z,(1,4),9,(6,third,(r['variant']//2)%4));z['split']='confirmatory_sealed';rows.append(z)
 return rows

def verify(rows):
 for r in rows:
  assert len(r['ids'])==64
  assert oracle(r['ops'],r['q'])+48==r['label']
  for j in r['stages']:
   for e in [r['q'],r['other']]:assert oracle(r['ops'][:2*j+2],e)==P.oracle(r['ops'][:2*j+2],e)

def frequencies(rows):
 aux=collections.Counter();trans=collections.Counter();kind=collections.Counter()
 for r in rows:
  kind[r['kind']]+=1;j=r['stages'][0]
  for e in [r['q'],r['other']]:aux[e,oracle(r['ops'][:2*j+2],e)]+=1
  if r['kind']=='correct':
   e=r['affected'];old=oracle(r['ops'][:r['event']],e);new=oracle(r['ops'][:r['event']+1],e);trans[e,old,new]+=1
 return dict(auxiliary=[dict(entity=e,value=v,count=n) for (e,v),n in sorted(aux.items())],transitions=[dict(entity=e,old=a,new=b,count=n) for (e,a,b),n in sorted(trans.items())],kinds=dict(kind),records=len(rows),unique_programs=len({tuple(r['ids']) for r in rows}))
