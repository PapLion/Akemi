import unittest,torch
from vendor.cryo_historical import CryoTiny
class HistoricalControl(unittest.TestCase):
 def test_frozen_control_causality_and_document_batch_isolation(self):
  torch.manual_seed(17);m=CryoTiny(v=64,d=16,layers=1,dropout=0.)
  x=torch.randint(1,60,(2,12));other=x.clone();other[:,7:]=torch.randint(1,60,(2,5))
  for train in [True,False]:
   m.train(train);torch.testing.assert_close(m(x)[:,:7],m(other)[:,:7],atol=2e-5,rtol=2e-4)
  docs=torch.tensor([[0]*5+[1]*7,[0]*12]);out=m(x,docs)
  torch.testing.assert_close(out[0,5:],m(x[:1,5:])[0],atol=2e-5,rtol=2e-4)
  torch.testing.assert_close(out[1],m(x[1:])[0],atol=2e-5,rtol=2e-4)
