import unittest,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,data_panel
import value_probes as probes
import torch.nn.functional as F
class PersistenceTests(unittest.TestCase):
 def test_reload_decoder_and_normalizer(self):
  torch.set_num_threads(1);rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};data={s:F.one_hot(torch.tensor([r['current'] for r in rr]),4).float() for s,rr in rows.items()}
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'readout.pt';result,preds=probes.fit(data,rows,'value','linear',save_path=p);s=torch.load(p,weights_only=True);m=probes.Decoder(s['input_dim'],s['classes']);m.load_state_dict(s['model'],strict=True);x,e,y,_=probes.arrays(rows['dev'],data['dev'],'value');actual=m((x-s['mean'])/s['sd'],e).argmax(-1).tolist();self.assertEqual(actual,preds['dev']['prediction'])
if __name__=='__main__':unittest.main()
