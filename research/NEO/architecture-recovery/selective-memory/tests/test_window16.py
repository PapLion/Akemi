import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,network
class Window16Tests(unittest.TestCase):
 def test_prefix_cannot_reach_query_without_declared_memory(self):
  torch.set_num_threads(1);x=torch.arange(32)[None]+40;y=x.clone();y[:,:16]+=40
  for arm in network.ARMS:
   for train in [True,False]:
    m=network.build(arm,17,window=16);m.train(train);a=m(x);b=m(y)
    if arm in ['no_ice','transformer']:self.assertTrue(torch.equal(a[:,-1],b[:,-1]))
    z=x.clone();z[:,24:]+=30;torch.testing.assert_close(a[:,:24],m(z)[:,:24],atol=2e-5,rtol=2e-4)
  for arm in ['no_ice','transformer']:
   m=network.build(arm,17,window=16);captured=[]
   def hook(module,args,out):out.retain_grad();captured.append(out)
   h=m.core.emb.register_forward_hook(hook);m(x)[:,-1,48].backward();h.remove();self.assertEqual(float(captured[0].grad[:,:16].abs().sum()),0)
if __name__=='__main__':unittest.main()
