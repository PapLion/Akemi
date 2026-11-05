"""One fixed, all-arm extension from engineering-learning checkpoints. CPU only."""
from pathlib import Path
import time,json,hashlib,random,statistics
import torch
import torch.nn.functional as F
from experiment import make_model,optimizer,batch,evaluate,checkpoint,ARMS
from tasks import TASKS
R=Path(__file__).resolve().parent
torch.set_num_threads(1)
def main():
 dest=R/'results/learning-1000';dest.mkdir(exist_ok=True);start=time.monotonic();panel=[json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines()];train=[r for r in panel if r['split']=='train'];dev=[r for r in panel if r['split']=='dev'];dataset=hashlib.sha256((R/'results/panel.jsonl').read_bytes()).hexdigest()
 config={'seeds':[17,29,43],'arms':ARMS,'start_update':100,'end_update':1000,'new_targets':7200,'total_targets':8000,'unique_train_records':448,'lr':.003,'batch':8,'width':32,'chunk':8,'layers':1,'max_wall_seconds':1800,'source':'EXTENSION_PROTOCOL.md','status':'exploratory; all arms last checkpoint, no selection'}
 (R/'results/extension-config.json').write_text(json.dumps(config,indent=2))
 for seed in config['seeds']:
  rng=random.Random(seed+5000);order=[rng.sample(range(len(train)),8) for _ in range(1000)];prior=json.loads((R/f'results/learning/order-{seed}.json').read_text());assert order[:100]==prior
  orderhash=hashlib.sha256(json.dumps(order).encode()).hexdigest();(dest/f'order-{seed}.json').write_text(json.dumps(order))
  for arm in ARMS:
   output=dest/f'{arm}-{seed}.json'
   if output.exists():continue
   if time.monotonic()-start>1800:
    (dest/'TIME_LIMIT.json').write_text(json.dumps({'next_arm':arm,'seed':seed,'elapsed_s':time.monotonic()-start}));return
   state=torch.load(R/f'results/learning/{arm}-{seed}.pt',weights_only=True,map_location='cpu');assert state['update']==100 and state['cursor']==800 and state['dataset_sha256']==dataset
   m=make_model(arm,seed);m.load_state_dict(state['model'],strict=True);op=optimizer(m);op.load_state_dict(state['optimizer']);torch.set_rng_state(state['rng']);random.setstate(state['python_rng'])
   old=json.loads((R/f'results/learning/{arm}-{seed}.json').read_text());oldpred=[json.loads(s) for s in (R/f'results/learning/{arm}-{seed}-predictions.jsonl').read_text().splitlines()];initial=[r for r in oldpred if r['stage']=='initial'];logs=[];t0=time.monotonic();m.train()
   for step in range(100,1000):
    x,y=batch([train[k] for k in order[step]]);ts=time.monotonic();op.zero_grad(set_to_none=True)
    from experiment import forward_answer
    logits,out=forward_answer(m,x);loss=F.cross_entropy(logits,y);assert torch.isfinite(loss);loss.backward();gn=torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);op.step()
    logs.append({'update':step+1,'loss':float(loss.detach()),'gradient_norm':float(gn),'update_s':time.monotonic()-ts,'targets':8,'input_ids':512})
    if (step+1)%100==0:print(arm,seed,'update',step+1,'loss',float(loss.detach()),flush=True)
   new_s=time.monotonic()-t0;final,gates=evaluate(m,dev,arm,seed,'final');trained,_=evaluate(m,train,arm,seed,'train_final')
   (dest/f'{arm}-{seed}-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in initial+final+trained));(dest/f'{arm}-{seed}-gates.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in gates))
   metrics={stage:{task:{'n':len(rr:=[r for r in records if r['task']==task]),'accuracy':sum(r['correct'] for r in rr)/len(rr),'candidate_accuracy':sum(r['candidate_correct'] for r in rr)/len(rr),'nll':statistics.mean(r['nll'] for r in rr)} for task in TASKS} for stage,records in [('initial',initial),('final',final),('train_final',trained)]}
   result={'arm':arm,'seed':seed,'order_sha256':orderhash,'prefix_order_verified':True,'resume_from_update':100,'train_s':old['train_s']+new_s,'extension_train_s':new_s,'targets':8000,'new_targets':7200,'input_ids':512000,'parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'metrics':metrics,'updates':old['updates']+logs}
   output.write_text(json.dumps(result,indent=2));torch.save(checkpoint(m,op,1000,8000,{'order_sha256':orderhash,'seed':seed,'prefix100_verified':True}),dest/f'{arm}-{seed}.pt')
   print('DONE',arm,seed,'accuracy',statistics.mean(x['accuracy'] for x in metrics['final'].values()),'extension_s',round(new_s,2),flush=True)
if __name__=='__main__':main()
