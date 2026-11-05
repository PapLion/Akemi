import sys,unittest,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from capacity_control import build_control
from variants import build
class Control(unittest.TestCase):
 def test_active_capacity_and_equivalent_input(self):
  h=build('intact',17);b=build_control(17);a=sum(p.numel() for p in h.parameters() if p.requires_grad);n=sum(p.numel() for p in b.parameters() if p.requires_grad);self.assertLess(abs(a-n)/a,.02)
  torch.testing.assert_close(h.emb.weight,b.emb.weight,rtol=0,atol=0)
  x=torch.randint(1,120,(2,16));y=x.clone();y[:,8:]+=1;torch.testing.assert_close(b(x)[:,:8],b(y)[:,:8],rtol=2e-4,atol=2e-5)
  b(x)[:,-1].sum().backward();self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum()>0 for p in b.parameters()))
if __name__=='__main__':unittest.main()
