import sys,unittest,copy,io,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
import network
class ModelTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(1);torch.manual_seed(5);self.x=torch.randint(40,90,(2,32));self.doc=torch.zeros_like(self.x)
 def test_future_and_outside_window_access(self):
  # Removing block isolation would expose old prefix even through two attention layers.
  for arm in network.ARMS:
   m=network.build(arm,17);a=m(self.x);z=self.x.clone();z[:,20:]=(z[:,20:]+1)%100
   torch.testing.assert_close(a[:,:20],m(z)[:,:20],atol=2e-5,rtol=2e-4)
   if arm in ['no_ice','transformer']:
    z=self.x.clone();z[:,:24]=(z[:,:24]+1)%100
    self.assertTrue(torch.equal(a[:,-1],m(z)[:,-1]))
 def test_reset_batch_and_padding(self):
  for arm in network.ARMS:
   m=network.build(arm,17);doc=self.doc.clone();doc[:,16:]=1
   a=m(self.x,doc);b=m(self.x[:,16:]);torch.testing.assert_close(a[:,16:],b,atol=2e-5,rtol=2e-4)
   torch.testing.assert_close(a[:1],m(self.x[:1],doc[:1]),atol=2e-5,rtol=2e-4)
   valid=torch.ones_like(self.x,dtype=torch.bool);valid[:,15]=False;c=m(self.x,self.doc,valid);self.assertTrue(torch.equal(c[:,15],torch.zeros_like(c[:,15])))
 def test_full_reference_equivalence(self):
  for arm in network.ARMS:
   m=network.build(arm,17,window=0)
   torch.testing.assert_close(m(self.x),m.reference(self.x),atol=2e-5,rtol=2e-4)
 def test_gradients_optimizer_and_resume(self):
  for arm in network.ARMS:
   m=network.build(arm,17);op=network.optimizer(m);params=[p for p in m.parameters() if p.requires_grad];self.assertEqual(len({id(p) for g in op.param_groups for p in g['params']}),len(params));before=[p.detach().clone() for p in params]
   def step(mm,oo,x):
    oo.zero_grad();torch.nn.functional.cross_entropy(mm(x)[:,-1],torch.tensor([48,49])).backward();torch.nn.utils.clip_grad_norm_(mm.parameters(),1.,error_if_nonfinite=True);oo.step()
   for _ in range(2):step(m,op,self.x)
   self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all() for p in params));self.assertTrue(all(not torch.equal(a,b) for a,b in zip(before,params)))
   buf=io.BytesIO();torch.save({'model':m.state_dict(),'optimizer':op.state_dict(),'rng':torch.get_rng_state()},buf);buf.seek(0);s=torch.load(buf,weights_only=True)
   n=network.build(arm,17);n.load_state_dict(s['model'],strict=True);oo=network.optimizer(n);oo.load_state_dict(s['optimizer'])
   torch.set_rng_state(s['rng']);step(m,op,self.x.flip(0));torch.set_rng_state(s['rng']);step(n,oo,self.x.flip(0));self.assertTrue(all(torch.equal(a,b) for a,b in zip(m.parameters(),n.parameters())))
 def test_memory_intervention_and_cross_chunk_gradient(self):
  for arm in ['event_fast','delta_fast']:
   m=network.build(arm,17);out,trace=m(self.x,trace=True);torch.nn.functional.cross_entropy(out[:,-1],torch.tensor([48,49])).backward()
   self.assertGreater(sum(float(p.grad.abs().sum()) for n,p in m.named_parameters() if 'memory_head' in n and p.grad is not None),0)
   self.assertTrue(any(float(t['memory'].grad.abs().sum())>0 for t in trace[:-1] if t['memory'].grad is not None))
   suppressed=m(self.x,intervention='reset');self.assertFalse(torch.equal(out[:,-1],suppressed[:,-1]))
if __name__=='__main__':unittest.main()
