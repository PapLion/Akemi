import sys,unittest,copy,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from variants import build
from experiment import optimizer
class Equivalence(unittest.TestCase):
 def test_chunk1_logits_gradients_updates(self):
  a=build('intact',17,width=16);b=build('chunk2',17,width=16);b.write_chunk=1
  x=torch.randint(1,120,(2,12));doc=torch.tensor([[0]*5+[1]*7,[0]*12]);valid=torch.ones_like(x,dtype=torch.bool);valid[1,-2:]=False
  oa,ob=optimizer(a),optimizer(b)
  for _ in range(3):
   for m,o in [(a,oa),(b,ob)]:o.zero_grad();torch.nn.functional.cross_entropy(m(x,doc,valid)[:,9],torch.tensor([48,49])).backward()
   for (n,p),(nn,q) in zip(a.named_parameters(),b.named_parameters()):
    self.assertEqual(n,nn);torch.testing.assert_close(p.grad,q.grad,rtol=2e-3,atol=3e-6)
   oa.step();ob.step()
   torch.testing.assert_close(a(x,doc,valid),b(x,doc,valid),rtol=2e-4,atol=2e-5)
 def test_common_foreground_and_tied_head(self):
  a=build('intact',17)
  for arm in ['transformer','no_ice','no_filter','depth1','event','delta','detach','chunk2']:
   b=build(arm,17)
   for n,p in a.named_parameters():
    if n.startswith(('emb.','blocks.','slow_norm.')):torch.testing.assert_close(p,dict(b.named_parameters())[n],rtol=0,atol=0)
 def test_chunk2_backprop_crosses_pair_boundary(self):
  m=build('chunk2',17,width=16);saved=[];original=m.hidden
  def hidden(*args):
   h=original(*args);saved.append(h);return h
  m.hidden=hidden;x=torch.randint(1,120,(1,8));loss=m(x)[:,-1].square().sum();g=torch.autograd.grad(loss,saved[0])[0]
  self.assertGreater(g[0,1].norm().item(),0)
if __name__=='__main__':unittest.main()
