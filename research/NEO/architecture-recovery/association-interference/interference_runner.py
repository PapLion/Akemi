import os,sys,json,random,hashlib,time,collections,copy
from pathlib import Path
import torch
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'association'))
import run
P=run.data_panel.panel
torch.set_num_threads(1)
def dump(p,x):p.write_text(json.dumps(x,indent=2))
def fixture(condition,layout=0):
 rows=[]
 for q in range(5):
  for offset in range(1,5):
   other=(q+offset)%5
   for v in range(4):
    for w in range(4):
     for order in range(2):
      # Balanced independent initial values; different offsets rotate 1,2,3.
      delta=1+(offset+order)%3
      e='ABCDE'[q];o='ABCDE'[other];ops=[['~',e,'0'] for _ in range(15)]
      start=0 if not layout else 2;event=4 if not layout else 8
      facts=[['=',e,str(v)],['=',o,str(w)]]
      if order:facts.reverse()
      ops[start:start+2]=facts
      target=e if condition in 'AB' else o;old=v if target==e else w
      value=old if condition in 'AC' else (old+delta)%4
      ops[event]=['!',target,str(value)]
      r=P.make_record(ops,e,'factorial','train' if not layout else 'layout')
      r.update(q=e,other=o,condition=condition,stages=[start//2,event//2],event=event)
      rows.append(r)
 return rows

def entries(rows,stages=None):
 out=[]
 for b,r in enumerate(rows):
  for j in (r['stages'] if stages is None else stages):
   for e in sorted([r['q'],r['other']]):
    y=P.oracle(r['ops'][:min(2*j+2,15)],e)
    if y!=4:out.append((b,j,'ABCDE'.index(e),y))
 return out

def forward(m,d,rows,stages=None):
 logits,tr=m(torch.tensor([r['ids'] for r in rows]),trace=True)
 en=entries(rows,stages);x=torch.stack([tr[j]['memory'][b].flatten() for b,j,e,y in en]);ee=torch.tensor([e for b,j,e,y in en]);yy=torch.tensor([y for b,j,e,y in en])
 a=d(x,ee);lm=F.cross_entropy(logits[:,-1],torch.tensor([r['label'] for r in rows]));aux=F.cross_entropy(a,yy)
 return lm,aux,a,yy,logits,tr,en

def setup():
 m,d=run.setup();o=torch.optim.AdamW([p for p in [*m.parameters(),*d.parameters()] if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 return m,d,o,random.Random(17)
def update(m,d,o,rng,rows):
 ix=[rng.randrange(len(rows)) for _ in range(8)];o.zero_grad(set_to_none=True)
 lm,aux,a,y,_,_,_=forward(m,d,[rows[i] for i in ix]);(lm+.1*aux).backward()
 grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None}
 assert all(torch.isfinite(p.grad).all() for p in [*m.parameters(),*d.parameters()] if p.grad is not None)
 torch.nn.utils.clip_grad_norm_([*m.parameters(),*d.parameters()],1);o.step()
 return dict(indices=ix,lm=float(lm.detach()),aux=float(aux.detach()),accuracy=float((a.argmax(-1)==y).float().mean()),gradients=grads)
def save(path,m,d,o,rng,step):
 torch.save(dict(model=m.state_dict(),decoder=d.state_dict(),optimizer=o.state_dict(),rng=rng.getstate(),torch_rng=torch.get_rng_state(),python_rng=random.getstate(),step=step,cursor=step*8,microstep=0,accumulation=1,scheduler=None,config=dict(lr=.003,clip=1,lambda_aux=.1,batch=8,seed=17),dataset_sha=hashlib.sha256(json.dumps(fixture('A')).encode()).hexdigest()),path)
def equal(a,b):
 if isinstance(a,torch.Tensor):return torch.equal(a,b)
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b

def certify(out):
 rows=fixture('A');m,d,o,rng=setup();params=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];assert {id(p) for p in params}=={id(p) for g in o.param_groups for p in g['params']};assert len(params)==sum(len(g['params']) for g in o.param_groups)
 x=torch.tensor([r['ids'] for r in rows[::321][:2]])
 for train in [False,True]:
  m.train(train);y,tr=m(x,trace=True);xx=x.clone();xx[:,24:]=120;z,tt=m(xx,trace=True)
  assert torch.equal(y[:,:24],z[:,:24]);assert torch.equal(tr[2]['memory'],tt[2]['memory'])
  assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-6,rtol=1e-5)
  joined=torch.cat([x[:1],x[1:]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:])],1)
  assert torch.allclose(m(joined,doc=doc)[:,64:],y[1:],atol=1e-5,rtol=1e-5)
 m.eval();lm,aux,a,y,l,tr,en=forward(m,d,rows[:8]);aux.backward()
 gradients={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert any('memory_head.value' in n and v>0 for n,v in gradients.items());assert all(torch.isfinite(t['memory'].grad).all() for t in tr[:3] if t['memory'].grad is not None)
 m,d,o,rng=setup();hist=[]
 for i in range(3):hist.append(update(m,d,o,rng,rows))
 save(out/'resume.pt',m,d,o,rng,3)
 for i in range(3):hist.append(update(m,d,o,rng,rows))
 final=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state()))
 n,e,p,s=setup();cp=torch.load(out/'resume.pt',weights_only=True);n.load_state_dict(cp['model'],strict=True);e.load_state_dict(cp['decoder'],strict=True);p.load_state_dict(cp['optimizer']);s.setstate(cp['rng']);torch.set_rng_state(cp['torch_rng']);random.setstate(cp['python_rng']);tail=[update(n,e,p,s,rows) for _ in range(cp['step'],6)]
 assert equal(final,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state()));assert hist[3:]==tail;assert cp['cursor']==24
 dump(out/'certification.json',dict(pass_all=True,continuous_updates=6,interrupt_after=3,resume_exact=True,coverage=True,causality_train_eval=True,batch_document_isolation=True,gradients=gradients,order=[r['indices'] for r in hist],scope='CPU FP32 dropout0 single-process; no CUDA/AMP'))

def evaluate(m,d,rows):
 preds=[];labels=[];details=[];loss=0;orig=0;stage_counts=collections.Counter();conf=[[0]*4 for _ in range(4)];by=collections.defaultdict(lambda:[0,0])
 with torch.no_grad():
  for i in range(0,len(rows),16):
   rr=rows[i:i+16];lm,aux,a,y,l,tr,en=forward(m,d,rr);pr=a.argmax(-1).tolist();ys=y.tolist();loss+=float(aux)*len(ys);preds+=pr;labels+=ys;orig+=sum(p==r['label'] for p,r in zip(l[:,-1].argmax(-1).tolist(),rr))
   for (b,j,e,v),p in zip(en,pr):
    conf[v][p]+=1;by[f'{e}:{v}'][1]+=1;by[f'{e}:{v}'][0]+=p==v;stage_counts[(j,'correct')]+=p==v;stage_counts[(j,'total')]+=1
   # Before query: both associations, no local context in decoder.
   _,_,aa,yy,_,_,_=forward(m,d,rr,[6]);details.extend([dict(id=r['id'],query=r['q'],response=int(pp),target=r['label']) for r,pp in zip(rr,l[:,-1].argmax(-1))]);
   for p,v in zip(aa.argmax(-1).tolist(),yy.tolist()):stage_counts[('retained','correct')]+=p==v;stage_counts[('retained','total')]+=1
 return dict(aux_ce=loss/len(labels),aux_accuracy=sum(p==v for p,v in zip(preds,labels))/len(labels),original_accuracy=orig/len(rows),confusion=conf,by_entity_value=dict(by),stage_counts={str(k):v for k,v in stage_counts.items()},predictions=preds,labels=labels,responses=details)
def main():
 out=R/'results';out.mkdir(exist_ok=False)
 data={c:fixture(c) for c in 'ABCD'}
 for c,rr in data.items():
  assert all(len(r['ids'])==64 and len(entries([r]))==4 for r in rr)
  counts=collections.Counter((e,v,j) for b,j,e,v in entries(rr))
  for e,j in {(e,j) for e,v,j in counts}:assert len({counts[e,v,j] for v in range(4)})==1
  dump(out/f'{c}-data.json',rr);dump(out/f'{c}-frequencies.json',[dict(entity=e,value=v,chunk=j,count=n) for (e,v,j),n in sorted(counts.items())])
 certify(out);print('CERTIFICATION PASS',flush=True)
 for c,rr in data.items():
  m,d,o,rng=setup();logs=[];t=time.monotonic()
  for step in range(150):
   logs.append(update(m,d,o,rng,rr))
   if step%25==0:print(c,step,logs[-1]['aux'],flush=True)
  save(out/f'{c}.pt',m,d,o,rng,150);dump(out/f'{c}-curves.json',logs)
  result={'train':evaluate(m,d,rr),'new_layout':evaluate(m,d,fixture(c,1)),'seconds':time.monotonic()-t};dump(out/f'{c}-evaluation.json',result);print(c,{k:result['train'][k] for k in ['aux_accuracy','aux_ce','original_accuracy']},flush=True)
if __name__=='__main__':main()
