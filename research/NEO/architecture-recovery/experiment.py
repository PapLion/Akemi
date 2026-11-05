"""Bounded CPU synthetic learning, all arms/seeds preserved. Not pretraining."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse,dataclasses,hashlib,json,random,time,resource,copy,io,platform
from pathlib import Path
import torch
import torch.nn.functional as F
from models import Config,CryoNext,causal_loss
from tasks import load_tokenizer,build_panel,FP,TASKS
from vendor.cryo_historical import CryoTiny
R=Path(__file__).resolve().parent
torch.set_num_threads(1)
ARMS=['b0_local','b0_full','cryo_history','event','delta','event_no_memory','event_no_filter','event_always_write','event_no_persist','delta_no_persist']
def make_model(arm,seed=17,width=32,chunk=8):
 cfg=Config(vocab=8192,width=width,layers=1,chunk=chunk,slots=4,key_dim=8)
 torch.manual_seed(seed);base=CryoNext(dataclasses.replace(cfg,kind='b0'));shared={k:v.clone() for k,v in base.state_dict().items()}
 torch.manual_seed(seed+123)
 if arm=='cryo_history':
  m=CryoTiny(v=8192,d=width,layers=1,dropout=0.);m.emb.weight.data.copy_(shared['emb.weight']);return m
 kind='b0' if arm=='b0_local' else ('b0_full' if arm=='b0_full' else arm.split('_')[0])
 ablation=arm[len(kind)+1:] if arm.startswith(kind+'_') and kind in ['event','delta'] else 'none'
 m=CryoNext(dataclasses.replace(cfg,kind=kind,ablation=ablation))
 st=m.state_dict()
 for key,value in shared.items():st[key]=value
 m.load_state_dict(st,strict=True);return m

def logits_at(m,ids):
 if isinstance(m,CryoNext):return m(ids,answer_positions=torch.full((len(ids),),ids.shape[1]-1,dtype=torch.long))
 return m(ids)[:,-1]
def forward_answer(m,ids):
 out=logits_at(m,ids);return (out.logits,out) if hasattr(out,'logits') else (out,None)
def optimizer(m):return torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
def batch(rows):return torch.tensor([x['ids'] for x in rows]),torch.tensor([x['label'] for x in rows])
def checkpoint(m,opt,update,cursor,sampler):
 return {'model':m.state_dict(),'optimizer':opt.state_dict(),'config':dataclasses.asdict(m.cfg) if isinstance(m,CryoNext) else {'kind':'cryo_history','width':32,'layers':1,'vocab':8192},'rng':torch.get_rng_state(),'python_rng':random.getstate(),'update':update,'microstep':0,'cursor':cursor,'sampler':sampler,'scheduler':None,'accumulation':{'steps':1,'pending':False},'tokenizer_fingerprint':FP,'dataset_sha256':hashlib.sha256((R/'results/panel.jsonl').read_bytes()).hexdigest()}
def structural_preflight(panel):
 x,y=batch([r for r in panel if r['split']=='train'][:2]);results=[]
 for arm in ARMS:
  m=make_model(arm);opt=optimizer(m);before={n:p.detach().clone() for n,p in m.named_parameters() if p.requires_grad};coverage={id(p) for g in opt.param_groups for p in g['params']};assert len(coverage)==len(before)
  for _ in range(2):
   opt.zero_grad();logits,_=forward_answer(m,x);loss=F.cross_entropy(logits,y);loss.backward()
   for name,p in m.named_parameters():
    if p.requires_grad:
     assert p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum()>0,(arm,name)
   opt.step()
  assert all(not torch.equal(before[n],p) for n,p in m.named_parameters() if p.requires_grad)
  state=copy.deepcopy(checkpoint(m,opt,2,4,{'seed':17,'epoch':0}));buf=io.BytesIO();torch.save(state,buf);buf.seek(0);state=torch.load(buf,weights_only=True)
  other=make_model(arm);other.load_state_dict(state['model'],strict=True);oo=optimizer(other);oo.load_state_dict(state['optimizer'])
  for mm,op in [(m,opt),(other,oo)]:
   torch.set_rng_state(state['rng']);op.zero_grad();l,_=forward_answer(mm,x);F.cross_entropy(l,y).backward();op.step()
  assert all(torch.equal(a,b) for a,b in zip(m.parameters(),other.parameters()))
  def equal(a,b):
   if isinstance(a,torch.Tensor):return torch.equal(a,b)
   if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
   if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
   return a==b
  assert equal(opt.state_dict(),oo.state_dict())
  results.append({'arm':arm,'status':'PASS','parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'trainable_tensors':len(before),'frozen_tensors':[n for n,p in m.named_parameters() if not p.requires_grad],'updates':3,'resume_error':0.,'optimizer_state_equal':True,'checkpoint_keys':list(state)})
 (R/'results/engineering.json').write_text(json.dumps(results,indent=2));return results
@torch.no_grad()
def evaluate(m,rows,arm,seed,stage):
 m.eval();records=[];gate_data=[];losses=[]
 for i in range(0,len(rows),16):
  rr=rows[i:i+16];x,y=batch(rr);logits,out=forward_answer(m,x);nll=F.cross_entropy(logits,y,reduction='none');pred=logits.argmax(-1);choices=torch.tensor([load_tokenizer().encode(str(i))[0] for i in range(8)]);restricted=choices[logits[:,choices].argmax(-1)]
  for j,r in enumerate(rr):records.append({'id':r['id'],'task':r['task'],'arm':arm,'seed':seed,'stage':stage,'label':int(y[j]),'prediction':int(pred[j]),'candidate_prediction':int(restricted[j]),'correct':bool(pred[j]==y[j]),'candidate_correct':bool(restricted[j]==y[j]),'nll':float(nll[j]),'family':r['family']})
  if out and out.trace.get('write'):
   for j,r in enumerate(rr):
    for k,(op,ent,val) in enumerate(r['semantics']):
     relevant=ent==r['entity'] and op in ['!','=','+','$','^','-']
     gate_data.append({'id':r['id'],'chunk':k,'task_relevant':relevant,'op':op,'write_mean':float(out.trace['write'][k][j].mean()),'erase_mean':float(out.trace['erase'][k][j].mean()),'memory_norm':float(out.trace['memory_after'][k][j].norm())})
 m.train()
 return records,gate_data

def learn(max_seconds=2400):
 panel=[json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines()];assert (R/'results/engineering.json').exists()
 train=[x for x in panel if x['split']=='train'];dev=[x for x in panel if x['split']=='dev'];start=time.monotonic();outdir=R/'results/learning';outdir.mkdir(exist_ok=True)
 cfg={'version':'synthetic-v1','seeds':[17,29,43],'arms':ARMS,'updates':100,'batch':8,'chunk':8,'width':32,'layers':1,'lr':.003,'max_seconds':max_seconds,'objective':'Full-vocabulary next-token cross entropy at answer position only','timing':'single CPU thread; eval excluded from train update time','evaluation':'all dev after exactly 100 updates; no early stopping by quality'}
 (R/'results/learning-config.json').write_text(json.dumps(cfg,indent=2))
 for seed in cfg['seeds']:
  rng=random.Random(seed+5000);order=[rng.sample(range(len(train)),8) for _ in range(100)];orderhash=hashlib.sha256(json.dumps(order).encode()).hexdigest();(outdir/f'order-{seed}.json').write_text(json.dumps(order))
  for arm in ARMS:
   dest=outdir/f'{arm}-{seed}.json'
   if dest.exists():continue
   if time.monotonic()-start>max_seconds:
    (outdir/'TIME_LIMIT.json').write_text(json.dumps({'seed':seed,'next_arm':arm,'elapsed_s':time.monotonic()-start}));return
   m=make_model(arm,seed);op=optimizer(m);initial,_=evaluate(m,dev,arm,seed,'initial');logs=[];t0=time.monotonic()
   for step,indices in enumerate(order):
    x,y=batch([train[k] for k in indices]);ts=time.monotonic();op.zero_grad(set_to_none=True);logits,output=forward_answer(m,x);loss=F.cross_entropy(logits,y)
    assert torch.isfinite(loss);loss.backward();gradnorm=torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);op.step()
    logs.append({'update':step+1,'loss':float(loss),'gradient_norm':float(gradnorm),'update_s':time.monotonic()-ts,'targets':len(y),'input_ids':x.numel(),'candidate_slots_executed':output.stats.get('candidate_slots_executed',0) if output else None})
   train_s=time.monotonic()-t0;final,gates=evaluate(m,dev,arm,seed,'final');trained,_=evaluate(m,train,arm,seed,'train_final')
   (outdir/f'{arm}-{seed}-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in initial+final+trained))
   (outdir/f'{arm}-{seed}-gates.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in gates))
   metrics={stage:{task:{'n':len(rr:=[r for r in records if r['task']==task]),'accuracy':sum(r['correct'] for r in rr)/len(rr),'candidate_accuracy':sum(r['candidate_correct'] for r in rr)/len(rr),'nll':sum(r['nll'] for r in rr)/len(rr)} for task in TASKS} for stage,records in [('initial',initial),('final',final),('train_final',trained)]}
   result={'arm':arm,'seed':seed,'order_sha256':orderhash,'train_s':train_s,'targets':800,'input_ids':51200,'parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'metrics':metrics,'updates':logs,'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
   dest.write_text(json.dumps(result,indent=2));torch.save(checkpoint(m,op,100,800,{'order_sha256':orderhash,'seed':seed}),outdir/f'{arm}-{seed}.pt')
   print(arm,seed,'dev_accuracy',sum(r['correct'] for r in final)/len(final),'nll',sum(r['nll'] for r in final)/len(final),'train_s',round(train_s,2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','learn']);p.add_argument('--max-seconds',type=int,default=2400);a=p.parse_args()
 if a.mode=='preflight':print(json.dumps(structural_preflight([json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines()]),indent=2))
 else:learn(a.max_seconds)
