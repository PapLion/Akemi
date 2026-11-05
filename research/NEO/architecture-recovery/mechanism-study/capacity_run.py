"""Preregistered same-recipe ablations; resumable only between completed arms."""
import sys,json,time,random,hashlib,argparse,resource,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
import torch.nn.functional as F
from capacity_control import build_control
def build(arm,seed):return build_control(seed)
from experiment import batch,optimizer,evaluate,checkpoint
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
ARMS=['capacity_transformer']
def main(seconds):
 out=R/'results/capacity';out.mkdir(exist_ok=True);rows=[json.loads(s) for s in (R.parent/'results/panel.jsonl').read_text().splitlines()];train=[r for r in rows if r['split']=='train'];dev=[r for r in rows if r['split']=='dev'];start=time.monotonic()
 cfg={'arms':ARMS,'seeds':[17,29,43],'updates':1000,'batch':8,'width':32,'lr':.003,'betas':[.9,.95],'weight_decay':.01,'clip':1,'max_seconds_per_invocation':seconds,'panel_sha256':hashlib.sha256((R.parent/'results/panel.jsonl').read_bytes()).hexdigest(),'control':'Original intact checkpoints reproduced read-only; not retrained','torch':torch.__version__}
 (out/'config.json').write_text(json.dumps(cfg,indent=2))
 for seed in cfg['seeds']:
  rng=random.Random(seed+5000);order=[rng.sample(range(len(train)),8) for _ in range(1000)];oh=hashlib.sha256(json.dumps(order).encode()).hexdigest();(out/f'order-{seed}.json').write_text(json.dumps(order))
  for arm in ARMS:
   path=out/f'{arm}-{seed}.json'
   if path.exists():continue
   if time.monotonic()-start>seconds:
    (out/'TIME_LIMIT.json').write_text(json.dumps({'next_arm':arm,'seed':seed,'seconds':time.monotonic()-start}));return
   m=build(arm,seed);op=optimizer(m);logs=[];t0=time.monotonic()
   for step,ix in enumerate(order):
    x,y=batch([train[k] for k in ix]);ts=time.monotonic();op.zero_grad(set_to_none=True);z=m(x)[:,-1];loss=F.cross_entropy(z,y);loss.backward();gn=torch.nn.utils.clip_grad_norm_(m.parameters(),1,error_if_nonfinite=True);op.step()
    logs.append({'update':step+1,'loss':float(loss),'gradient_norm':float(gn),'update_s':time.monotonic()-ts,'batch_accuracy':float((z.argmax(-1)==y).float().mean())})
   elapsed=time.monotonic()-t0;rr,_=evaluate(m,dev,arm,seed,'dev');tr,_=evaluate(m,train,arm,seed,'train')
   (out/f'{arm}-{seed}-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rr+tr))
   result={'arm':arm,'seed':seed,'dev_accuracy':sum(r['correct'] for r in rr)/len(rr),'train_accuracy':sum(r['correct'] for r in tr)/len(tr),'dev_nll':sum(r['nll'] for r in rr)/len(rr),'per_task':{t:sum(r['correct'] for r in rr if r['task']==t)/sum(r['task']==t for r in rr) for t in sorted({r['task'] for r in rr})},'train_s':elapsed,'targets_consumed':8000,'unique_train_records':len(train),'parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'frozen':[n for n,p in m.named_parameters() if not p.requires_grad],'order_sha256':oh,'updates':logs,'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
   state=checkpoint(m,op,1000,8000,{'order_sha256':oh,'seed':seed});state['config']={'kind':arm,'width':32,'vocab':8192,'layers':1};torch.save(state,out/f'{arm}-{seed}.pt');tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2));os.replace(tmp,path)
   print(arm,seed,round(result['dev_accuracy'],4),round(result['train_accuracy'],4),round(elapsed,2),flush=True);del m,op,state
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--max-seconds',type=int,default=2400);main(p.parse_args().max_seconds)
