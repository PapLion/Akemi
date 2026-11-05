"""F2 technical preflight only. No corpus training entry point."""
from pathlib import Path
import sys,random,json,time,resource,copy,hashlib,statistics
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent))
import torch
from torch import nn
import torch.nn.functional as F
from vendor.cryo_historical import Baseline,language_loss
P={'seed':17,'vocab':8192,'width':128,'layers':4,'fast_steps':2,'precision':'CPU FP32','threads':1,'batch':2,'contexts':[128,256],'warmup_updates':2,'measured_updates':5,'lr':.003,'betas':[.9,.95],'weight_decay':.01,'clip':1.,'training_authorized':False,'data':'synthetic deterministic token IDs; technical benchmark only'}
torch.set_num_threads(1)
class F2(Baseline):
 def __init__(self):
  super().__init__(v=8192,d=128,layers=4,dropout=0.);del self.norm
  self.fast=nn.Linear(384,128);self.fast_norm=nn.RMSNorm(128,eps=1e-6);self.slow_norm=nn.RMSNorm(128,eps=1e-6);self.init_weights(self.fast)
 def forward(self,ids,doc=None,valid=None):
  x=self.hidden(ids,doc,valid);z=x
  for _ in range(2):z=self.fast_norm(z+torch.tanh(self.fast(torch.cat([z,x,torch.zeros_like(x)],-1))))
  out=F.linear(self.slow_norm(z),self.emb.weight)
  return out if valid is None else out*valid[...,None]
def make(kind):
 random.seed(17);torch.manual_seed(17)
 return F2() if kind=='F2' else Baseline(v=8192,d=128,layers=4,dropout=0.)
def opt(m):return torch.optim.AdamW(m.parameters(),lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
def fixture(u,T=32):
 g=torch.Generator().manual_seed(17000+u);x=torch.randint(0,256,(2,T),generator=g);doc=torch.zeros_like(x);v=torch.ones_like(x,dtype=torch.bool);return x,doc,v
def update(m,o,u,T=32):
 x,d,v=fixture(u,T);o.zero_grad(set_to_none=True);t=time.perf_counter();y=m(x,d,v);loss=language_loss(y,x,d,v);a=time.perf_counter();loss.backward();b=time.perf_counter();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters());gn=torch.nn.utils.clip_grad_norm_(m.parameters(),1);o.step();c=time.perf_counter()
 return dict(forward_ms=(a-t)*1000,backward_ms=(b-a)*1000,adamw_and_clip_ms=(c-b)*1000,update_ms=(c-t)*1000,targets=2*(T-1),loss=float(loss.detach()),gradient_norm=float(gn))
def snapshot(path,m,o,u,kind):
 torch.save(dict(model=m.state_dict(),optimizer=o.state_dict(),cursor=u,torch_rng=torch.get_rng_state(),python_rng=random.getstate(),protocol=P,kind=kind,source_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),path)
def restore(path):
 c=torch.load(path,weights_only=True);assert c['protocol']==P and c['source_sha']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest();m=make(c['kind']);o=opt(m);m.load_state_dict(c['model']);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c['cursor']
def equal(a,b):
 if isinstance(a,torch.Tensor):return torch.equal(a,b)
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
def contracts(kind,out):
 m=make(kind);o=opt(m);x,d,v=fixture(0);y=m(x,d,v);alt=x.clone();alt[:,16:]=(alt[:,16:]+1)%256;assert torch.equal(y[:,:16],m(alt,d,v)[:,:16])
 assert torch.allclose(y[:1],m(x[:1],d[:1],v[:1]),atol=1e-6,rtol=1e-5)
 # Packed documents: no attention, positional or target transitions across boundaries.
 d[:,16:]=1;z=m(x,d,v);assert torch.allclose(z[:,16:],m(x[:,16:],d[:,16:]),atol=1e-6,rtol=1e-5)
 mask=d[:,:-1]==d[:,1:];assert torch.equal(language_loss(z,x,d,v),F.cross_entropy(z[:,:-1][mask],x[:,1:][mask]))
 v[:,-4:]=False;a=language_loss(m(x,d,v),x,d,v);xx=x.clone();xx[:,-4:]=42;assert torch.equal(a,language_loss(m(xx,d,v),xx,d,v))
 assert {id(p) for p in m.parameters()}=={id(p) for g in o.param_groups for p in g['params']}
 before=m.emb.weight.detach().clone()
 for u in range(2):update(m,o,u)
 assert not torch.equal(before,m.emb.weight);snapshot(out/f'{kind}-resume.pt',m,o,2,kind)
 for u in range(2,6):update(m,o,u)
 target=copy.deepcopy((m.state_dict(),o.state_dict(),torch.get_rng_state(),random.getstate()));r,ro,c=restore(out/f'{kind}-resume.pt')
 for u in range(c,6):update(r,ro,u)
 assert equal(target,(r.state_dict(),ro.state_dict(),torch.get_rng_state(),random.getstate()))
 # Prefix recomputation generation, no hidden KV state or memory.
 ids=torch.tensor([[257,48,49]])
 for _ in range(4):ids=torch.cat([ids,m(ids)[:,-1].argmax(-1,keepdim=True)],1)
 return {'causal':True,'row_isolation':True,'document_reset':True,'shift':True,'padding_mask':True,'finite_all_gradients':True,'parameters_updated':True,'adamw_coverage':True,'resume_6_vs_2_plus_4_exact_model_optimizer_rng_cursor':True,'generation_ids':ids.tolist()}
def main():
 out=ROOT/'results';(ROOT/'F2_CONFIG.json').write_text(json.dumps(P,indent=2)+'\n');results={}
 for kind in ['F2','Transformer']:
  checks=contracts(kind,out);m=make(kind);params=sum(p.numel() for p in m.parameters());bench=[]
  assert params==(2082176 if kind=='F2' else 2032768)
  for T in P['contexts']:
   m=make(kind);o=opt(m)
   for u in range(2):update(m,o,u,T)
   rows=[update(m,o,u,T) for u in range(2,7)];t=time.perf_counter();snapshot(out/f'{kind}-{T}.pt',m,o,7,kind);save=time.perf_counter()-t;t=time.perf_counter();restore(out/f'{kind}-{T}.pt');load=time.perf_counter()-t
   total=sum(r['update_ms'] for r in rows)/1000;rate=sum(r['targets'] for r in rows)/total
   bench.append({'context':T,'batch':2,'updates':rows,'targets_per_second':rate,'mean_update_ms':statistics.mean(r['update_ms'] for r in rows),'stdev_update_ms':statistics.stdev(r['update_ms'] for r in rows),'checkpoint_seconds':save,'restore_seconds':load,'five_million_compute_hours':5e6/rate/3600,'rough_dense_train_flops_per_target':6*params,'attention_extra_flops_note':'6P heuristic excludes attention quadratic term, activation/RoPE/normalization overhead and tied embedding lookup savings'})
  results[kind]={'parameters':params,'embedding_tied_parameters':m.emb.weight.numel(),'contracts':checks,'benchmark':bench,'process_peak_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
 (out/'f2-benchmark.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:{'parameters':v['parameters'],'rates':[(b['context'],b['targets_per_second']) for b in v['benchmark']]} for k,v in results.items()}))
if __name__=='__main__':main()
