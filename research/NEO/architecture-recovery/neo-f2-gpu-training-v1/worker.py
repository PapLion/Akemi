"""F2 private GPU training; fixed recipe, exact finite data pass, resumable updates."""
from pathlib import Path
import os,json,time,random,hashlib,math,resource,copy,argparse,collections
import numpy as np
import torch
import torch.nn.functional as F
import f2
R=Path(__file__).resolve().parent
CFG=dict(seed=17,context=128,batch=2,max_targets=5000000,lr=.003,betas=[.9,.95],weight_decay=.01,clip=1.,precision='FP32',Hielo=False,Trapos=False)
PROMPTS=['La historia de','The purpose of','En matemáticas,','A Python function']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sync(device):
 if device=='cuda':torch.cuda.synchronize()
class Data:
 def __init__(self,split):
  a=np.load(R/(split+'.npz'));self.ids=a['ids'];self.offsets=a['offsets'];self.langs=a['langs'];self.windows=[]
  for d in range(len(self.offsets)-1):
   for off in range(int(self.offsets[d]),int(self.offsets[d+1])-1,127):self.windows.append((d,off,min(128,int(self.offsets[d+1])-off)))
  if split=='train':random.Random(17).shuffle(self.windows)
  self.sha=sha(R/(split+'.npz'));self.order_sha=hashlib.sha256(json.dumps(self.windows).encode()).hexdigest();self.cursor=0;self.targets=0
 def batch(self,device,budget=None):
  x=torch.full((2,128),256,dtype=torch.long);valid=torch.zeros_like(x,dtype=torch.bool);langs=[];keys=[];n=0
  for i in range(2):
   if self.cursor==len(self.windows) or (budget is not None and n==budget):break
   d,off,length=self.windows[self.cursor];self.cursor+=1
   if budget is not None:length=min(length,budget-n+1)
   assert length>=2
   x[i,:length]=torch.from_numpy(self.ids[off:off+length].astype(np.int64));valid[i,:length]=True;langs.append(str(self.langs[d]));keys.append((d,off,length));n+=length-1
  self.targets+=n
  return x.to(device),torch.zeros_like(x,device=device),valid.to(device),n,langs,keys
 def state(self):return dict(cursor=self.cursor,targets=self.targets,sha=self.sha,order_sha=self.order_sha)
 def load(self,s):
  assert s['sha']==self.sha and s['order_sha']==self.order_sha
  self.cursor=s['cursor'];self.targets=s['targets']
def checkpoint(path,m,o,d,u,device,extra):
 c=dict(model=m.state_dict(),optimizer=o.state_dict(),reader=d.state(),update=u,config=CFG,torch_rng=torch.get_rng_state(),python_rng=random.getstate(),numpy_rng=None,cuda_rng=torch.cuda.get_rng_state_all() if device=='cuda' else [],dataset_manifest_sha=sha(R/'dataset.json'),model_source_sha=sha(R/'f2.py'),worker_sha=sha(__file__),extra=extra)
 tmp=Path(str(path)+'.tmp');torch.save(c,tmp);os.replace(tmp,path)
def restore(path,m,o,d,device):
 c=torch.load(path,map_location='cpu',weights_only=True);assert c['config']==CFG and c['dataset_manifest_sha']==sha(R/'dataset.json') and c['model_source_sha']==sha(R/'f2.py') and c['worker_sha']==sha(__file__)
 m.load_state_dict(c['model']);o.load_state_dict(c['optimizer']);d.load(c['reader']);torch.set_rng_state(c['torch_rng'].cpu());random.setstate(c['python_rng'])
 if device=='cuda':torch.cuda.set_rng_state_all([s.cpu() for s in c['cuda_rng']])
 return c
@torch.no_grad()
def evaluate(m,device,limit=None):
 m.eval();d=Data('dev');stats=collections.defaultdict(lambda:[0.,0]);start=time.perf_counter()
 while d.cursor<len(d.windows) and (limit is None or d.cursor<limit):
  x,doc,v,n,langs,_=d.batch(device);y=m(x,doc,v);mask=v[:,:-1]&v[:,1:]
  ce=F.cross_entropy(y[:,:-1].float().reshape(-1,8192),x[:,1:].reshape(-1),reduction='none').view(2,127)
  for i,lang in enumerate(langs):
   nn=int(mask[i].sum());ss=float(ce[i][mask[i]].sum());stats[lang][0]+=ss;stats[lang][1]+=nn;stats['all'][0]+=ss;stats['all'][1]+=nn
 sync(device);m.train();return {k:dict(nll=s/n,ppl=math.exp(min(50,s/n)),targets=n,domain='encyclopedia') for k,(s,n) in stats.items()}|{'seconds':time.perf_counter()-start}
def update(m,o,d,device,budget=None):
 x,doc,v,n,langs,keys=d.batch(device,budget);o.zero_grad(set_to_none=True);sync(device);t=time.perf_counter();loss=f2.language_loss(m(x,doc,v),x,doc,v);loss.backward()
 assert torch.isfinite(loss);assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters())
 gn=torch.nn.utils.clip_grad_norm_(m.parameters(),1.);o.step();sync(device);dt=time.perf_counter()-t
 return dict(loss=float(loss.detach()),gradient_norm=float(gn),clipped=float(gn)>1,targets=n,seconds=dt,keys=keys)
def preflight(device,out):
 m=f2.make('F2').to(device);o=f2.opt(m);d=Data('train');x,doc,v,_,_,_=d.batch(device);y=m(x,doc,v);z=x.clone();z[:,64:]=42
 assert torch.equal(y[:,:64],m(z,doc,v)[:,:64])
 assert torch.allclose(y[:1],m(x[:1],doc[:1],v[:1]),atol=1e-5,rtol=1e-5)
 xx=x.clone();vv=v.clone();vv[:,-5:]=False;aa=f2.language_loss(m(xx,doc,vv),xx,doc,vv);xx[:,-5:]=48;assert torch.equal(aa,f2.language_loss(m(xx,doc,vv),xx,doc,vv))
 assert {id(p) for p in m.parameters()}=={id(p) for g in o.param_groups for p in g['params']}
 # RNG + AdamW + reader end-to-end exact resume on the actual selected corpus.
 d=Data('train');rows=[update(m,o,d,device) for _ in range(2)];checkpoint(out/'preflight.pt',m,o,d,2,device,{})
 rows +=[update(m,o,d,device) for _ in range(2)];expected=copy.deepcopy((m.state_dict(),o.state_dict(),d.state(),torch.get_rng_state(),random.getstate(),torch.cuda.get_rng_state_all() if device=='cuda' else []))
 n=f2.make('F2').to(device);no=f2.opt(n);dd=Data('train');restore(out/'preflight.pt',n,no,dd,device);rr=[update(n,no,dd,device) for _ in range(2)]
 actual=(n.state_dict(),no.state_dict(),dd.state(),torch.get_rng_state(),random.getstate(),torch.cuda.get_rng_state_all() if device=='cuda' else [])
 assert f2.equal(expected,actual) and [r['loss'] for r in rows[2:]]==[r['loss'] for r in rr]
 bf=dict(supported=device=='cuda' and torch.cuda.is_bf16_supported(),training_precision='FP32')
 if bf['supported']:
  try:
   with torch.no_grad(),torch.autocast('cuda',dtype=torch.bfloat16):b=m(x,doc,v)
   bf['finite']=bool(torch.isfinite(b).all());bf['max_logit_abs_vs_fp32']=float((b.float()-m(x,doc,v)).abs().max())
  except RuntimeError as error:bf['failure']=str(error)
  bf['decision']='diagnostic only; FP32 recipe retained, no BF16 training certificate claimed'
 dump(out/'preflight.json',dict(status='PASS',causal=True,padding=True,row_isolation=True,adamw=True,all_gradients_finite=True,exact_4_vs_2_plus_2_resume=True,targets_per_pass=sum(n-1 for _,_,n in Data('train').windows),bf16=bf,technical_updates=6))
 (out/'preflight.pt').unlink()
@torch.no_grad()
def generate(m,device):
 from core import NeoTokenizer
 tok=NeoTokenizer.load(R/'tokenizer.json',expected_fingerprint='813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b');m.eval();out=[]
 for prompt in PROMPTS:
  ids=[257]+tok.encode(prompt);generated=[]
  for _ in range(64):
   x=torch.tensor([ids[-128:]],device=device);logits=m(x)[0,-1].float();logits[256:512]=-float('inf');n=int(logits.argmax());generated.append(n);ids.append(n)
  words=tok.decode(generated,errors='replace').split();tri=[tuple(words[i:i+3]) for i in range(len(words)-2)]
  out.append(dict(prompt=prompt,generated=tok.decode(generated,errors='replace'),ids=generated,word_type_token_ratio=len(set(words))/max(1,len(words)),repeated_trigram_fraction=1-len(set(tri))/max(1,len(tri))))
 m.train();return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['F2','Transformer'],default='F2');ap.add_argument('--device',default='cuda');ap.add_argument('--preflight',action='store_true');ap.add_argument('--technical-updates',type=int,default=0);args=ap.parse_args();device=args.device
 torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 out=R/'results'/args.kind;out.mkdir(parents=True,exist_ok=True)
 if args.preflight:preflight(device,out);return
 m=f2.make(args.kind).to(device);o=f2.opt(m);d=Data('train');u=0;weighted=0.;seen=0;elapsed=0.;nextsave=1000000
 latest=out/'latest.pt'
 if latest.exists():
  c=restore(latest,m,o,d,device);u=c['update'];weighted=c['extra']['weighted'];seen=c['extra']['seen'];elapsed=c['extra']['elapsed'];nextsave=(seen//1000000+1)*1000000
 else:dump(out/'initial-dev.json',evaluate(m,device))
 start=time.perf_counter();metrics=out/'curve.jsonl'
 with metrics.open('a',buffering=1) as log:
  while d.cursor<len(d.windows) and seen<CFG['max_targets']:
   row=update(m,o,d,device,CFG['max_targets']-seen);u+=1;seen+=row['targets'];weighted+=row['loss']*row['targets'];elapsed+=row['seconds']
   log.write(json.dumps(dict(update=u,targets_seen=seen,loss=row['loss'],gradient_norm=row['gradient_norm'],clipped=row['clipped'],lr=.003,seconds=row['seconds'],cumulative_update_seconds=elapsed,targets_per_second=seen/elapsed,gpu_allocated=torch.cuda.memory_allocated() if device=='cuda' else 0))+'\n')
   if u%250==0:print(args.kind,u,seen,seen/elapsed,row['loss'],flush=True)
   if seen>=nextsave or (args.technical_updates and u>=args.technical_updates):
    checkpoint(latest,m,o,d,u,device,dict(weighted=weighted,seen=seen,elapsed=elapsed));checkpoint(out/f'targets-{seen}.pt',m,o,d,u,device,dict(weighted=weighted,seen=seen,elapsed=elapsed));dump(out/f'dev-{seen}.json',evaluate(m,device,64));nextsave+=1000000
   if args.technical_updates and u>=args.technical_updates:return
 checkpoint(out/'final.pt',m,o,d,u,device,dict(weighted=weighted,seen=seen,elapsed=elapsed));checkpoint(latest,m,o,d,u,device,dict(weighted=weighted,seen=seen,elapsed=elapsed))
 dev=evaluate(m,device);gens=generate(m,device)
 dump(out/'generations.json',gens)
 # Fixed train NLL on 256 windows, distinct from online optimization average.
 td=Data('train');m.eval();sn=0.;nt=0
 with torch.no_grad():
  while td.cursor<min(256,len(td.windows)):
   x,doc,v,n,_,_=td.batch(device);sn+=float(f2.language_loss(m(x,doc,v),x,doc,v))*n;nt+=n
 dump(out/'summary.json',dict(kind=args.kind,parameters=sum(p.numel() for p in m.parameters()),targets=seen,updates=u,online_train_nll=weighted/seen,final_train_fixed_sample_nll=sn/nt,final_train_sample_targets=nt,dev=dev,update_seconds=elapsed,wall_seconds_this_process=time.perf_counter()-start,targets_per_second=seen/elapsed,peak_gpu_allocated=torch.cuda.max_memory_allocated() if device=='cuda' else 0,peak_rss_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,dataset_sha=sha(R/'dataset.json'),checkpoint_sha=sha(out/'final.pt'),config=CFG))
 print('COMPLETE',args.kind,seen,dev,flush=True)
if __name__=='__main__':main()
