"""Conditional linear/MLP decoders; only auxiliary parameters are optimized."""
import json,time
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
R=Path(__file__).resolve().parent
TASKS={'presence':2,'value':4,'old':4,'corrected':2}
class Decoder(nn.Module):
 def __init__(self,d,c,mlp=False):
  super().__init__();h=32 if mlp else c;self.w=nn.Parameter(torch.randn(5,d,h)*.02);self.b=nn.Parameter(torch.zeros(5,h));self.out=nn.Parameter(torch.randn(5,h,c)*.02) if mlp else None;self.bias=nn.Parameter(torch.zeros(5,c)) if mlp else None
 def forward(self,x,e):
  y=(x[:,None]@self.w[e]).squeeze(1)+self.b[e]
  return y if self.out is None else (y.tanh()[:,None]@self.out[e]).squeeze(1)+self.bias[e]
def arrays(rr,features,task):
 use=torch.tensor([True if task in ['presence','corrected'] else bool(r['present']) for r in rr]);e=torch.tensor([r['entity_index'] for r in rr])[use]
 label={'presence':'present','value':'current','old':'old','corrected':'corrected'}[task];y=torch.tensor([r[label] for r in rr])[use]
 return features[use],e,y,use

def fit(data,rows,task,kind,permuted=False,save_path=None):
 torch.manual_seed(101);train=arrays(rows['train'],data['train'],task);mean=train[0].mean(0);sd=train[0].std(0).clamp_min(.01)
 parts={s:arrays(rows[s],data[s],task) for s in rows};parts={s:((x-mean)/sd,e,y,use) for s,(x,e,y,use) in parts.items()}
 model=Decoder(mean.numel(),TASKS[task],kind=='mlp');opt=torch.optim.AdamW(model.parameters(),lr=.02,weight_decay=.001);x,e,truth,_=parts['train'];y=truth[torch.randperm(len(truth))] if permuted else truth;curves=[]
 for step in range(201):
  out=model(x,e);loss=F.cross_entropy(out,y)
  if step%20==0:curves.append({'step':step,'loss':float(loss.detach()),'train_accuracy':float((out.argmax(-1)==y).float().mean())})
  if step==200:break
  opt.zero_grad();loss.backward();assert all(torch.isfinite(p.grad).all() for p in model.parameters());opt.step()
 result={'task':task,'decoder':kind,'permuted_train':permuted,'parameters':sum(p.numel() for p in model.parameters()),'curves':curves,'splits':{}};predictions={}
 with torch.no_grad():
  for s,(xx,ee,yy,use) in parts.items():
   pred=model(xx,ee).argmax(-1);acc=float((pred==yy).float().mean());bal=sum(float((pred[yy==k]==k).float().mean()) for k in range(TASKS[task]) if (yy==k).any())/len(yy.unique())
   result['splits'][s]={'accuracy':acc,'balanced_accuracy':bal,'n':len(yy)};predictions[s]={'prediction':pred.tolist(),'truth':yy.tolist(),'indices':use.nonzero().flatten().tolist()}
 if save_path is not None:torch.save({'model':model.state_dict(),'mean':mean,'sd':sd,'task':task,'kind':kind,'input_dim':mean.numel(),'classes':TASKS[task],'seed':101,'updates':200},save_path)
 return result,predictions

def features(f,rr,which):
 if which=='memory':return f['states'][:,6]
 if which=='read':return f['read']
 if which=='local':return f['local']
 idx=torch.tensor([r['positions'][2]//2 for r in rr]);n=torch.arange(len(rr))
 if which=='pooled_write':return f['pooled'][n,idx]
 if which=='post_write':return f['states'][n,idx]
 if which=='after_first':return f['states'][n,torch.tensor([r['positions'][0]//2 for r in rr])]
 raise ValueError(which)
def main():
 torch.set_num_threads(1);rows={s:[json.loads(l) for l in (R/'data'/f'{s}.jsonl').read_text().splitlines()] for s in ['train','dev','structural']};outdir=R/'results/probes';outdir.mkdir(exist_ok=True);start=time.time()
 jobs=[]
 for cp in sorted((R/'results').glob('*-trained.pt'))+sorted((R/'results').glob('*-initial.pt')):
  jobs.append((cp,'memory',list(TASKS)))
  if '-17-normal-trained' in cp.stem:
   for source,ts in [('read',['value']),('local',['value']),('pooled_write',['value']),('post_write',['value']),('write_value',['value']),('after_first',['old'])]:jobs.append((cp,source,ts))
 for cp,source,tasks in jobs:
  dst=outdir/(cp.stem+'-'+source+'.json')
  if dst.exists():continue
  raw=torch.load(cp,weights_only=True)
  if source=='write_value':
   import extract
   m,_=extract.load_model(raw['arm'],raw['seed']);data={}
   for ss in rows:
    ff=raw['features'][ss];idx=torch.tensor([r['positions'][2]//2 for r in rows[ss]]);z=ff['pooled'][torch.arange(len(idx)),idx]
    with torch.no_grad():
     if raw['arm']=='intact':data[ss]=ff['candidate'][torch.arange(len(idx)),idx]
     else:
      head=m.core.memory_head;projection=head.candidate if raw['arm']=='event_fast' else head.value
      data[ss]=projection(z.reshape(-1,head.cfg.width)).tanh().reshape(len(idx),-1)
  else:data={s:features(raw['features'][s],rows[s],source) for s in rows}
  results=[];preds=[]
  for task in tasks:
   for kind in ['linear','mlp']:
    result,p=fit(data,rows,task,kind);results.append(result);preds.append({'task':task,'decoder':kind,'predictions':p})
   if task=='value':
    result,p=fit(data,rows,task,'linear',True);results.append(result);preds.append({'task':task,'decoder':'permuted-linear','predictions':p})
  dst.write_text(json.dumps({'checkpoint_features':cp.name,'feature':source,'results':results},indent=2)+'\n');(outdir/(dst.stem+'-predictions.json')).write_text(json.dumps(preds)+'\n');print(dst.name,round(time.time()-start,1),flush=True)
 # Explicit code and presence controls do not impersonate trained model states.
 for control in ['explicit','presence_only']:
  data={}
  for s,rr in rows.items():
   p=torch.tensor([r['present'] for r in rr]);v=torch.tensor([r['current'] for r in rr]);o=torch.tensor([r['old'] for r in rr]);c=torch.tensor([r['corrected'] for r in rr]);data[s]=torch.cat([p[:,None],F.one_hot(v,4)*p[:,None],F.one_hot(o,4)*p[:,None],c[:,None]],1).float() if control=='explicit' else p[:,None].float()
  results=[]
  for task in TASKS:
   r,p=fit(data,rows,task,'linear');results.append(r)
  (outdir/(control+'.json')).write_text(json.dumps({'control':control,'results':results},indent=2)+'\n')
 print('COMPLETE',time.time()-start)
if __name__=='__main__':main()
