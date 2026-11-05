"""State/gradient observations, not causal attribution of a learned algorithm."""
import sys,json,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import make_model,batch
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'cryo-next-generation/results';torch.set_num_threads(1)
def main():
 rows=[json.loads(s) for s in (OLD/'panel.jsonl').read_text().splitlines()];dev=[r for r in rows if r['split']=='dev'];selected=[next(r for r in dev if r['task']==t) for t in sorted({r['task'] for r in dev})];x,y=batch(selected);out=[]
 for seed in [17,29,43]:
  for stage in ['initial','trained']:
   m=make_model('cryo_history',seed)
   if stage=='trained':m.load_state_dict(torch.load(OLD/f'learning-1000/cryo_history-{seed}.pt',weights_only=True)['model'],strict=True)
   captured=[];orig=m.hidden
   def hidden(*args):
    h=orig(*args);captured.append(h);return h
   m.hidden=hidden;logits,trace=m(x,return_trace=True);loss=torch.nn.functional.cross_entropy(logits[:,-1],y);grads=torch.autograd.grad(loss,[captured[0]]+[t['slow'] for t in trace],allow_unused=True)
   gates=torch.stack([t['gate'] for t in trace],1);slow=torch.stack([t['slow'] for t in trace],1)
   out.append({'seed':seed,'stage':stage,'ids':[r['id'] for r in selected],'nll':float(loss.detach()),'gate_mean':float(gates.detach().mean()),'gate_fraction_below_01':float((gates<.1).float().mean()),'gate_fraction_above_09':float((gates>.9).float().mean()),'slow_norm_by_position':slow.detach().norm(dim=-1).mean(0).tolist(),'hidden_grad_norm_by_position':grads[0].norm(dim=-1).mean(0).tolist(),'slow_grad_norm_by_position':[float(g.norm(dim=-1).mean()) if g is not None else 0 for g in grads[1:]],'gate_mean_by_record':gates.detach().reshape(len(selected),8,8,-1).mean((0,2,3)).tolist()})
 (R/'results/state-diagnostics.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
