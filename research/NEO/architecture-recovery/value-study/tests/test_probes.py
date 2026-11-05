import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,data_panel
import value_probes as probes
import torch.nn.functional as F
class ProbeTests(unittest.TestCase):
 def test_positive_and_presence_negative(self):
  torch.set_num_threads(1);rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};data={s:F.one_hot(torch.tensor([r['current'] for r in rr]),4).float() for s,rr in rows.items()};r,_=probes.fit(data,rows,'value','linear');self.assertEqual(r['splits']['dev']['accuracy'],1.)
  data={s:torch.tensor([[r['present']] for r in rr]).float() for s,rr in rows.items()};r,_=probes.fit(data,rows,'value','linear');self.assertEqual(r['splits']['dev']['accuracy'],.25)
 def test_decoder_does_not_change_features(self):
  torch.set_num_threads(1);rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};data={s:torch.randn(len(rr),4) for s,rr in rows.items()};old={s:x.clone() for s,x in data.items()};probes.fit(data,rows,'value','linear')
  for s in data:self.assertTrue(torch.equal(data[s],old[s]))
if __name__=='__main__':unittest.main()
