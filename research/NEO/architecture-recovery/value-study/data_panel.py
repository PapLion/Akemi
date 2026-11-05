"""Balanced diagnostic programs; all siblings remain within a layout split."""
import sys,json,hashlib,itertools,collections
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'selective-memory'))
import panel
LAYOUTS={'train':[(0,4,8),(1,5,9)],'dev':[(2,6,10)],'structural':[(3,7,11)]}
def generate(split):
 rows=[]
 for layout,(first,middle,last) in enumerate(LAYOUTS[split]):
  for ei,e in enumerate('ABCDE'):
   other='ABCDE'[(ei+1)%5]
   for old,new,present,regime in itertools.product(range(4),range(4),[0,1],range(4)):
    # Deterministic distractor values independent of labels, and no query-entity accepted writes.
    ops=[['~',other,str((i+ei)%4)] for i in range(15)]
    for i in [2,6,10,13]:ops[i]=['=',other,str(i%4)]
    ops[first]=['=',e,str(old)]
    if regime==1:ops[last]=['!',e,str(new)]
    elif regime==2:ops[middle]=['!',e,str((old+1)%4)];ops[last]=['!',e,str(new)]
    elif regime==3:ops[last]=['!',other,str(new)]
    else:ops[last]=['~',e,str(new)]
    if not present:ops[12]=['-',e,'_']
    else:ops[12]=['x',e,'0']
    ops[14]=['~',e,'3']
    r=panel.make_record(ops,e,str(regime),split);r.update(old=old,new=new,present=present,corrected=int(regime in [1,2]),regime=regime,layout=layout,positions=[first,middle,last],current=(new if regime in [1,2] else old),entity_index=ei)
    assert panel.reverse_oracle(ops,e)==r['answer']==(r['current'] if present else 4)
    rows.append(r)
 return rows
def main():
 manifest={}
 for split in LAYOUTS:
  rows=generate(split);p=R/'data'/f'{split}.jsonl';p.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));manifest[split]={'n':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'present_labels':dict(collections.Counter(r['answer'] for r in rows if r['present']))}
 (R/'data/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
