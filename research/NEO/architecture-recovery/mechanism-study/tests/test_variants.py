"""Catch changed recurrence, future writes, missing gradients and broken restoration."""
import sys,unittest,torch,copy,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from variants import build,VARIANTS
from experiment import make_model
class Variants(unittest.TestCase):
 def test_historical_reference_exact(self):
  old=make_model('cryo_history',17,width=16);m=build('intact',17,width=16);x=torch.randint(1,120,(2,13))
  self.assertEqual(set(old.state_dict()),set(m.state_dict()))
  torch.testing.assert_close(old(x),m(x),rtol=0,atol=0)
 def test_causal_train_eval_and_resets(self):
  for arm in VARIANTS:
   m=build(arm,17,width=16);x=torch.randint(1,120,(2,15));y=x.clone();y[:,7:]+=1
   for train in [True,False]:
    m.train(train);torch.testing.assert_close(m(x)[:,:7],m(y)[:,:7],rtol=2e-4,atol=2e-5)
   d=torch.tensor([[0]*5+[1]*10,[0]*15]);out=m(x,d)
   torch.testing.assert_close(out[0,5:],m(x[:1,5:])[0],rtol=2e-4,atol=2e-5)
   torch.testing.assert_close(out[1],m(x[1:])[0],rtol=2e-4,atol=2e-5)
 def test_gradients_updates_and_resume(self):
  for arm in VARIANTS:
   m=build(arm,17,width=16);op=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,foreach=False);x=torch.randint(1,120,(2,16));y=torch.tensor([48,49]);before={n:p.detach().clone() for n,p in m.named_parameters() if p.requires_grad}
   for _ in range(2):
    op.zero_grad();loss=torch.nn.functional.cross_entropy(m(x)[:,-1],y);loss.backward()
    for n,p in m.named_parameters():
     if p.requires_grad:self.assertIsNotNone(p.grad,(arm,n));self.assertTrue(torch.isfinite(p.grad).all(),(arm,n));self.assertGreater(p.grad.abs().sum().item(),0,(arm,n))
    op.step()
   self.assertTrue(all(not torch.equal(p,before[n]) for n,p in m.named_parameters() if p.requires_grad),arm)
   ids=[id(p) for g in op.param_groups for p in g['params']];self.assertEqual(len(ids),len(set(ids)));self.assertEqual(set(ids),{id(p) for p in m.parameters() if p.requires_grad})
   state=copy.deepcopy({'model':m.state_dict(),'optimizer':op.state_dict(),'rng':torch.get_rng_state()});f=io.BytesIO();torch.save(state,f);f.seek(0);state=torch.load(f,weights_only=True)
   other=build(arm,17,width=16);other.load_state_dict(state['model'],strict=True);oo=torch.optim.AdamW([p for p in other.parameters() if p.requires_grad],lr=.003,foreach=False);oo.load_state_dict(state['optimizer'])
   for mm,o in [(m,op),(other,oo)]:torch.set_rng_state(state['rng']);o.zero_grad();torch.nn.functional.cross_entropy(mm(x)[:,-1],y).backward();o.step()
   for a,b in zip(m.parameters(),other.parameters()):torch.testing.assert_close(a,b,rtol=0,atol=0)
 def test_detach_changes_backward_not_forward(self):
  m=build('intact',17,width=16);n=build('detach',17,width=16);x=torch.randint(1,120,(1,16));torch.testing.assert_close(m(x),n(x),atol=0,rtol=0)
  gm=torch.autograd.grad(m(x)[:,-1].square().mean(),m.memory_init)[0]
  self.assertGreater(gm.abs().sum().item(),0);self.assertFalse(n.memory_init.requires_grad)
 def test_chunk1_is_original_and_partial_prefix_not_flushed(self):
  m=build('intact',17,width=16);n=build('chunk2',17,width=16);n.write_chunk=1;x=torch.randint(1,120,(1,13));torch.testing.assert_close(m(x),n(x),rtol=2e-4,atol=2e-5)
  n.write_chunk=2;torch.testing.assert_close(n(x[:,:7]),n(x)[:,:7],rtol=2e-4,atol=2e-5)
if __name__=='__main__':unittest.main()
