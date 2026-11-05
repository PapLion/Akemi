import unittest,torch,sys,io,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from models import Config,CryoNext,affine_scan,causal_loss

torch.set_num_threads(1)
class Contracts(unittest.TestCase):
 def setUp(self):torch.manual_seed(111)
 def model(self,kind='event',**kw):return CryoNext(Config(vocab=64,width=16,layers=1,chunk=4,slots=3,key_dim=4,kind=kind,**kw))
 def test_future_train_eval(self):
  for kind in ['event','delta','b0','b0_full']:
   for train in [True,False]:
    m=self.model(kind);m.train(train);x=torch.randint(1,60,(2,13));y=x.clone();y[:,7:]=torch.randint(1,60,(2,6))
    torch.testing.assert_close(m(x).logits[:,:7],m(y).logits[:,:7],atol=2e-5,rtol=2e-4)
 def test_backward_has_no_future_activation_dependency(self):
  for kind in ['event','delta','b0','b0_full']:
   m=self.model(kind);captured=[]
   def hook(module,args,out):out.retain_grad();captured.append(out)
   handle=m.emb.register_forward_hook(hook);x=torch.randint(1,60,(1,13));m(x).logits[:,:7].square().sum().backward();handle.remove()
   self.assertEqual(float(captured[0].grad[:,7:].abs().max()),0.)
 def test_sessions_and_actual_candidate_accounting(self):
  m=self.model('event');x=torch.randint(1,60,(2,16));first=m(x[:,:4],session_id=('a','b'))
  with self.assertRaises(ValueError):m(x[:,4:8],state=first.state,session_id=('b','a'))
  with self.assertRaises(ValueError):m(x[:,4:8],state=first.state)
  valid=torch.ones_like(x,dtype=torch.bool);valid[0,5:]=False
  out=m(x,valid=valid)
  self.assertEqual(out.stats['candidate_slots_executed'],2*4*m.cfg.slots)
  self.assertLess(out.stats['candidate_slots_eligible'],out.stats['candidate_slots_executed'])
 def test_batch_documents_and_padding(self):
  for kind in ['event','delta','b0','b0_full']:
   m=self.model(kind);x=torch.randint(1,60,(2,11));doc=torch.tensor([[0]*5+[1]*6,[8]*3+[9]*8]);valid=torch.ones_like(x,dtype=torch.bool)
   a=m(x,doc,valid).logits
   for row in range(2):
    torch.testing.assert_close(a[row],m(x[row:row+1],doc[row:row+1]).logits[0],atol=2e-5,rtol=2e-4)
    for d in doc[row].unique():
     mask=doc[row]==d;torch.testing.assert_close(a[row,mask],m(x[row:row+1,mask]).logits[0],atol=2e-5,rtol=2e-4)
   valid[:,-2:]=False;x2=x.clone();x2[:,-2:]=1
   torch.testing.assert_close(m(x,doc,valid).logits[:,:-2],m(x2,doc,valid).logits[:,:-2])
 def test_continuation_and_cross_boundary_grad(self):
  for kind in ['event','delta']:
   m=self.model(kind);x=torch.randint(1,60,(1,12));whole=m(x);first=m(x[:,:8],session_id="a");second=m(x[:,8:],state=first.state,session_id="a")
   torch.testing.assert_close(whole.logits[:,8:],second.logits,atol=2e-5,rtol=2e-4)
   first.state.memory.retain_grad();second.logits.square().mean().backward();self.assertGreater(first.state.memory.grad.abs().sum().item(),0)
   with self.assertRaises(ValueError):m(x[:,4:8],state=m(x[:,:3],session_id="a").state,session_id="a")
 def test_memory_effect_and_real_skip(self):
  for kind in ['event','delta']:
   m=self.model(kind);x=torch.randint(1,60,(1,12));first=m(x[:,:4],session_id="a");state=copy.copy(first.state);state.memory=state.memory+1
   self.assertGreater((m(x[:,4:8],state=state,session_id="a").logits-m(x[:,4:8],state=first.state,session_id="a").logits).abs().max().item(),1e-7)
  m=self.model();m.eval();m.cfg.hard_threshold=1.0;o=m(torch.randint(1,60,(1,8)),hard=True)
  self.assertEqual(o.stats['candidate_slots_executed'],0);self.assertGreater(o.stats['candidate_slots_eligible'],0)
 def test_optimizer_and_resume(self):
  for kind in ['event','delta','b0','b0_full']:
   m=self.model(kind);opt=torch.optim.AdamW(m.parameters(),lr=.001,foreach=False);x=torch.randint(1,60,(2,12));params=dict(m.named_parameters());before={n:p.detach().clone() for n,p in params.items()}
   for _ in range(2):
    opt.zero_grad();loss=causal_loss(m(x).logits,x);loss.backward()
    for n,p in params.items():self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n);self.assertGreater(p.grad.abs().sum().item(),0,n)
    opt.step()
   for n,p in params.items():self.assertFalse(torch.equal(before[n],p),n)
   self.assertEqual({id(p) for g in opt.param_groups for p in g['params']},{id(p) for p in m.parameters()})
   f=io.BytesIO();torch.save({'model':m.state_dict(),'opt':opt.state_dict(),'rng':torch.get_rng_state(),'update':2,'cursor':24},f);f.seek(0);saved=torch.load(f,weights_only=True)
   n=self.model(kind);n.load_state_dict(saved['model'],strict=True);other=torch.optim.AdamW(n.parameters(),lr=.001,foreach=False);other.load_state_dict(saved['opt'])
   for model,optimizer in [(m,opt),(n,other)]:
    torch.set_rng_state(saved['rng']);optimizer.zero_grad();causal_loss(model(x).logits,x).backward();optimizer.step()
   for a,b in zip(m.parameters(),n.parameters()):self.assertTrue(torch.equal(a,b))
 def test_delta_scan_values_and_gradients(self):
  a=torch.randn(2,7,4,4,dtype=torch.double,requires_grad=True)*.1;b=torch.randn(2,7,4,3,dtype=torch.double,requires_grad=True);initial=torch.randn(2,4,3,dtype=torch.double)
  states=[];s=initial
  for i in range(7):s=a[:,i]@s+b[:,i];states.append(s)
  seq=torch.stack(states,1);par=affine_scan(a,b,initial);torch.testing.assert_close(seq,par,atol=1e-10,rtol=1e-10)
  gs=torch.autograd.grad(seq.square().sum(),(a,b),retain_graph=True);gp=torch.autograd.grad(par.square().sum(),(a,b))
  for x,y in zip(gs,gp):torch.testing.assert_close(x,y,atol=1e-9,rtol=1e-9)
  m=self.model('delta');x=torch.randint(1,60,(2,13));doc=torch.tensor([[0]*7+[1]*6,[0]*13]);u=m(x,doc);v=m(x,doc,parallel=True)
  torch.testing.assert_close(u.logits,v.logits,atol=2e-5,rtol=2e-4)
  g1=torch.autograd.grad(u.logits.square().sum(),tuple(m.parameters()));g2=torch.autograd.grad(v.logits.square().sum(),tuple(m.parameters()))
  for a,b in zip(g1,g2):torch.testing.assert_close(a,b,atol=3e-6,rtol=2e-3)
 def test_always_write_unused_signals_frozen(self):
  m=self.model('event',ablation='always_write')
  self.assertTrue(all(not p.requires_grad for p in m.signals.parameters()))
 def test_loss_boundaries(self):
  logits=torch.randn(1,6,64);ids=torch.randint(1,60,(1,6));doc=torch.tensor([[0,0,0,1,1,1]]);valid=torch.tensor([[1,1,1,1,1,0]],dtype=torch.bool)
  loss=causal_loss(logits,ids,doc,valid);expected=torch.nn.functional.cross_entropy(logits[0,[0,1,3]],ids[0,[1,2,4]])
  torch.testing.assert_close(loss,expected)
 def test_sft_target_mask_and_empty_targets(self):
  logits=torch.randn(1,6,64);ids=torch.randint(1,60,(1,6));doc=torch.tensor([[0,0,0,1,1,1]]);target=torch.tensor([[0,0,1,1,0,1]],dtype=torch.bool)
  torch.testing.assert_close(causal_loss(logits,ids,doc,target_mask=target),torch.nn.functional.cross_entropy(logits[0,[1,4]],ids[0,[2,5]]))
  with self.assertRaises(ValueError):causal_loss(logits,ids,target_mask=torch.zeros_like(ids,dtype=torch.bool))
 def test_chunks32_64(self):
  for c in [32,64]:
   for kind in ['event','delta']:
    m=CryoNext(Config(vocab=64,width=16,layers=1,chunk=c,slots=3,key_dim=4,kind=kind));x=torch.randint(1,60,(1,c*2));o=m(x);self.assertEqual(o.logits.shape,(1,c*2,64));causal_loss(o.logits,x).backward()
if __name__=='__main__':unittest.main()
