"""Prove post-training trace/config instrumentation preserves normal training math."""
import json,sys
from pathlib import Path
import torch
import network,network_trained_v5 as frozen,panel
R=Path(__file__).resolve().parent

def main():
 torch.set_num_threads(1);x=torch.tensor([r['ids'] for r in panel.load('train')[:2]]);out=[]
 for arm,window in [(a,16) for a in network.ARMS]+[('transformer',0)]:
  a=frozen.build(arm,17,window);b=network.build(arm,17,window);assert a.config()==b.config();oa=frozen.optimizer(a);ob=network.optimizer(b)
  for step in range(2):
   ya=a(x);yb=b(x);assert torch.equal(ya,yb),(arm,step,'logits')
   la=ya[:,-1].square().mean();lb=yb[:,-1].square().mean();la.backward();lb.backward()
   for (n,p),(nn,q) in zip(a.named_parameters(),b.named_parameters()):
    assert n==nn
    assert (p.grad is None)==(q.grad is None)
    if p.grad is not None:assert torch.equal(p.grad,q.grad),(arm,n,'grad')
   oa.step();ob.step();oa.zero_grad(set_to_none=True);ob.zero_grad(set_to_none=True)
   for n,p in a.state_dict().items():assert torch.equal(p,b.state_dict()[n]),(arm,n,'updated')
  out.append({'arm':arm,'window':window,'updates':2,'exact_logits_gradients_parameters':True})
 (R/'results/source-equivalence.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS frozen/current normal equations',len(out))
if __name__=='__main__':main()
