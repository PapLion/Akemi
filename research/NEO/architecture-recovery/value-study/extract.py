"""Observe actual frozen forwards; temporary method wrappers only record tensors."""
import sys,json,hashlib,types,time
from pathlib import Path
import torch
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'selective-memory'))
import network
SOURCE=R.parent.parent/'cryo-selective-memory-study/selective-memory/results'
def load_model(arm,seed,mode='normal',trained=True):
 cp=SOURCE/('extend' if mode=='normal' else 'ablations')/f'{arm}-{mode}-w16-{seed}.pt'
 s=torch.load(cp,map_location='cpu',weights_only=True);c=s['config'];m=network.build(arm,seed,c['window'],c['mode'],random_budget=c.get('random_budget',.5))
 if trained:m.load_state_dict(s['model'],strict=True)
 assert m.config()==c, (m.config(),c)
 m.eval();m.requires_grad_(False)
 return m,cp
@torch.no_grad()
def observe(m,ids):
 pooled=[];reads=[];raw=[];projections=[];handles=[];old=None
 if m.arm.endswith('_fast'):
  h=m.core.memory_head;old=(h._summarize,h._read)
  def summ(*args,**kw):
   z=old[0](*args,**kw);pooled.append(z.detach().clone());return z
  def read(*args,**kw):
   y,g=old[1](*args,**kw);reads.append(args[1].detach().clone());raw.append(y.detach().clone());return y,g
  h._summarize=summ;h._read=read
 handles.append(m.core.read.register_forward_hook(lambda mod,args,out:projections.append(out.detach().clone())))
 try:logits,tr=m(ids,trace=True)
 finally:
  for hook in handles:hook.remove()
  if old is not None:h._summarize,h._read=old
 if m.arm=='intact':
  states=torch.stack([tr[i]['slow'] for i in range(7,64,8)],1);gates=torch.stack([torch.stack([tr[t]['gate'] for t in range(i-7,i+1)],1).mean(1) for i in range(7,64,8)],1)
  z=torch.stack([tr[i]['fast'] for i in range(7,64,8)],1);read_feature=m.core.read(tr[63]['previous']);candidate=torch.stack([tr[i]['candidate'] for i in range(7,64,8)],1)
 else:
  states=torch.stack([t['memory'].flatten(1) for t in tr],1);gates=torch.stack([t['write'].flatten(1) for t in tr],1);z=torch.stack([a[:,0].flatten(1) for a in pooled],1);candidate=z
  read_feature=projections[-1][:,-1]
 hidden=m.core.hidden(ids)
 return {'states':states.detach(),'gates':gates.detach(),'pooled':z.detach(),'candidate':candidate.detach(),'read':read_feature.detach(),'local':hidden[:,-1].detach(),'logits5':logits[:,-1,48:53].detach(),'prediction':logits[:,-1].argmax(-1).detach()}
def main():
 torch.set_num_threads(1);start=time.time();rows={s:[json.loads(x) for x in (R/'data'/f'{s}.jsonl').read_text().splitlines()] for s in ['train','dev','structural']};manifest=[]
 configs=[(a,s,'normal',t) for a in ['intact','event_fast','delta_fast'] for s in [17,29,43] for t in [True,False]]+ [('delta_fast',s,mode,True) for s in [17,29,43] for mode in ['always','random']]
 for arm,seed,mode,trained in configs:
  key=f'{arm}-{seed}-{mode}-'+('trained' if trained else 'initial');dst=R/'results'/f'{key}.pt'
  if dst.exists():continue
  m,cp=load_model(arm,seed,mode,trained);data={};torch.manual_seed(991)
  for split,rr in rows.items():
   chunks=[]
   for i in range(0,len(rr),32):chunks.append(observe(m,torch.tensor([r['ids'] for r in rr[i:i+32]])))
   data[split]={k:torch.cat([c[k] for c in chunks]) for k in chunks[0]}
  torch.save({'features':data,'arm':arm,'seed':seed,'mode':mode,'trained':trained,'checkpoint':str(cp),'checkpoint_sha256':hashlib.sha256(cp.read_bytes()).hexdigest()},dst)
  manifest.append({'key':key,'seconds_elapsed':time.time()-start,'checkpoint':str(cp)});print(key,round(time.time()-start,1),flush=True)
 if manifest:(R/'results/extraction-run.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
