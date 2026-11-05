import sys,unittest,copy,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybrid import build_hybrid
from variants import build
from experiment import optimizer
class HybridTests(unittest.TestCase):
 def test_causal_reset_batch_and_gradients(self):
  for arm in ['event_fast','delta_fast']:
   m=build_hybrid(arm,17,width=16);x=torch.randint(1,120,(2,17));y=x.clone();y[:,7:]+=1
   for train in [True,False]:m.train(train);torch.testing.assert_close(m(x)[:,:7],m(y)[:,:7],rtol=2e-4,atol=2e-5)
   doc=torch.tensor([[0]*5+[1]*12,[0]*17]);torch.testing.assert_close(m(x,doc)[0,5:],m(x[:1,5:])[0],rtol=2e-4,atol=2e-5)
   torch.testing.assert_close(m(x)[1],m(x[1:])[0],rtol=2e-4,atol=2e-5)
   torch.testing.assert_close(m(x[:,:7]),m(x)[:,:7],rtol=2e-4,atol=2e-5)
   op=optimizer(m);before={n:p.clone().detach() for n,p in m.named_parameters() if p.requires_grad};loss=torch.nn.functional.cross_entropy(m(x)[:,-1],torch.tensor([48,49]));loss.backward()
   for n,p in m.named_parameters():
    if p.requires_grad:self.assertIsNotNone(p.grad,(arm,n));self.assertTrue(torch.isfinite(p.grad).all(),(arm,n));self.assertGreater(p.grad.abs().sum().item(),0,(arm,n))
   op.step();self.assertTrue(all(not torch.equal(p,before[n]) for n,p in m.named_parameters() if p.requires_grad))
 def test_fast_weights_and_resume(self):
  for arm in ['event_fast','delta_fast']:
   a=build_hybrid(arm,17,width=16);ref=build('intact',17,width=16)
   for n,p in a.named_parameters():
    if n.startswith(('fast.','fast_norm.','read.','emb.','blocks.','slow_norm.')):torch.testing.assert_close(p,dict(ref.named_parameters())[n],rtol=0,atol=0)
   op=optimizer(a);x=torch.randint(1,120,(2,16));y=torch.tensor([48,49])
   for _ in range(2):op.zero_grad();torch.nn.functional.cross_entropy(a(x)[:,-1],y).backward();op.step()
   state=copy.deepcopy({'model':a.state_dict(),'opt':op.state_dict()});b=build_hybrid(arm,17,width=16);b.load_state_dict(state['model'],strict=True);ob=optimizer(b);ob.load_state_dict(state['opt'])
   for m,o in [(a,op),(b,ob)]:o.zero_grad();torch.nn.functional.cross_entropy(m(x)[:,-1],y).backward();o.step()
   for p,q in zip(a.parameters(),b.parameters()):torch.testing.assert_close(p,q,rtol=0,atol=0)
if __name__=='__main__':unittest.main()
