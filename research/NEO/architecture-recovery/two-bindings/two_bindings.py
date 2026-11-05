"""Fixed paired supervision experiment; no architecture changes, CPU only."""
import sys,json,random,hashlib,collections,time,copy,platform
from pathlib import Path
import torch
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'association-interference'))
import interference_runner as I
P=I.P
torch.set_num_threads(1)
CONFIG=dict(seed=17,decoder_seed=101,updates=150,batch=8,lr=.003,betas=[.9,.95],weight_decay=.01,clip=1.,lambda_initial=.1,lambda_post=.1,precision='CPU FP32',threads=1,aux_pass_accuracy=.9,aux_pass_ce=.5)
def dump(p,x):p.write_text(json.dumps(x,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def data(dev=False):
 rows=[]
 # Each ordered role pair, all 16 value pairs, both write orders, both event types.
 # Five cyclic pairs; dev changes layout and reverses each matched write order.
 for qi,q in enumerate('ABCDE'):
  other='ABCDE'[(qi+1)%5]
  for va in range(4):
   for vb in range(4):
    for order in range(2):
     for kind in ['preserve','correct']:
      start=4 if dev else 2*order
      event=10 if dev else 6
      ops=[['~',q,'0'] for _ in range(15)]
      facts=[['=',q,str(va)],['=',other,str(vb)]]
      if order ^ dev:facts.reverse()
      ops[start:start+2]=facts
      # Rotate corrected role. Query is role A; B may instead be corrected.
      affected=q if (qi+order)%2==0 else other
      old=va if affected==q else vb
      delta=1+qi%3
      ops[event]=['!',affected,str(old if kind=='preserve' else (old+delta)%4)]
      r=P.make_record(ops,q,'two_binding_'+kind,'dev' if dev else 'train')
      r.update(q=q,other=other,kind=kind,affected=affected,stages=[start//2,event//2],event=event,initial_values=[va,vb],write_order=order)
      rows.append(r)
 return rows

def stage(m,d,rows,tr,index):
 states=[];entities=[];ys=[];meta=[]
 for b,r in enumerate(rows):
  j=r['stages'][index] if index<2 else 6
  for role,e in enumerate([r['q'],r['other']]):
   value=P.oracle(r['ops'][:min(2*j+2,15)],e)
   assert value in range(4)
   states.append(tr[j]['memory'][b].flatten());entities.append('ABCDE'.index(e));ys.append(value);meta.append((b,j,role,e,value))
 logits=d(torch.stack(states),torch.tensor(entities));target=torch.tensor(ys)
 return F.cross_entropy(logits,target),logits,target,meta

def losses(m,d,rows):
 logits,tr=m(torch.tensor([r['ids'] for r in rows]),trace=True)
 a=stage(m,d,rows,tr,0);b=stage(m,d,rows,tr,1)
 lm=F.cross_entropy(logits[:,-1],torch.tensor([r['label'] for r in rows]))
 return lm,a,b,logits,tr

def total(lm,initial,post,arm):return lm+.1*initial+(.1*post if arm=='B' else 0.)
def setup():return I.setup()
def update(m,d,o,rng,rows,arm):
 indices=[rng.randrange(len(rows)) for _ in range(8)];batch=[rows[i] for i in indices];o.zero_grad(set_to_none=True)
 lm,a,b,_,tr=losses(m,d,batch);loss=total(lm,a[0],b[0],arm);loss.backward()
 assert all(torch.isfinite(p.grad).all() for p in [*m.parameters(),*d.parameters()] if p.grad is not None)
 grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None}
 torch.nn.utils.clip_grad_norm_([*m.parameters(),*d.parameters()],1.);o.step()
 return dict(indices=indices,lm=float(lm.detach()),initial_ce=float(a[0].detach()),post_ce=float(b[0].detach()),total=float(loss.detach()),initial_accuracy=float((a[1].argmax(-1)==a[2]).float().mean()),post_accuracy=float((b[1].argmax(-1)==b[2]).float().mean()),gradients=grads)
def save(path,m,d,o,rng,rows,arm,step):
 torch.save(dict(model=m.state_dict(),decoder=d.state_dict(),optimizer=o.state_dict(),rng=rng.getstate(),torch_rng=torch.get_rng_state(),python_rng=random.getstate(),cursor=step*8,step=step,microstep=0,accumulation=1,scheduler=None,config=CONFIG,arm=arm,dataset_sha256=digest(rows),model_config=m.config()),path)
def restore(path,rows,arm):
 m,d,o,rng=setup();s=torch.load(path,weights_only=True,map_location='cpu');assert s['dataset_sha256']==digest(rows) and s['arm']==arm and s['config']==CONFIG
 m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True);o.load_state_dict(s['optimizer']);rng.setstate(s['rng']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng']);assert s['cursor']==s['step']*8
 return m,d,o,rng,s['step']

def frequencies(rows):
 counts=collections.Counter()
 for r in rows:
  for k,j in enumerate(r['stages']):
   for e in [r['q'],r['other']]:
    prefix=r['ops'][:2*j+2];v=P.oracle(prefix,e)
    rev=next(int(vv) for op,ee,vv in reversed(prefix) if ee==e and op in '=!');assert rev==v
    counts[k,j,e,v,r['kind']]+=1
 for k,j,e,kind in {(k,j,e,kind) for k,j,e,v,kind in counts}:
  # Some joint position/event strata correlate with value parity; record, do not invent balance.
  pass
 marginal=collections.Counter()
 for (k,j,e,v,kind),n in counts.items():marginal[k,e,v,kind]+=n
 for k,e,kind in {(k,e,kind) for k,e,v,kind in marginal}:assert len({marginal[k,e,v,kind] for v in range(4)})==1
 return [dict(stage=k,chunk=j,entity=e,value=v,event=kind,count=n) for (k,j,e,v,kind),n in sorted(counts.items())]

def certify(out,rows):
 report={};assert len(rows)==320;assert all(len(r['ids'])==64 for r in rows)
 assert len({r['id'] for r in rows})==len(rows)
 # Dataset and complete parameter identity, all optimizer groups exact.
 m,d,o,rng=setup();n,e,p,s=setup();assert I.equal(m.state_dict(),n.state_dict()) and I.equal(d.state_dict(),e.state_dict())
 pars=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];opars=[p for g in o.param_groups for p in g['params']];assert len(opars)==len({id(p) for p in opars})==len(pars) and set(map(id,pars))==set(map(id,opars))
 # Loss coefficient tests do not depend on learned outcomes.
 z=torch.tensor(1.,requires_grad=True);u=torch.tensor(2.,requires_grad=True);v=torch.tensor(3.,requires_grad=True)
 for arm in 'AB':
  grad=torch.autograd.grad(total(z,u,v,arm),(u,v),allow_unused=True,retain_graph=True);assert abs(float(grad[0])-.1)<1e-7;assert (grad[1] is None) if arm=='A' else abs(float(grad[1])-.1)<1e-7
 batch=[rows[i] for i in [0,41,82,123,164,205,246,287]];x=torch.tensor([r['ids'] for r in batch])
 for mode in [False,True]:
  m.train(mode);y,tr=m(x,trace=True);xx=x.clone();xx[:,32:]=120;yy,tt=m(xx,trace=True);assert torch.equal(y[:,:32],yy[:,:32])
  for k in [0,1]:
   a=stage(m,d,batch,tr,k);b=stage(m,d,batch,tt,k);assert torch.equal(a[1],b[1]) and torch.equal(a[0],b[0]);assert a[3]==b[3]
  assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-6,rtol=1e-5)
  joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1)
  assert torch.allclose(m(joined,doc=doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
  valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127;assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
 m.eval();lm,a,b,_,tr=losses(m,d,batch)
 a[0].backward();g={name:float(p.grad.norm()) for name,p in m.named_parameters() if p.grad is not None};assert any('memory_head.value' in k and val>0 for k,val in g.items());assert all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
 # Prefix-only equivalence at each actually supervised state.
 maxerr=0.
 with torch.no_grad():
  for r in batch:
   full=m(torch.tensor([r['ids']]),trace=True)[1]
   for j in r['stages']:
    short=m(torch.tensor([r['ids'][:8*(j+1)]]),trace=True)[1][-1]['memory'];diff=(full[j]['memory']-short).abs().max();maxerr=max(maxerr,float(diff));assert torch.allclose(full[j]['memory'],short,atol=1e-5,rtol=1e-5)
 # Exact end-to-end resume for BOTH changed objectives, 4+4 updates.
 for arm in 'AB':
  m,d,o,rng=setup();hist=[update(m,d,o,rng,rows,arm) for _ in range(4)];save(out/f'cert-resume-{arm}.pt',m,d,o,rng,rows,arm,4)
  hist.extend(update(m,d,o,rng,rows,arm) for _ in range(4))
  final=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state(),random.getstate()))
  n,e,p,s,step=restore(out/f'cert-resume-{arm}.pt',rows,arm);tail=[update(n,e,p,s,rows,arm) for _ in range(step,8)]
  assert I.equal(final,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state(),random.getstate()));assert hist[4:]==tail
  report[arm]=dict(exact_resume=True,updates=8,split=4,sample_indices=[r['indices'] for r in hist])
 report.update(pass_all=True,prefix_max_abs=maxerr,gradient_norms_initial=g,loss_coefficients={'A':[1.,.1,0.],'B':[1.,.1,.1]},train_eval_causal=True,masks=True,session_isolation=True,initial_identity=True,optimizer_coverage=True,normal_decoder_not_in_forward=True)
 dump(out/'certification.json',report)

def evaluate(m,d,rows):
 accum={};states=[];predictions=[]
 with torch.no_grad():
  for start in range(0,len(rows),16):
   batch=rows[start:start+16];lm,a,b,logits,tr=losses(m,d,batch);st=[a,b,stage(m,d,batch,tr,2)]
   for bi,r in enumerate(batch):
    row=dict(id=r['id'],kind=r['kind'],q=r['q'],other=r['other'],affected=r['affected'],original_prediction=int(logits[bi,-1].argmax()),original_label=r['label'],stages={})
    for name,ss in zip(['initial','post','retained'],st):
     ll=ss[1][2*bi:2*bi+2];yy=ss[2][2*bi:2*bi+2];row['stages'][name]=dict(pred=ll.argmax(-1).tolist(),label=yy.tolist(),ce=F.cross_entropy(ll,yy,reduction='none').tolist())
    predictions.append(row);states.append(torch.stack([tr[j]['memory'][bi].cpu() for j in [r['stages'][0],r['stages'][1],6]]))
 for kind in ['all','preserve','correct']:
  records=[r for r in predictions if kind=='all' or r['kind']==kind];n=len(records);metrics={}
  if not n:continue
  for name in ['initial','post','retained']:
   correct=[[int(r['stages'][name]['pred'][i]==r['stages'][name]['label'][i]) for i in range(2)] for r in records]
   conf={}
   for r in records:
    for i,e in enumerate([r['q'],r['other']]):
     conf.setdefault(e,[[0]*4 for _ in range(4)]);conf[e][r['stages'][name]['label'][i]][r['stages'][name]['pred'][i]]+=1
   metrics[name]=dict(A_accuracy=sum(v[0] for v in correct)/n,B_accuracy=sum(v[1] for v in correct)/n,joint_accuracy=sum(all(v) for v in correct)/n,ce_A=sum(r['stages'][name]['ce'][0] for r in records)/n,ce_B=sum(r['stages'][name]['ce'][1] for r in records)/n,confusion_per_entity=conf)
  metrics['original_accuracy']=sum(r['original_prediction']==r['original_label'] for r in records)/n
  metrics['unjustified_changes_A']=sum(r['stages']['initial']['pred'][0]!=r['stages']['post']['pred'][0] for r in records if r['stages']['initial']['label'][0]==r['stages']['post']['label'][0])/sum(r['stages']['initial']['label'][0]==r['stages']['post']['label'][0] for r in records)
  accum[kind]=metrics
 return dict(metrics=accum,predictions=predictions),torch.stack(states)

def provenance():
 root=R.parent.parent/'cryo-association-learning-v1';files=[]
 for sub in ['association','association-repair','association-interference']:
  for p in sorted((root/sub).rglob('*')):
   if p.is_file() and '__pycache__' not in str(p):files.append((str(p),sha(p)))
 return files

def main():
 out=R/'results';out.mkdir(exist_ok=False);before=provenance();dump(out/'historical-hashes-before.json',before)
 train=data();dev=data(True);assert not {r['id'] for r in train}&{r['id'] for r in dev}
 dump(out/'train.json',train);dump(out/'dev-layout.json',dev);dump(out/'frequencies.json',dict(train=frequencies(train),dev=frequencies(dev)))
 dump(out/'protocol.json',dict(config=CONFIG,objective_A='LM + .1 CE_initial',objective_B='LM + .1 CE_initial + .1 CE_post',dataset_sha256=digest(train),dev_sha256=digest(dev),train_records=len(train),dev_records=len(dev),torch_version=str(torch.__version__),platform=platform.platform()))
 certify(out,train);print('ALL PRETRAINING CONTRACTS PASS',flush=True)
 for arm in 'AB':
  m,d,o,rng=setup();save(out/f'{arm}-initial.pt',m,d,o,rng,train,arm,0);logs=[];t=time.monotonic()
  for step in range(150):
   logs.append(update(m,d,o,rng,train,arm))
   if step==74:save(out/f'{arm}-75.pt',m,d,o,rng,train,arm,75)
   if step%25==0:print(arm,step,logs[-1]['initial_ce'],logs[-1]['post_ce'],flush=True)
  seconds=time.monotonic()-t;save(out/f'{arm}-150.pt',m,d,o,rng,train,arm,150);dump(out/f'{arm}-curves.json',logs)
  for name,rows in [('train',train),('dev-layout',dev)]:
   ev,states=evaluate(m,d,rows);ev['training_seconds']=seconds;dump(out/f'{arm}-{name}-evaluation.json',ev);torch.save(dict(states=states,ids=[r['id'] for r in rows],stage_order=['initial','post','retained']),out/f'{arm}-{name}-states.pt');print(arm,name,ev['metrics']['all']['initial'],flush=True)
 after=provenance();assert before==after;dump(out/'historical-preservation.json',dict(exact_unchanged=True,files=len(before)))
if __name__=='__main__':main()
