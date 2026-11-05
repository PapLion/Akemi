"""Diagnostic backward only: no updates, no modification of stored weights."""
import json,statistics
from pathlib import Path
import torch
import torch.nn.functional as F
import panel,network,learn
from vendor.cryo_historical import CryoTiny
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def probe(m,rows):
 x,y=learn.batch(rows);m.eval();m.zero_grad(set_to_none=True)
 if m.arm=='intact':
  out,tr=CryoTiny.forward(m.core,x,return_trace=True);states=[r['slow'] for r in tr]
  for t in states:t.retain_grad()
 else:out,tr=m(x,trace=True);states=[r['memory'] for r in tr]
 loss=F.cross_entropy(out[:,-1],y);loss.backward();top=out[:,-1].detach().softmax(-1).topk(5,-1)
 gg=torch.cat([(r['gate'] if m.arm=='intact' else r['write']).detach().flatten() for r in (tr if m.arm=='intact' else tr[:-1])])
 return {'loss':float(loss.detach()),'top5_ids':top.indices.tolist(),'top5_probabilities':top.values.tolist(),'gate_summary':{'mean':float(gg.mean()),'sd':float(gg.std()),'fraction_low':float((gg<.05).float().mean()),'fraction_high':float((gg>.95).float().mean())},'state_gradients':[{'index':i,'norm':float(t.grad.norm()) if t.grad is not None else None,'state_norm':float(t.detach().norm())} for i,t in enumerate(states)],'parameters':[{'name':n,'norm':float(p.grad.norm()) if p.grad is not None else None,'finite':bool(torch.isfinite(p.grad).all()) if p.grad is not None else False} for n,p in m.named_parameters() if p.requires_grad]}
def main():
 rr=panel.load('iid')+panel.load('structural');chosen=[]
 for task in ['replace','multiple','discard','goal']:
  group=[]
  for r in rr:
   old=next((int(v) for op,e,v in r['ops'] if op in '=!' and e==r['entity']),4)
   if r['task']==task and r['outside_window'] and old!=r['answer']:group.append(r)
  chosen+=sorted(group,key=lambda r:r['id'])[:2]
 assert len(chosen)==8;results=[]
 for cp in sorted((R/'results/extend').glob('*.pt')):
  s=torch.load(cp,weights_only=True,map_location='cpu');c=s['config']
  if c['arm'] not in ['intact','event_fast','delta_fast']:continue
  seed=int(cp.stem.rsplit('-',1)[1]);m=network.build(c['arm'],seed,c['window'],c['mode']);initial=probe(m,chosen);m.load_state_dict(s['model'],strict=True);trained=probe(m,chosen)
  assert all(p['finite'] for p in trained['parameters'])
  results.append({'checkpoint':cp.name,'initial':initial,'trained':trained})
 (R/'results/gradient-horizons.json').write_text(json.dumps({'ids':[r['id'] for r in chosen],'diagnostic_only':True,'results':results},indent=2));print('PASS finite diagnostic gradients',len(results))
if __name__=='__main__':main()
