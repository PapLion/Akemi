import sys,unittest,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from variants import build,VARIANTS
from hybrid import build_hybrid
class TrainingMasks(unittest.TestCase):
 def cases(self):
  return [(a,build(a,17,width=16)) for a in VARIANTS]+[(a,build_hybrid(a,17,width=16)) for a in ['event_fast','delta_fast']]
 def test_prefix_loss_has_zero_future_activation_gradient(self):
  for arm,m in self.cases():
   saved=[];hook=m.emb.register_forward_hook(lambda mod,args,out:saved.append(out));x=torch.randint(1,120,(1,16));z=m(x);g=torch.autograd.grad(z[:,:7].square().sum(),saved[0])[0];hook.remove();self.assertEqual(g[:,7:].abs().sum().item(),0,arm)
 def test_padding_gap_resets_same_document_and_zeroes_output(self):
  for arm,m in self.cases():
   x=torch.randint(1,120,(1,20));v=torch.ones_like(x,dtype=torch.bool);v[:,5:8]=False;y=m(x,valid=v)
   self.assertEqual(y[:,5:8].abs().sum().item(),0,arm);torch.testing.assert_close(y[:,8:],m(x[:,8:]),atol=2e-5,rtol=2e-4)
if __name__=='__main__':unittest.main()
