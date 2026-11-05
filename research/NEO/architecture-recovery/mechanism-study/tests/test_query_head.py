import sys,unittest,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from variants import build
from query_head import answer_only
class QueryHead(unittest.TestCase):
 def test_answer_logits_and_all_parameter_gradients(self):
  a=build('no_ice',17,width=16);b=build('no_ice',17,width=16);x=torch.randint(1,120,(2,16));y=torch.tensor([48,49])
  la=a(x)[:,-1];lb=answer_only(b,x);torch.testing.assert_close(la,lb,rtol=2e-4,atol=2e-5)
  for z in [la,lb]:torch.nn.functional.cross_entropy(z,y).backward()
  for (n,p),(nn,q) in zip(a.named_parameters(),b.named_parameters()):
   if p.requires_grad:torch.testing.assert_close(p.grad,q.grad,rtol=2e-3,atol=3e-6)
 def test_cannot_apply_reduction_to_memory_model(self):
  with self.assertRaises(ValueError):answer_only(build('intact',17,width=16),torch.ones(1,8,dtype=torch.long))
if __name__=='__main__':unittest.main()
