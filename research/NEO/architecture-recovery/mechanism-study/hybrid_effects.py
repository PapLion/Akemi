"""Inference-only read suppression: functional use is not a trained memory ablation."""
import sys,json,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybrid import build_hybrid
from experiment import batch
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
@torch.no_grad()
def main():
 rows=[json.loads(s) for s in (R.parent/'results/panel.jsonl').read_text().splitlines()];rows=[r for r in rows if r['split']=='dev'];summ=[];details=[]
 for p in sorted((R/'results/hybrid').glob('*.pt')):
  arm,seed=p.stem.rsplit('-',1);seed=int(seed);m=build_hybrid(arm,seed);m.load_state_dict(torch.load(p,weights_only=True)['model'],strict=True);m.eval();original=m.memory_head._read;observed=[]
  for start in range(0,len(rows),16):
   rr=rows[start:start+16];x,y=batch(rr);states=[]
   def record(xx,mem):states.append(float(mem.norm(dim=(-2,-1)).mean()));return original(xx,mem)
   m.memory_head._read=record;a=m(x)[:,-1];m.memory_head._read=lambda xx,mem:(xx,torch.zeros_like(xx[...,:1]));b=m(x)[:,-1];m.memory_head._read=original
   for j,r in enumerate(rr):
    q={'arm':arm,'seed':seed,'id':r['id'],'task':r['task'],'correct':bool(a[j].argmax()==y[j]),'read_suppressed_correct':bool(b[j].argmax()==y[j]),'prediction_changed':bool(a[j].argmax()!=b[j].argmax()),'max_logit_delta':float((a[j]-b[j]).abs().max())};observed.append(q);details.append(q)
  summ.append({'arm':arm,'seed':seed,'dev_accuracy':sum(r['correct'] for r in observed)/len(observed),'read_suppressed_accuracy':sum(r['read_suppressed_correct'] for r in observed)/len(observed),'prediction_change_rate':sum(r['prediction_changed'] for r in observed)/len(observed),'mean_max_logit_delta':sum(r['max_logit_delta'] for r in observed)/len(observed)})
 (R/'results/hybrid-effects.json').write_text(json.dumps(summ,indent=2));(R/'results/hybrid-effects-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in details))
if __name__=='__main__':main()
