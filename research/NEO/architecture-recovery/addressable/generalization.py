"""Post-training diagnostic only: no optimizer, no hyperparameter selection."""
import copy
import torch
import run_addressable as R
from analyze_addressable import correction_panel,evaluate
A=R.A;C=R.C;T=R.T;O=R.O

def recode(r):
 z=C.P.make_record(r['ops'],r['q'],'diagnostic','diagnostic');r.update(ids=z['ids'],label=z['label']);return r

def main():
 rows=C.data('same');m,d,*_=A.restore(O/'main.pt',rows);m.eval();pan=correction_panel('same');report={}
 for name,rr in [('bang',pan),('equals',[recode(dict(copy.deepcopy(r),ops=[['=' if op=='!' else op,e,v] for op,e,v in r['ops']])) for r in pan])]:
  ev=evaluate(m,d,rr,'diagnostic-correction-'+name);p=[r for r in ev['predictions'] if r['kind']=='correct'];counts={}
  for relation in ['affected','unmodified']:
   n=good=0
   for pred,row in zip(ev['predictions'],rr):
    if row['kind']!='correct':continue
    role=(0 if row['affected']==row['q'] else 1);role=role if relation=='affected' else 1-role
    good+=pred['stages']['post']['pred'][role]==pred['stages']['post']['label'][role];n+=1
   counts[relation]=dict(n=n,accuracy=good/n)
  report[name]=dict(metrics=ev['metrics'],by_role=counts)
 novel=[]
 for r in C.data('same',True):
  qi='ABCDE'.index(r['q'])
  for distance in [2,3,4]:
   z=copy.deepcopy(r);new='ABCDE'[(qi+distance)%5];z['ops']=[[op,new if e==r['other'] else e,v] for op,e,v in z['ops']];z['other']=new;novel.append(recode(z))
 ev=evaluate(m,d,novel,'unseen-entity-pairs');report['unseen_pairs']=ev['metrics'];report['scope']='Unseen pairings, same five entity tokens/four values, new layouts; no unseen vocabulary or language claim.'
 R.dump('generalization.json',report)
 print({k:(v.get('by_role') if isinstance(v,dict) else v) for k,v in report.items() if k!='unseen_pairs'});print('novel',ev['metrics']['all']['initial']['joint_accuracy'],ev['metrics']['all']['original_accuracy'])
if __name__=='__main__':main()
