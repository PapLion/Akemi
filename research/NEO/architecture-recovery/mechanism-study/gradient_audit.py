"""Parameter-wise gradients at actual task length; no optimization."""
import sys,json,torch,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import batch
from variants import build
from matched_head import build_matched
from capacity_control import build_control
from hybrid import build_hybrid
def factory(arm,seed):
 return build_hybrid(arm,seed) if arm.endswith('_fast') else (build_control(seed) if arm=='capacity_transformer' else (build_matched(arm,seed) if arm.endswith('_matched') else build(arm,seed)))
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def main():
 rows=[json.loads(s) for s in (R.parent/'results/panel.jsonl').read_text().splitlines()];tr=[r for r in rows if r['split']=='train'];out=[]
 for p in sorted(p for folder in ['ablations','capacity','matched','hybrid'] for p in (R/'results'/folder).glob('*.pt')):
  arm,seed=p.stem.rsplit('-',1);seed=int(seed);initial=factory(arm,seed);trained=factory(arm,seed);trained.load_state_dict(torch.load(p,weights_only=True)['model'],strict=True);rng=random.Random(seed+5000);x,y=batch([tr[k] for k in rng.sample(range(len(tr)),8)])
  for stage,m in [('initial',initial),('trained',trained)]:
   loss=torch.nn.functional.cross_entropy(m(x)[:,-1],y);loss.backward()
   for n,q in m.named_parameters():
    if not q.requires_grad:continue
    grad=q.grad;out.append({'arm':arm,'seed':seed,'stage':stage,'parameter':n,'grad_present':grad is not None,'grad_finite':bool(torch.isfinite(grad).all()) if grad is not None else False,'grad_norm':float(grad.norm()) if grad is not None else None,'grad_nonzero_elements':int((grad!=0).sum()) if grad is not None else 0,'elements':q.numel(),'parameter_change_norm':float((q.detach()-dict(initial.named_parameters())[n].detach()).norm()) if stage=='trained' else None})
 (R/'results/parameter-gradients.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
