import sys,json,random,hashlib
from pathlib import Path
import torch
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'value-study'))
import extract,data_panel
import value_probes as probes
torch.set_num_threads(1)
def setup():
 m,_=extract.load_model('delta_fast',17);m.requires_grad_(True)
 # Preserve deliberate freezes from the historical optimizer.
 import network
 ref=network.build('delta_fast',17,16)
 for (n,p),(nn,q) in zip(m.named_parameters(),ref.named_parameters()):p.requires_grad_(q.requires_grad)
 torch.manual_seed(101);d=probes.Decoder(256,4);return m,d

def loss(m,d,rr):
 x=torch.tensor([r['ids'] for r in rr]);out,tr=m(x,trace=True);states=[];entities=[];labels=[]
 for b,r in enumerate(rr):
  for j,t in enumerate(tr):
   ops=r['ops'][j*2:min(j*2+2,15)]
   for e in sorted({e for op,e,v in ops if op in '=!'}):
    val=data_panel.panel.oracle(r['ops'][:min(j*2+2,15)],e)
    if val!=4:states.append(t['memory'][b].flatten());entities.append('ABCDE'.index(e));labels.append(val)
 a=d(torch.stack(states),torch.tensor(entities));aux=F.cross_entropy(a,torch.tensor(labels));lm=F.cross_entropy(out[:,-1],torch.tensor([r['label'] for r in rr]));return lm,aux,float((a.argmax(-1)==torch.tensor(labels)).float().mean())
def train(name,rr,steps,lam):
 m,d=setup();o=torch.optim.AdamW([p for p in list(m.parameters())+list(d.parameters()) if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False);rng=random.Random(17);logs=[]
 for step in range(steps):
  batch=[rr[rng.randrange(len(rr))] for _ in range(8)];o.zero_grad();lm,aux,acc=loss(m,d,batch);total=lm+lam*aux if lam else lm;total.backward();assert all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None);torch.nn.utils.clip_grad_norm_(list(m.parameters())+list(d.parameters()),1);o.step();logs.append(dict(step=step,lm=float(lm.detach()),aux=float(aux.detach()),accuracy=acc))
 torch.save(dict(model=m.state_dict(),decoder=d.state_dict(),optimizer=o.state_dict(),rng=rng.getstate(),torch_rng=torch.get_rng_state(),cursor=steps*8,step=steps,lambda_aux=lam),R/'results'/f'{name}.pt');(R/'results'/f'{name}.json').write_text(json.dumps(logs));return m,d,logs

def main():
 rr=data_panel.generate('train');micro=[]
 for e in 'ABCDE':
  for v in range(4):micro.append(next(r for r in rr if r['entity']==e and r['present'] and r['current']==v and r['regime']==1))
 m,d,logs=train('microfit',micro,150,.1)
 with torch.no_grad():lm,a,acc=loss(m,d,micro)
 gate=acc>=.9 and float(a)<.5
 (R/'results/microfit-gate.json').write_text(json.dumps(dict(pass_gate=gate,accuracy=acc,aux=float(a))))
 if not gate:return
 for name,lam in [('control',0),('treatment',.1)]:
  m,d,logs=train(name,rr,600,lam);results={}
  for split in ['train','dev','structural']:
   rows=data_panel.generate(split);pred=[];aux=[]
   with torch.no_grad():
    for i in range(0,len(rows),8):
     batch=rows[i:i+8];x=torch.tensor([r['ids'] for r in batch]);pred+=m(x)[:,-1].argmax(-1).tolist();aux.append(loss(m,d,batch)[2])
   results[split]=dict(original_accuracy=sum(p==r['label'] for p,r in zip(pred,rows))/len(rows),aux_accuracy=sum(aux)/len(aux),predictions=pred)
  (R/'results'/f'{name}-evaluation.json').write_text(json.dumps(results))
if __name__=='__main__':main()
