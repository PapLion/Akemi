"""Reporting-only guard: an unchanged-association rate is undefined if all query values change.
Static copy of existing evaluator; logits/losses/labels/metrics otherwise untouched.
No model or training function modified.
"""
import torch
import torch.nn.functional as F
from runner_v11 import T
losses=T.losses
stage=T.stage
def evaluate(m,d,rows):
 accum={};states=[];predictions=[]
 with torch.no_grad():
  for start in range(0,len(rows),16):
   batch=rows[start:start+16];lm,a,b,logits,tr=losses(m,d,batch);st=[a,b,stage(m,d,batch,tr,2)]
   for bi,r in enumerate(batch):
    row=dict(id=r['id'],kind=r['kind'],q=r['q'],other=r['other'],affected=r['affected'],original_prediction=int(logits[bi,-1].argmax()),original_label=r['label'],stages={})
    for name,ss in zip(['initial','post','retained'],st):
     ll=ss[1][2*bi:2*bi+2];yy=ss[2][2*bi:2*bi+2];row['stages'][name]=dict(pred=ll.argmax(-1).tolist(),label=yy.tolist(),ce=F.cross_entropy(ll,yy,reduction='none').tolist())
    predictions.append(row);states.append(torch.stack([tr[j]['memory'][bi].cpu() for j in [r['stages'][0],r['stages'][1],6]]))
 for kind in ['all','preserve','correct']:
  records=[r for r in predictions if kind=='all' or r['kind']==kind];n=len(records);metrics={}
  if not n:continue
  for name in ['initial','post','retained']:
   correct=[[int(r['stages'][name]['pred'][i]==r['stages'][name]['label'][i]) for i in range(2)] for r in records]
   conf={}
   for r in records:
    for i,e in enumerate([r['q'],r['other']]):
     conf.setdefault(e,[[0]*4 for _ in range(4)]);conf[e][r['stages'][name]['label'][i]][r['stages'][name]['pred'][i]]+=1
   metrics[name]=dict(A_accuracy=sum(v[0] for v in correct)/n,B_accuracy=sum(v[1] for v in correct)/n,joint_accuracy=sum(all(v) for v in correct)/n,ce_A=sum(r['stages'][name]['ce'][0] for r in records)/n,ce_B=sum(r['stages'][name]['ce'][1] for r in records)/n,confusion_per_entity=conf)
  metrics['original_accuracy']=sum(r['original_prediction']==r['original_label'] for r in records)/n
  denominator=sum(r['stages']['initial']['label'][0]==r['stages']['post']['label'][0] for r in records)
  metrics['unjustified_changes_A']=(sum(r['stages']['initial']['pred'][0]!=r['stages']['post']['pred'][0] for r in records if r['stages']['initial']['label'][0]==r['stages']['post']['label'][0])/denominator) if denominator else None
  accum[kind]=metrics
 return dict(metrics=accum,predictions=predictions),torch.stack(states)
