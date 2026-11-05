import unittest,sys,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,network,learn,panel
import diagnose
class TraceAndRandomTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(1)
 def test_historical_trace_matches_regular_forward(self):
  m=network.build('intact',17,16);x=torch.tensor([panel.load('train')[0]['ids']]);expected=m(x);actual,trace=m(x,trace=True)
  self.assertEqual(len(trace),64);self.assertTrue(torch.equal(expected,actual))
 def test_random_budget_is_part_of_checkpoint_identity(self):
  m=network.build('delta_fast',17,16,'random',random_budget=.37)
  self.assertEqual(m.config()['random_budget'],.37)
 def test_random_counterfactual_uses_common_rng_without_altering_training_rng(self):
  import copy
  m=network.build('delta_fast',17,16,'random',random_budget=.37);rr=panel.load('iid')[:16];changed=copy.deepcopy(rr);changed[0]=panel.counterfactual(changed[0],'valid');rng=torch.get_rng_state().clone()
  a=diagnose.predictions(m,rr);b=diagnose.predictions(m,changed);self.assertEqual(a[1:],b[1:]);self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(a,diagnose.predictions(m,rr))
 def test_actual_runner_random_resume(self):
  old=learn.R
  with tempfile.TemporaryDirectory() as tmp:
   learn.R=Path(tmp);(learn.R/'results').mkdir()
   try:
    rows=learn.micro_panel(panel.load('train'))
    learn.train('delta_fast',17,'continuous',4,16,'random',rows,random_budget=.37)
    learn.train('delta_fast',17,'interrupted',2,16,'random',rows,random_budget=.37)
    learn.train('delta_fast',17,'interrupted',4,16,'random',rows,random_budget=.37)
    a=torch.load(learn.R/'results/continuous/delta_fast-random-w16-17.pt',weights_only=True);b=torch.load(learn.R/'results/interrupted/delta_fast-random-w16-17.pt',weights_only=True)
    for k in a['model']:self.assertTrue(torch.equal(a['model'][k],b['model'][k]),k)
    for k in ['sampler_rng','cursor','step','config']:self.assertEqual(a[k],b[k])
    self.assertTrue(torch.equal(a['torch_rng'],b['torch_rng']))
    for k in a['optimizer']['state']:
     for n in ['step','exp_avg','exp_avg_sq']:self.assertTrue(torch.equal(a['optimizer']['state'][k][n],b['optimizer']['state'][k][n]),n)
   finally:learn.R=old
if __name__=='__main__':unittest.main()
