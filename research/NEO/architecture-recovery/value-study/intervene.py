"""Matched-state causal interventions using actual donor trajectories."""
import json,copy,time
from pathlib import Path
import torch
import torch.nn.functional as F
import extract,data_panel
from vendor.cryo_historical import segments
R=Path(__file__).resolve().parent
@torch.no_grad()
def historical(m,ids,donor=None,at=56):
 c=m.core;x=c.hidden(ids);b,t,d=x.shape;slow=c.memory_init.expand(b,-1);outs=[]
 for i in range(t):
  if i==at and donor is not None:slow=donor
  fast=x[:,i]
  for _ in range(2):fast=c.fast_norm(fast+torch.tanh(c.fast(torch.cat([fast,x[:,i],c.read(slow)],-1))))
  z=torch.cat([slow,fast],-1);g=c.gate(z).sigmoid();candidate=torch.tanh(c.slow(z));slow=(1-g)*slow+g*candidate;outs.append(c.slow_norm(fast+c.read(slow)))
 return F.linear(torch.stack(outs,1),c.emb.weight)
@torch.no_grad()
def injected(m,ids,donor):
 if m.arm=='intact':return historical(m,ids,donor)
 head=m.core.memory_head;old=head._read;count=[0]
 def read(x,memory):
  j=count[0];count[0]+=1
  if j==7:memory=donor.reshape_as(memory)
  return old(x,memory)
 head._read=read
 try:return m(ids)
 finally:head._read=old

def main():
 torch.set_num_threads(1);rr=[r for r in data_panel.generate('dev') if r['present'] and r['regime'] in [1,2] and r['old']!=r['current']];x=torch.tensor([r['ids'] for r in rr]);records=[]
 for arm in ['intact','event_fast','delta_fast']:
  for seed in [17,29,43]:
   m,_=extract.load_model(arm,seed);original=extract.observe(m,x)
   if arm=='intact':assert torch.equal(m(x),historical(m,x))
   sham=injected(m,x,original['states'][:,6]);base=m(x);assert torch.equal(sham,base),(arm,'sham')
   for kind in ['valid','obsolete']:
    changed=[]
    for r in rr:
     ops=copy.deepcopy(r['ops']);i=r['positions'][2] if kind=='valid' else r['positions'][0];ops[i][2]=str((int(ops[i][2])+1)%4);changed.append(data_panel.panel.make_record(ops,r['query'],r['task'],'diagnostic'))
    xx=torch.tensor([r['ids'] for r in changed]);assert torch.equal(x[:,-16:],xx[:,-16:]);donor=extract.observe(m,xx);y=injected(m,x,donor['states'][:,6]);pred=y[:,-1].argmax(-1);distance=(original['states'][:,6]-donor['states'][:,6]).norm(dim=-1)
    norm=original['states'][:,6].norm(dim=-1).clamp_min(1e-8)
    for i,r in enumerate(rr):records.append({'arm':arm,'seed':seed,'kind':kind,'id':r['id'],'entity':r['entity'],'base_answer':r['answer'],'donor_answer':changed[i]['answer'],'prediction':int(original['prediction'][i])-48,'donor_prediction':int(donor['prediction'][i])-48,'injected_prediction':int(pred[i])-48,'state_l2':float(distance[i]),'relative_l2':float(distance[i]/norm[i]),'logits5_l2':float((y[i,-1,48:53]-base[i,-1,48:53]).norm()),'sham_exact':True})
   print(arm,seed,flush=True)
 (R/'results/interventions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
if __name__=='__main__':main()
