"""Bounded, resumable CPU engineering/symbolic learning only."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse,random,json,time,hashlib,resource,copy
from pathlib import Path
import torch
import torch.nn.functional as F
import panel,network
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def batch(rows):return torch.tensor([r['ids'] for r in rows]),torch.tensor([r['label'] for r in rows])
def save(path,state):
 tmp=path.with_suffix('.tmp');torch.save(state,tmp);tmp.replace(path)
@torch.no_grad()
@torch.random.fork_rng(devices=[])
def evaluate(m,rows):
 m.eval();out=[]
 for i in range(0,len(rows),32):
  rr=rows[i:i+32];x,y=batch(rr);logits=m(x)[:,-1];loss=F.cross_entropy(logits,y,reduction='none');pred=logits.argmax(-1)
  for j,r in enumerate(rr):out.append({'id':r['id'],'task':r['task'],'split':r['split'],'entity':r['entity'],'answer':r['answer'],'label':r['label'],'prediction':int(pred[j]),'correct':bool(pred[j]==y[j]),'nll':float(loss[j]),'outside_window':r['outside_window']})
 m.train();return out
def metrics(pred):
 return {'n':len(pred),'accuracy':sum(r['correct'] for r in pred)/len(pred),'nll':sum(r['nll'] for r in pred)/len(pred),'by_task':{t:sum(r['correct'] for r in pred if r['task']==t)/sum(r['task']==t for r in pred) for t in sorted({r['task'] for r in pred})},'outside_accuracy':sum(r['correct'] for r in pred if r['outside_window'])/max(1,sum(r['outside_window'] for r in pred)),'recent_accuracy':sum(r['correct'] for r in pred if not r['outside_window'])/max(1,sum(not r['outside_window'] for r in pred))}
def micro_panel(rows):
 out=[];counts={k:0 for k in range(5)};suffix=set()
 for i,task in enumerate(panel.TASKS+['retain','replace']):
  label=i%5
  r=next(r for r in rows if r['task']==task and r['answer']==label and tuple(r['ids'][-8:]) not in suffix)
  out.append(r);counts[label]+=1;suffix.add(tuple(r['ids'][-8:]))
 assert set(counts.values())=={2};return out

def train(arm,seed,stage,steps,window=8,mode='normal',rows=None):
 folder=R/'results'/stage;folder.mkdir(exist_ok=True);key=f'{arm}-{mode}-w{window}-{seed}';dest=folder/(key+'.json');cp=folder/(key+'.pt')
 if dest.exists() and json.loads(dest.read_text())['step']>=steps:return
 trainrows=panel.load('train') if rows is None else rows;datahash=hashlib.sha256(json.dumps(trainrows,sort_keys=True).encode()).hexdigest();m=network.build(arm,seed,window,mode);opt=network.optimizer(m);rng=random.Random(seed+5000);logs=[];cuts=[];start=0
 if cp.exists():
  s=torch.load(cp,weights_only=True,map_location='cpu');assert s['dataset_sha256']==datahash and s['config']==m.config();m.load_state_dict(s['model'],strict=True);opt.load_state_dict(s['optimizer']);rng.setstate(s['sampler_rng']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng']);logs=s['updates'];cuts=s['cuts'];start=s['step']
 else:cuts=[{'step':0,'metrics':metrics(evaluate(m,trainrows if stage.startswith('micro') else panel.load('iid')))}]
 coverage=[id(p) for g in opt.param_groups for p in g['params']];assert len(coverage)==len(set(coverage))==sum(p.requires_grad for p in m.parameters())
 order=[];gradlog=[]
 for step in range(start,steps):
  ix=list(range(len(trainrows))) if stage.startswith('micro') else rng.sample(range(len(trainrows)),8);order.append(ix);x,y=batch([trainrows[k] for k in ix]);t=time.perf_counter();opt.zero_grad(set_to_none=True);logits=m(x)[:,-1];loss=F.cross_entropy(logits,y);assert torch.isfinite(loss);loss.backward();norm=torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True)
  if step==start or step==steps-1:
   gradlog.append({'step':step+1,'tensors':[{'name':n,'norm':float(p.grad.norm()) if p.grad is not None else None,'finite':bool(torch.isfinite(p.grad).all()) if p.grad is not None else False} for n,p in m.named_parameters() if p.requires_grad]})
  opt.step();logs.append({'step':step+1,'loss':float(loss.detach()),'gradient_norm':float(norm),'batch_accuracy':float((logits.argmax(-1)==y).float().mean()),'seconds':time.perf_counter()-t,'targets':len(ix),'indices':ix})
  if (step+1)%100==0 or step+1==steps:
   cuts.append({'step':step+1,'metrics':metrics(evaluate(m,trainrows if stage.startswith('micro') else panel.load('iid')))})
   state={'model':m.state_dict(),'optimizer':opt.state_dict(),'config':m.config(),'step':step+1,'cursor':sum(x['targets'] for x in logs),'sampler_rng':rng.getstate(),'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'updates':logs,'cuts':cuts,'dataset_sha256':datahash,'scheduler':None,'accumulation':{'steps':1,'pending':False},'microstep':0,'tokenizer':'atomic ASCII fixtures / 8192 output IDs; no tokenizer training'};save(cp,state)
  if step+1 in [100,300,1000]:print(stage,arm,seed,step+1,cuts[-1]['metrics']['accuracy'],flush=True)
 datasets={'micro':trainrows} if stage.startswith('micro') else {s:panel.load(s) for s in ['train','iid','compositional','structural','both']};preds=[];met={}
 for split,rr in datasets.items():
  pp=evaluate(m,rr);preds.extend(pp);met[split]=metrics(pp)
 (folder/(key+'-predictions.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in preds));result={'arm':arm,'seed':seed,'mode':mode,'window':window,'step':steps,'metrics':met,'cuts':cuts,'updates':logs,'gradients':gradlog,'training_seconds':sum(r['seconds'] for r in logs),'parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'peak_rss_cumulative':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'dataset_sha256':datahash};dest.write_text(json.dumps(result,indent=2))
 print('FINAL',stage,key,{k:round(v['accuracy'],4) for k,v in met.items()},flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['micro','micro-v2','micro-v3','pilot','extend','ablate']);p.add_argument('--max-seconds',type=int,default=1800);a=p.parse_args();start=time.monotonic()
 if a.stage in ['micro','micro-v2','micro-v3']:cases=[(arm,17,16,'normal') for arm in network.ARMS]+[('transformer',17,0,'normal')];steps=200;rows=micro_panel(panel.load('train'));(R/f'results/{a.stage}-panel.json').write_text(json.dumps(rows,indent=2))
 elif a.stage=='pilot':cases=[(arm,17,16,'normal') for arm in network.ARMS]+[('transformer',17,0,'normal')];steps=300;rows=None
 elif a.stage=='extend':
  pilot=list((R/'results/pilot').glob('*.json'));assert any(json.loads(p.read_text())['metrics']['iid']['accuracy']>.35 for p in pilot if not p.name.endswith('predictions.jsonl')),'Pilot gate failed'
  assert any(json.loads(p.read_text())['metrics']['micro']['accuracy']>=.8 for p in (R/'results/micro-v3').glob('*.json')),'Microfit gate failed'
  cases=[(arm,seed,16,'normal') for seed in [17,29,43] for arm in network.ARMS]+[('transformer',seed,0,'normal') for seed in [17,29,43]];steps=1000;rows=None
 else:raise RuntimeError('Ablations require explicit pilot-based preregistered selection; use train API after recording gate')
 for arm,seed,win,mode in cases:
  if time.monotonic()-start>a.max_seconds:print('BOUND reached; next',arm,seed,flush=True);return
  # Extend seed17 from its completed pilot, preserving trajectory and sampler state.
  if a.stage=='extend' and seed==17:
   folder=R/'results/extend';folder.mkdir(exist_ok=True);name=f'{arm}-{mode}-w{win}-{seed}.pt';source=R/'results/pilot'/name
   if not (folder/name).exists():import shutil;shutil.copyfile(source,folder/name)
  train(arm,seed,a.stage,steps,win,mode,rows)
if __name__=='__main__':main()
