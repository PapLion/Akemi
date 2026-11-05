import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,network
class AblationTests(unittest.TestCase):
 def test_no_read_equals_training_without_ice(self):
  torch.set_num_threads(1);x=torch.arange(64)[None]+40;target=torch.tensor([48])
  a=network.build('no_ice',17,16);oa=network.optimizer(a)
  for arm in ['event_fast','delta_fast']:
   # Independent reference trajectory per comparison, not a moving trained target.
   a=network.build('no_ice',17,16);oa=network.optimizer(a);b=network.build(arm,17,16,mode='no_read');ob=network.optimizer(b)
   for _ in range(3):
    torch.testing.assert_close(a(x),b(x),atol=2e-5,rtol=2e-4)
    for m,o in [(a,oa),(b,ob)]:
     o.zero_grad();torch.nn.functional.cross_entropy(m(x)[:,-1],target).backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1.);o.step()
   for n,p in a.core.named_parameters():
    if p.requires_grad:torch.testing.assert_close(p,dict(b.core.named_parameters())[n],atol=3e-5,rtol=2e-3)
 def test_always_write_removes_gate_only_not_memory(self):
  torch.set_num_threads(1);x=torch.arange(32)[None]+40
  for arm in ['event_fast','delta_fast']:
   m=network.build(arm,17,16,mode='always');y,tr=m(x,trace=True);self.assertTrue(all(torch.equal(r['write'],torch.ones_like(r['write'])) for r in tr));self.assertTrue(any(float(r['memory'].norm())>0 for r in tr));y[:,-1,48].backward()
   for n,p in m.named_parameters():
    if p.requires_grad:self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n)
if __name__=='__main__':unittest.main()
