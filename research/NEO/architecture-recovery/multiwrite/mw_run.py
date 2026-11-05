from mw_model import *
import json,copy,random,collections,resource
R=Path(__file__).resolve().parent
OUT=R/'results'
def dump(n,x):T.dump(OUT/n,x)
def certify():
 rows=C.data('same');batch=rows[::20];x=torch.tensor([r['ids'] for r in batch]);ref,rd,_,_=T.setup();m,d,o,rng=setup(1)
 a,ta=ref(x,trace=True);b,tb=m(x,trace=True);assert torch.equal(a,b)
 la=T.losses(ref,rd,batch);lb=T.losses(m,d,batch);(la[0]+.1*la[1][0]).backward();(lb[0]+.1*lb[1][0]).backward()
 for (n,p),(nn,q) in zip(ref.named_parameters(),m.named_parameters()):
  assert n==nn and ((p.grad is None and q.grad is None) or torch.equal(p.grad,q.grad))
 report=dict(k1_logits_gradients_exact=True)
 m,d,o,rng=setup(2);base,_,_,_=T.setup()
 for key,value in base.state_dict().items():
  if 'summary_query' not in key:assert torch.equal(value,m.state_dict()[key])
 assert m.core.memory_head._read.__func__ is base.core.memory_head._read.__func__
 params=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];op=[p for g in o.param_groups for p in g['params']];assert len(params)==len(op)==len(set(map(id,op))) and set(map(id,params))==set(map(id,op))
 for mode in [False,True]:
  m.train(mode);y,tr=m(x,trace=True);xx=x.clone();xx[:,16:]=120;z,tt=m(xx,trace=True);assert torch.equal(y[:,:16],z[:,:16]);assert torch.equal(tr[1]['memory'],tt[1]['memory']);assert torch.equal(T.stage(m,d,batch,tr,0)[0],T.stage(m,d,batch,tt,0)[0])
  assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-6,rtol=1e-5)
  joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1);assert torch.allclose(m(joined,doc=doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
  valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127;assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
 m.eval();lm,a,b,logits,tr=T.losses(m,d,batch);a[0].backward();qg=m.core.memory_head.summary_query.grad;assert torch.isfinite(qg).all() and (qg.norm(dim=-1)>0).all();assert not torch.equal(qg[0],qg[1]);assert not torch.equal(tr[1]['candidates'][:,0],tr[1]['candidates'][:,1])
 # Both summaries react to actual changed input values; no oracle enters model API.
 with torch.no_grad():
  xx=x.clone();xx[:,10]=48+(xx[:,10]-48+1)%4;_,pert=m(xx,trace=True)
  dif=(tr[1]['candidates']-pert[1]['candidates']).norm(dim=-1);assert (dif.mean(0)>0).all()
  short=m(x[:,:16],trace=True)[1][-1]['memory'];assert torch.allclose(tr[1]['memory'],short,atol=1e-5,rtol=1e-5)
 # Exact recurrence continuation using recorded candidates, and gradient path through previous memory.
 t=tr[1];s=t['before']
 for i in range(2):s=delta_step(s,t['keys'][:,i],t['values'][:,i],.9+.09*t['controls'][:,i,:1],t['controls'][:,i,1:2],t['controls'][:,i,2:],2)
 assert torch.equal(s,t['memory']);assert tr[0]['memory'].grad is not None and tr[0]['memory'].grad.norm()>0
 report.update(candidate_gradient_norms=qg.norm(dim=-1).tolist(),value_perturbation_norms=dif.mean(0).tolist(),reader_unchanged=True,causal_train_eval=True,mask_reset_batch=True,continuation_recurrence=True,optimizer_exact=True)
 # Small disposable preflight; insist finite and net decline on fixed batch.
 m,d,o,rng=setup(2);fixed=batch
 losses=[]
 for step in range(20):
  o.zero_grad();lm,a,b,_,_=T.losses(m,d,fixed);loss=lm+.1*a[0];losses.append(float(loss.detach()));loss.backward();assert all(torch.isfinite(p.grad).all() for p in [*m.parameters(),*d.parameters()] if p.grad is not None);torch.nn.utils.clip_grad_norm_([*m.parameters(),*d.parameters()],1);o.step()
 assert losses[-1]<losses[0]
 report['preflight_losses']=losses
 # Full persisted 3+3 versus6 trajectory with new optimizer parameter shape.
 m,d,o,rng=setup(2);hist=[T.update(m,d,o,rng,rows,'A') for _ in range(3)];save(OUT/'resume.pt',m,d,o,rng,rows,2,3);hist.extend(T.update(m,d,o,rng,rows,'A') for _ in range(3));final=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state(),random.getstate()))
 n,e,p,s,step=load(OUT/'resume.pt',rows,2);tail=[T.update(n,e,p,s,rows,'A') for _ in range(step,6)];assert I.equal(final,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state(),random.getstate())) and hist[3:]==tail
 report['resume_exact']=True;dump('certification.json',report)

def main():
 OUT.mkdir(exist_ok=False);dump('protocol.json',dict(arms={'A':[1,'same'],'B':[2,'same'],'C':[1,'separate']},updates=300,seed=17,batch=8,lr=.003,clip=1,lambda_aux=.1,additional_seed_gate='B exceeds A joint train and dev by >=10 percentage points AND B dev joint>=.5 AND strict swapped joint>=.25; fixed before outcomes',capacity_control='Not trained; +32 query parameters explicitly counted; compute/init not matched'))
 for layout in ['same','separate']:
  dump(layout+'-train.json',C.data(layout));dump(layout+'-dev.json',C.data(layout,True))
 certify();print('CERTIFICATION PASS',flush=True)
 for arm,K,condition in [('A',1,'same'),('B',2,'same'),('C',1,'separate')]:
  rows=C.data(condition);m,d,o,rng=setup(K);save(OUT/f'{arm}-initial.pt',m,d,o,rng,rows,K,0);logs=[];start=time.monotonic()
  for step in range(300):
   logs.append(T.update(m,d,o,rng,rows,'A'))
   if step==149:save(OUT/f'{arm}-150.pt',m,d,o,rng,rows,K,150)
   if step%50==0:print(arm,step,logs[-1]['initial_ce'],flush=True)
  seconds=time.monotonic()-start;save(OUT/f'{arm}-300.pt',m,d,o,rng,rows,K,300);dump(arm+'-curves.json',logs)
  dump(arm+'-resources.json',dict(seconds=seconds,seconds_per_update=seconds/300,model_params=sum(p.numel() for p in m.parameters()),trainable_params=sum(p.numel() for p in m.parameters() if p.requires_grad),decoder_params=sum(p.numel() for p in d.parameters()),peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,note='RSS cumulative high-water mark; sequential process, not isolated per-arm peak'))
  for split,rr in [('train',rows),('dev',C.data(condition,True))]:
   ev,states=C.evaluate(m,d,rr);dump(f'{arm}-{split}-evaluation.json',ev);torch.save(dict(states=states,ids=[r['id'] for r in rr]),OUT/f'{arm}-{split}-states.pt');print(arm,split,ev['metrics']['all']['initial']['joint_accuracy'],flush=True)
if __name__=='__main__':main()
