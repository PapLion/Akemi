"""Paired chunk-boundary study. Historical neural modules are imported unchanged."""
import sys,json,collections,random,time,copy,hashlib
from pathlib import Path
import torch
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'two-bindings'))
import two_bindings as T
I=T.I;P=T.P
torch.set_num_threads(1)
CONFIG=dict(seed=17,updates=150,batch=8,lr=.003,clip=1,lambda_aux=.1,precision='CPU FP32',threads=1,positive_decoder_seed=202,positive_decoder_updates=100,positive_decoder_lr=.03,aux_pass_accuracy=.9,aux_pass_ce=.5)
def dump(name,x):T.dump(R/'results'/name,x)
def data(condition,dev=False):
 rows=[]
 for qi,q in enumerate('ABCDE'):
  other='ABCDE'[(qi+1)%5]
  for va in range(4):
   for vb in range(4):
    for order in range(2):
     ops=[['~',q,'0'] for _ in range(15)];shift=4 if dev else 0
     positions=[2+shift,3+shift] if condition=='same' else [0+shift,3+shift]
     facts=[['=',q,str(va)],['=',other,str(vb)]]
     if order:facts.reverse()
     for pos,fact in zip(positions,facts):ops[pos]=fact
     row=P.make_record(ops,q,'chunk_binding','dev' if dev else 'train')
     row.update(q=q,other=other,kind='preserve',affected=q,stages=[1+shift//2,5],event=None,condition=condition,positions=positions,write_order=order,initial_values=[va,vb])
     rows.append(row)
 return rows

def explicit(row):
 state={}
 for op,e,v in row['ops'][:2*row['stages'][0]+2]:
  if op in '=!':state[e]=int(v)
 return state

def positive():
 rows=[r for c in ['same','separate'] for dev in [False,True] for r in data(c,dev)]
 features=[];entities=[];labels=[]
 for r in rows:
  state=explicit(r);assert len(state)==2
  for e in [r['q'],r['other']]:
   assert state[e]==P.oracle(r['ops'],e)
   x=torch.zeros(256)
   for k,v in state.items():x['ABCDE'.index(k)*4+v]=1.
   features.append(x);entities.append('ABCDE'.index(e));labels.append(state[e])
 x=torch.stack(features);e=torch.tensor(entities);y=torch.tensor(labels)
 torch.manual_seed(202);d=I.run.probes.Decoder(256,4);o=torch.optim.AdamW(d.parameters(),lr=.03,weight_decay=0.)
 curve=[]
 for i in range(100):
  o.zero_grad();logits=d(x[:320],e[:320]);loss=F.cross_entropy(logits,y[:320]);loss.backward();o.step();curve.append(float(loss.detach()))
 with torch.no_grad():p=d(x,e).argmax(-1);accuracy=float((p==y).float().mean());ce=float(F.cross_entropy(d(x,e),y))
 assert accuracy==1.;dump('positive-control.json',dict(explicit_dictionary_accuracy=1.,decoder_accuracy=accuracy,decoder_ce=ce,decoder_updates=100,decoder_lr=.03,curve=curve,scope='Explicit oracle features; diagnostic only, no Hielo replacement. Decoder fits same/train mapping; other positions/order encoded identically by dictionary.'))
 torch.save(d.state_dict(),R/'results/positive-decoder.pt')

def certify(datasets):
 freq={};report={}
 for condition,rr in datasets.items():
  assert len(rr)==160;assert all(len(r['ids'])==64 and len(r['ops'])==15 for r in rr)
  count=collections.Counter((r['q'],*r['initial_values']) for r in rr);assert set(count.values())=={2}
  freq[condition]=[dict(entity=e,value=v,count=n) for (e,v),n in sorted(collections.Counter((ee,int(v)) for r in rr for op,ee,v in r['ops'] if op=='=').items())]
  assert len(set(x['count'] for x in freq[condition]))==1
 for a,b in zip(datasets['same'],datasets['separate']):
  assert a['initial_values']==b['initial_values'] and a['write_order']==b['write_order'] and a['q']==b['q'] and a['label']==b['label'] and a['stages']==b['stages']
  assert collections.Counter(tuple(op) for op in a['ops'])==collections.Counter(tuple(op) for op in b['ops'])
 m,d,o,rng=T.setup();n,e,p,s=T.setup();assert I.equal(m.state_dict(),n.state_dict()) and I.equal(d.state_dict(),e.state_dict())
 pars=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];opars=[p for g in o.param_groups for p in g['params']];assert len(opars)==len(set(map(id,opars)))==len(pars) and set(map(id,opars))==set(map(id,pars))
 visibility={}
 for cond,rr in datasets.items():
  m,d,o,rng=T.setup()
  rows=[rr[i] for i in range(0,160,20)];x=torch.tensor([r['ids'] for r in rows]);captured=[]
  def hook(module,args):captured.append(args[1].detach().clone())
  handle=m.core.blocks[0].register_forward_pre_hook(hook)
  try:
   for mode in [False,True]:
    m.train(mode);y,tr=m(x,trace=True);xx=x.clone();xx[:,16:]=120;z,tt=m(xx,trace=True)
    assert torch.equal(y[:,:16],z[:,:16]);assert torch.equal(tr[1]['memory'],tt[1]['memory'])
    aa=T.stage(m,d,rows,tr,0);bb=T.stage(m,d,rows,tt,0);assert torch.equal(aa[0],bb[0]) and torch.equal(aa[1],bb[1])
    assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-6,rtol=1e-5)
    joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1);assert torch.allclose(m(joined,doc=doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
    valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127;assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
  finally:handle.remove()
  mask=captured[0];assert mask[:,15,:16].all();assert not mask[:,63,:48].any();assert not mask.triu(1).any()
  visibility[cond]=dict(last_write_keys=mask[0,15].nonzero().flatten().tolist(),query_keys=mask[0,63].nonzero().flatten().tolist(),chunks=len(tr),meaningful_write_chunks=sorted(set(p//2 for p in rr[0]['positions'])))
  m.eval();o.zero_grad();lm,a,b,_,tr=T.losses(m,d,rows);a[0].backward();grads={name:float(p.grad.norm()) for name,p in m.named_parameters() if p.grad is not None};assert any('memory_head.value' in k and v>0 for k,v in grads.items());assert all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
  # Prefix-only equivalent, labels independently reconstructed from dictionary.
  with torch.no_grad():
   short=m(x[:,:16],trace=True)[1][-1]['memory'];assert torch.allclose(tr[1]['memory'],short,atol=1e-5,rtol=1e-5)
   for r in rr:assert [explicit(r)[e] for e in [r['q'],r['other']]]==r['initial_values']
  # Exact persisted optimizer/RNG/cursor/order resume of this unchanged initial-only loss.
  m,d,o,rng=T.setup();hist=[T.update(m,d,o,rng,rr,'A') for _ in range(3)];T.save(R/'results'/f'{cond}-resume.pt',m,d,o,rng,rr,'A',3)
  hist.extend(T.update(m,d,o,rng,rr,'A') for _ in range(3));final=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state(),random.getstate()))
  n,e,p,s,step=T.restore(R/'results'/f'{cond}-resume.pt',rr,'A');tail=[T.update(n,e,p,s,rr,'A') for _ in range(step,6)]
  assert I.equal(final,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state(),random.getstate()));assert hist[3:]==tail
  report[cond]=dict(pass_all=True,resume_exact=True,updates=6,cut=3,gradient_norms=grads)
 assert visibility['same']['last_write_keys']==visibility['separate']['last_write_keys'];dump('frequencies.json',freq);dump('visibility.json',visibility);dump('certification.json',report)

def history():
 root=R.parent.parent/'cryo-two-bindings-v1/two-bindings';return [(str(p),T.sha(p)) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in str(p)]
def evaluate(m,d,rr):
 ev,states=T.evaluate(m,d,rr)
 for group in ev['metrics'].values():
  for stage in ['initial','post','retained']:group[stage]['product_marginals']=group[stage]['A_accuracy']*group[stage]['B_accuracy']
 return ev,states

def main():
 (R/'results').mkdir(exist_ok=False);old=history();dump('historical-before.json',old)
 datasets={c:data(c) for c in ['same','separate']}
 dump('protocol.json',dict(config=CONFIG,objective='CE_response + .1 CE_initial_only',supervised_chunk_train=1,supervised_chunk_dev=3,conditions=['same','separate'],source_commit='1376df2',torch=str(torch.__version__)))
 for c,rr in datasets.items():dump(c+'-train.json',rr);dump(c+'-dev.json',data(c,True))
 positive();print('POSITIVE CONTROL PASS',flush=True);certify(datasets);print('ALL CONTRACTS PASS',flush=True)
 for c,rr in datasets.items():
  m,d,o,rng=T.setup();T.save(R/'results'/f'{c}-initial.pt',m,d,o,rng,rr,'A',0);logs=[];t=time.monotonic()
  for step in range(150):
   logs.append(T.update(m,d,o,rng,rr,'A'))
   if step%25==0:print(c,step,logs[-1]['initial_ce'],flush=True)
  seconds=time.monotonic()-t;T.save(R/'results'/f'{c}-150.pt',m,d,o,rng,rr,'A',150);dump(c+'-curves.json',logs)
  for name,rows in [('train',rr),('dev',data(c,True))]:
   ev,states=evaluate(m,d,rows);ev['training_seconds']=seconds;dump(f'{c}-{name}-evaluation.json',ev);torch.save(dict(states=states,ids=[r['id'] for r in rows],stage_order=['after_both','neutral_later','before_query']),R/'results'/f'{c}-{name}-states.pt');print(c,name,ev['metrics']['all']['initial']['joint_accuracy'],flush=True)
 assert old==history();dump('historical-preservation.json',dict(unchanged=True,files=len(old)))
if __name__=='__main__':main()
