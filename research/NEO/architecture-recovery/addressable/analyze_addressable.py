import copy,json,time,sys,hashlib,statistics
import torch
import torch.nn.functional as F
import run_addressable as R
A=R.A;T=R.T;C=R.C;O=R.O
sys.path.insert(0,str(O.parent.parent/'multiwrite'))
from mw_analyze import modified,correction_panel,joint_pairs

def evaluate(m,d,rows,name):
 ev,states=T.evaluate(m,d,rows);R.dump(name+'.json',ev);torch.save(states,O/(name+'-states.pt'));return ev

def main():
 if not (O/'main.pt').exists():return
 rows=C.data('same');m,d,o,rng,step=A.restore(O/'main.pt',rows);m.eval()
 report={}
 for split,rr in [('train',rows),('layout',C.data('same',True))]:
  a=evaluate(m,d,rr,'analysis-'+split)
  sw=[modified(r,'swap') for r in rr];b=evaluate(m,d,sw,'analysis-'+split+'-swap')
  ix=[i for i,r in enumerate(rr) if r['initial_values'][0]!=r['initial_values'][1]]
  sub=lambda ev:dict(predictions=[ev['predictions'][i] for i in ix])
  both=[]
  for r in rr:
   z=copy.deepcopy(r);z['q'],z['other']=r['other'],r['q'];rrr=C.P.make_record(z['ops'],z['q'],'query_other','diagnostic');z.update(ids=rrr['ids'],label=rrr['label']);both.append(z)
  other=evaluate(m,d,both,'analysis-'+split+'-other-query')
  functional=sum(x['original_prediction']==x['original_label'] and y['original_prediction']==y['original_label'] for x,y in zip(a['predictions'],other['predictions']))/len(rr)
  report[split]=dict(swap=joint_pairs(sub(a),sub(b)),normal_both_accuracy=functional,normal_other_accuracy=other['metrics']['all']['original_accuracy'])
 panel=correction_panel('same');ev=evaluate(m,d,panel,'corrections-controlled');report['corrections']=ev['metrics']
 cf=[r for r in panel if r['kind']=='correct'];base=evaluate(m,d,cf,'cf-base')
 for mode in ['obsolete','current']:
  changed=evaluate(m,d,[modified(r,mode) for r in cf],'cf-'+mode);pair=joint_pairs(base,changed,'post')
  p=base['predictions'];q=changed['predictions'];pair['normal_prediction_invariance']=sum(x['original_prediction']==y['original_prediction'] for x,y in zip(p,q))/len(p)
  report[mode]=pair
 x=torch.tensor([r['ids'] for r in rows]);normal=[];reset=[];swapped=[]
 with torch.no_grad():
  for i in range(0,len(rows),16):
   xx=x[i:i+16];normal.extend(m(xx)[:,-1].argmax(-1).tolist());reset.extend(m(xx,intervention='reset')[:,-1].argmax(-1).tolist());swapped.extend(m(xx,intervention='swap')[:,-1].argmax(-1).tolist())
 labels=[r['label'] for r in rows];report['interventions']={name:dict(accuracy=sum(p==y for p,y in zip(pred,labels))/len(rows),prediction_change=sum(p!=q for p,q in zip(pred,normal))/len(rows)) for name,pred in [('normal',normal),('reset',reset),('batch_swap',swapped)]}
 # Report learned address geometry, not a proxy for functional success.
 with torch.no_grad():
  keys=F.normalize(m.core.address(m.core.emb(torch.tensor([ord(e) for e in 'ABCDE']))),dim=-1)
 report['address_gram']=(keys@keys.T).tolist()
 # Fair fixed order check versus immutable historical baseline logs.
 previous=O.parent.parent.parent/'cryo-multiwrite-v1/multiwrite/results/A-curves.json'
 old=json.loads(previous.read_text());new=json.loads((O/'main-curve.json').read_text());assert [r['indices'] for r in old]==[r['indices'] for r in new]
 report['same_batch_order_as_rank1']=True
 # Cost on disposable restored models. No scientific checkpoint mutation.
 timings={}
 for arm in ['addressable','rank1']:
  if arm=='addressable':mm,dd,oo,rr,_=A.restore(O/'main.pt',rows)
  else:mm,dd,oo,rr=T.setup()
  ts=[]
  for i in range(7):
   t=time.perf_counter();T.update(mm,dd,oo,rr,rows,'A');dt=time.perf_counter()-t
   if i>=2:ts.append(dt)
  timings[arm]=dict(update_ms=statistics.mean(ts)*1000,targets_per_second=8/statistics.mean(ts),steps=5,warmup=2,scope='answer targets only; 16 additional auxiliary labels/update; full loss extraction and logging')
 report['timing']=timings;R.dump('analysis.json',report)
 # One architecture seed only. Confirm only if normal BOTH and corrected joint both >=90%.
 gate=report['layout']['normal_both_accuracy']>=.9 and report['corrections']['correct']['post']['joint_accuracy']>=.9 and report['current']['original_joint_accuracy']>=.9
 R.dump('confirmation-gate.json',dict(passed=gate,reason='all: layout normal both >=.9, corrected binding joint >=.9, current-value normal paired >=.9',additional_seeds_executed=False))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
