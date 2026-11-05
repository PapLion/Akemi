"""Validate completed trajectories without recomputing training."""
import sys,json,hashlib,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gradient_audit import factory
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
expected={'ablations':['transformer','no_ice','no_filter','depth1','event','delta','detach','chunk2'],'capacity':['capacity_transformer'],'matched':['event_matched','delta_matched'],'hybrid':['event_fast','delta_fast']}
report=[]
for folder,arms in expected.items():
 for seed in [17,29,43]:
  order=(R/'results'/folder/f'order-{seed}.json').read_bytes();oh=hashlib.sha256(order).hexdigest();assert order==(R/'results/ablations'/f'order-{seed}.json').read_bytes();assert order==(R.parents[1]/'cryo-next-generation/results/learning-1000'/f'order-{seed}.json').read_bytes()
  for arm in arms:
   p=R/'results'/folder/f'{arm}-{seed}.json';r=json.loads(p.read_text());assert r['seed']==seed and r['arm']==arm and r['targets_consumed']==8000 and r['order_sha256']==oh;assert len(r['updates'])==1000
   preds=[json.loads(s) for s in p.with_name(p.stem+'-predictions.jsonl').read_text().splitlines()];assert len(preds)==672;assert sum(x['stage']=='dev' for x in preds)==224;assert sum(x['stage']=='train' for x in preds)==448
   dev=[x for x in preds if x['stage']=='dev'];assert sum(x['correct'] for x in dev)/len(dev)==r['dev_accuracy']
   state=torch.load(p.with_suffix('.pt'),weights_only=True,map_location='cpu');m=factory(arm,seed);m.load_state_dict(state['model'],strict=True);assert state['update']==1000 and state['cursor']==8000 and state['accumulation']=={'steps':1,'pending':False};assert len(state['optimizer']['state'])==sum(p.requires_grad for p in m.parameters());assert all(int(s['step'])==1000 for s in state['optimizer']['state'].values())
   assert all(torch.isfinite(p).all() for p in m.parameters());report.append({'folder':folder,'arm':arm,'seed':seed,'status':'PASS','optimizer_tensors':len(state['optimizer']['state'])})
(R/'results/result-validation.json').write_text(json.dumps(report,indent=2));print(len(report),'trajectories verified')
