import unittest,sys,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from models import CryoNext,Config
from performance import region_instrumentation
class Profiling(unittest.TestCase):
 def test_instrumentation_preserves_values_and_gradients(self):
  for kind in ['event','delta']:
   torch.manual_seed(12);m=CryoNext(Config(vocab=64,width=16,layers=1,chunk=4,kind=kind));x=torch.randint(1,60,(1,12));a=m(x).logits;ga=torch.autograd.grad(a.sum(),tuple(m.parameters()))
   with region_instrumentation(m) as timings:b=m(x).logits;gb=torch.autograd.grad(b.sum(),tuple(m.parameters()))
   torch.testing.assert_close(a,b,atol=0,rtol=0)
   for u,v in zip(ga,gb):torch.testing.assert_close(u,v,atol=0,rtol=0)
   self.assertIn('hielo/read',timings)
if __name__=='__main__':unittest.main()
