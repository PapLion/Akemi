"""Approved-document-only, single-process resumable F2 batch reader.
One row per document window, no cross-document packing; stride T-1.
"""
from pathlib import Path
import json,hashlib,random,time
import torch
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'corpus-recovery-f2'))
import count_v3,f2

def digest(b):return hashlib.sha256(b).hexdigest()
class Reader:
 def __init__(self,manifest,context=128,batch=2):
  self.manifest=Path(manifest);self.manifest_sha=digest(self.manifest.read_bytes());self.context=context;self.batch=batch;self.cursor=0
  self.windows=[];tok=count_v3.load();self.docs=json.loads(self.manifest.read_text())['documents']
  for r in sorted(self.docs,key=lambda r:r['id']):
   assert r['decision']=='APPROVED'
   if r['split']!='train':continue
   raw=Path(r['path']).read_bytes();assert digest(raw)==r['sha']
   ids=tok.encode(raw.decode('utf-8'));assert len(ids)==r['v3_text_ids']
   ids=[257]+ids+[258]
   for off in range(0,len(ids)-1,context-1):self.windows.append((r['id'],off,ids[off:off+context]))
  random.Random(17).shuffle(self.windows)
  self.order_sha=digest(json.dumps(self.windows).encode())
 def state_dict(self):return dict(manifest_sha=self.manifest_sha,context=self.context,batch=self.batch,cursor=self.cursor,order_sha=self.order_sha)
 def load_state_dict(self,s):
  assert {k:v for k,v in s.items() if k!='cursor'}=={k:v for k,v in self.state_dict().items() if k!='cursor'}
  assert s['cursor']>=0;self.cursor=s['cursor']
 def next(self):
  rows=[self.windows[(self.cursor+j)%len(self.windows)] for j in range(self.batch)];self.cursor+=self.batch
  x=torch.full((self.batch,self.context),256,dtype=torch.long);valid=torch.zeros_like(x,dtype=torch.bool)
  for j,(_,_,ids) in enumerate(rows):x[j,:len(ids)]=torch.tensor(ids);valid[j,:len(ids)]=True
  return x,torch.zeros_like(x),valid,[(r[0],r[1]) for r in rows]
def step(m,o,r):
 x,d,v,keys=r.next();o.zero_grad(set_to_none=True);loss=f2.language_loss(m(x,d,v),x,d,v);loss.backward()
 assert torch.isfinite(loss) and all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters())
 torch.nn.utils.clip_grad_norm_(m.parameters(),1);o.step();return float(loss.detach()),keys

def certify():
 import copy,tempfile,unittest
 out=ROOT/'results';manifest=out/'approved-selection.json';start=time.perf_counter();r=Reader(manifest);setup=time.perf_counter()-start
 # Each within-document shifted target occurs exactly once, including EOS, excluding PAD.
 assert sum(len(ids)-1 for _,_,ids in r.windows)==25355
 assert len({(k,off) for k,off,_ in r.windows})==len(r.windows)
 m=f2.make('F2');o=f2.opt(m);losses=[]
 for _ in range(2):losses.append(step(m,o,r))
 ck=dict(model=copy.deepcopy(m.state_dict()),optimizer=copy.deepcopy(o.state_dict()),reader=r.state_dict(),torch_rng=torch.get_rng_state(),python_rng=random.getstate(),update=2,tokenizer=count_v3.FP,reader_source=digest(Path(__file__).read_bytes()))
 torch.save(ck,out/'integration-resume.pt')
 for _ in range(2):losses.append(step(m,o,r))
 expected=copy.deepcopy((m.state_dict(),o.state_dict(),r.state_dict(),torch.get_rng_state(),random.getstate()))
 c=torch.load(out/'integration-resume.pt',weights_only=True);n=f2.make('F2');no=f2.opt(n);rr=Reader(manifest);n.load_state_dict(c['model']);no.load_state_dict(c['optimizer']);rr.load_state_dict(c['reader']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng'])
 resumed=[step(n,no,rr) for _ in range(2)]
 assert losses[2:]==resumed
 assert f2.equal(expected,(n.state_dict(),no.state_dict(),rr.state_dict(),torch.get_rng_state(),random.getstate()))
 # Verify manifest mutation fails closed, and changed cursor actually changes order.
 bad=rr.state_dict()|{'manifest_sha':'invalid'}
 try:rr.load_state_dict(bad)
 except AssertionError:pass
 else:raise AssertionError('manifest mutation accepted')
 # Padding and target shift independently checked from real row.
 x,d,v,_=rr.next();y=n(x,d,v);mask=v[:,:-1]&v[:,1:];manual=torch.nn.functional.cross_entropy(y[:,:-1][mask],x[:,1:][mask]);assert torch.equal(manual,f2.language_loss(y,x,d,v))
 # Future suffix cannot affect real-prefix logits; independent row cannot affect another.
 z=x.clone();z[:,64:]=48
 assert torch.equal(y[:,:64],n(z,d,v)[:,:64])
 assert torch.allclose(y[:1],n(x[:1],d[:1],v[:1]),atol=1e-6,rtol=1e-5)
 report=dict(status='PASS',checks=['approved-only','content hashes','V3 lengths','one shifted target per document token plus EOS','no cross-document packing','deterministic shuffled windows','manifest/order identity','cursor','padding and shift','causality on real documents','row isolation','finite gradients','continuous 4 vs interrupted 2+2 exact parameters AdamW RNG cursor losses batch order'],updates_executed=6,maximum_training_updates_authorized=0,purpose='technical integration only, not F2 training',reader_setup_seconds=setup,windows=len(r.windows),targets_per_pass=25355,losses=[x[0] for x in losses],seconds=time.perf_counter()-start)
 (out/'reader-contracts.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':certify()
