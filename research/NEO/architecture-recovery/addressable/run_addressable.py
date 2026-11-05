import json,time,copy,random,collections,hashlib,resource
from pathlib import Path
import torch
import torch.nn.functional as F
import address_model as A
T=A.T;C=A.C;P=A.P;O=Path(__file__).parent/'results'
torch.set_num_threads(1)
def dump(n,x):T.dump(O/n,x)
def controls():
 # Diagnostic oracle one-hot associations; no use inside learned model.
 x=torch.zeros(32,8);y=[];entities=[]
 for a in range(4):
  for b in range(4):
   for e in range(2):
    i=len(y);x[i,a]=1;x[i,4+b]=1;y.append([a,b][e]);entities.append(e)
 y=torch.tensor(y);e=torch.tensor(entities)
 torch.manual_seed(202);w=torch.nn.Parameter(torch.randn(2,8,4)*.02);o=torch.optim.AdamW([w],lr=.03,weight_decay=0.)
 curve=[]
 for _ in range(100):
  o.zero_grad();z=(x[:,None]@w[e]).squeeze(1);l=F.cross_entropy(z,y);l.backward();o.step();curve.append(float(l.detach()))
 acc=float(((x[:,None]@w[e]).squeeze(1).argmax(-1)==y).float().mean());assert acc==1
 # Independent explicit addressing controls, all 16 pairs queried both ways.
 def exact(wrongkey=False,wrongvalue=False):
  correct=0
  for a in range(4):
   for b in range(4):
    state={0:(a+wrongvalue)%4,1:(b+wrongvalue)%4}
    for q in range(2):correct+=state[1-q if wrongkey else q]==[a,b][q]
  return correct/32
 dump('explicit-controls.json',dict(oracle=exact(),learned_reader=acc,reader_ce=float(l.detach()),curve=curve,wrong_key=exact(True),wrong_value=exact(False,True),scope='diagnostic explicit representations, not Cryo learning'))

def certify(rows):
 result={};m,d,o,rng=A.setup();x=torch.tensor([r['ids'] for r in rows[:8]])
 pars=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];ops=[p for g in o.param_groups for p in g['params']]
 assert len(ops)==len(set(map(id,ops)))==len(pars) and set(map(id,ops))==set(map(id,pars))
 for train in [True,False]:
  m.train(train);y,tr=m(x,trace=True)
  for cut in [4,8,12,16,24,32,48]:
   xx=x.clone();xx[:,cut:]=120;z=m(xx);assert torch.equal(y[:,:cut],z[:,:cut])
  assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-5,rtol=1e-5)
  joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1)
  assert torch.allclose(m(joined,doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
  valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127
  assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
  for j in [1,3]:
   prefix=m(x[:,:8*(j+1)],trace=True)[1][-1]['memory'];assert torch.allclose(prefix,tr[j]['memory'],atol=1e-5,rtol=1e-5)
 o.zero_grad();lm,a,b,_,tr=T.losses(m,d,rows[:8]);a[0].backward()
 g={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None}
 assert g['core.address.weight']>0 and g['core.event_value.weight']>0
 assert all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
 result['aux_gradients']=g
 m,d,o,rng=A.setup();logs=[T.update(m,d,o,rng,rows,'A') for _ in range(3)];A.save(O/'resume-check.pt',m,d,o,rng,rows,3)
 logs.extend(T.update(m,d,o,rng,rows,'A') for _ in range(3));end=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state(),random.getstate()))
 n,e,p,s,step=A.restore(O/'resume-check.pt',rows);tail=[T.update(n,e,p,s,rows,'A') for _ in range(step,6)]
 assert A.I.equal(end,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state(),random.getstate())) and logs[3:]==tail
 result.update(causal_train_eval=True,padding=True,document_reset=True,batch_independent=True,prefix_memory=True,optimizer_coverage=True,exact_resume_3_plus_3=True)
 dump('certification.json',result)

def train(name,rows):
 m,d,o,rng=A.setup();logs=[];t=time.monotonic()
 for step in range(300):
  logs.append(T.update(m,d,o,rng,rows,'A'))
  if (step+1)%100==0:print(name,step+1,logs[-1]['initial_accuracy'],flush=True)
 seconds=time.monotonic()-t;A.save(O/f'{name}.pt',m,d,o,rng,rows,300);dump(f'{name}-curve.json',logs)
 ev,states=T.evaluate(m,d,rows);dump(f'{name}-train.json',ev);torch.save(states,O/f'{name}-states.pt')
 dump(f'{name}-cost.json',dict(seconds=seconds,parameters=sum(p.numel() for p in m.parameters()),trainable=sum(p.numel() for p in m.parameters() if p.requires_grad),aux_parameters=sum(p.numel() for p in d.parameters()),rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,updates=300))
 return m,d,ev

def main():
 O.mkdir(exist_ok=True);assert not (O/'microfit.pt').exists()
 dump('protocol.json',dict(updates=300,seed=17,batch=8,lr=.003,clip=1.,lambda_aux=.1,microfit_gate='both marginal >= .9, joint >= .9, mean CE < .5',main_gate='only after microfit',key_seed=707,decoder_seed=101,precision='CPU FP32',normal_route='shared learned addressing, no auxiliary decoder',state=[8,32],format='observed four-ID records, accepted =/! only',limitations='record-aware input embedding key branch, not generic natural-language event extraction'))
 controls();rows=C.data('same');micro=[r for r in rows if r['q']=='A'];dump('microfit-data.json',micro);dump('train-data.json',rows);dump('dev-data.json',C.data('same',True))
 counts=collections.Counter((r['q'],r['other'],*r['initial_values']) for r in rows);assert set(counts.values())=={2};dump('frequencies.json',[dict(key=list(k),count=v) for k,v in counts.items()])
 certify(rows);print('CONTRACTS PASS',flush=True)
 m,d,ev=train('microfit',micro);met=ev['metrics']['all']['initial'];passed=min(met['A_accuracy'],met['B_accuracy'],met['joint_accuracy'])>=.9 and (met['ce_A']+met['ce_B'])/2<.5
 dump('microfit-gate.json',dict(passed=passed,metrics=met))
 if not passed:print('MICROFIT FAIL; MAIN NOT EXECUTED',flush=True);return
 m,d,ev=train('main',rows)
 for name,rr in [('dev',C.data('same',True)),('corrections',T.data(True))]:
  ev,states=T.evaluate(m,d,rr);dump(f'main-{name}.json',ev);torch.save(states,O/f'main-{name}-states.pt')
 print('MAIN COMPLETE',flush=True)
if __name__=='__main__':main()
