import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,extract,data_panel
class ExtractionTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(1)
 def test_extraction_preserves_predictions_and_causality(self):
  rr=data_panel.generate('dev')[:2];x=torch.tensor([r['ids'] for r in rr]);changed=x.clone();changed[:,48:]=ord('z')
  for arm,mode in [('intact','normal'),('event_fast','normal'),('delta_fast','normal'),('delta_fast','always'),('delta_fast','random')]:
   m,_=extract.load_model(arm,17,mode)
   torch.manual_seed(991)
   with torch.no_grad():y=m(x)[:,-1].argmax(-1)
   torch.manual_seed(991);a=extract.observe(m,x);torch.manual_seed(991);b=extract.observe(m,changed)
   self.assertTrue(torch.equal(y,a['prediction']),arm)
   self.assertTrue(torch.equal(a['states'][:,:6],b['states'][:,:6]),arm)
   self.assertTrue(all(not p.requires_grad for p in m.parameters()))
if __name__=='__main__':unittest.main()
