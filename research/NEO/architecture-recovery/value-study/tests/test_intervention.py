import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,extract,data_panel,intervene
class InterventionTests(unittest.TestCase):
 def test_sham_and_recipient_foreground(self):
  torch.set_num_threads(1);x=torch.tensor([r['ids'] for r in data_panel.generate('dev')[:2]])
  for arm in ['intact','event_fast','delta_fast']:
   m,_=extract.load_model(arm,17)
   with torch.no_grad():
    f=extract.observe(m,x);base=m(x);sham=intervene.injected(m,x,f['states'][:,6]);self.assertTrue(torch.equal(base,sham),arm)
if __name__=='__main__':unittest.main()
