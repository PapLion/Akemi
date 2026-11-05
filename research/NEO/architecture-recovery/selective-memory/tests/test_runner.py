import unittest,sys,tempfile,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,learn,network,panel
class RunnerTests(unittest.TestCase):
 def test_evaluation_preserves_training_rng(self):
  m=network.build('event_fast',17,mode='random');before=torch.get_rng_state().clone();learn.evaluate(m,panel.load('train')[:2]);self.assertTrue(torch.equal(before,torch.get_rng_state()))
 def test_resume_preserves_sampler_and_full_optimizer(self):
  with tempfile.TemporaryDirectory() as tmp:
   old=learn.R;learn.R=Path(tmp);(learn.R/'results').mkdir()
   try:
    rows=learn.micro_panel(panel.load('train'))
    learn.train('no_ice',17,'continuous',4,rows=rows)
    learn.train('no_ice',17,'interrupted',2,rows=rows);learn.train('no_ice',17,'interrupted',4,rows=rows)
    a=torch.load(learn.R/'results/continuous/no_ice-normal-w8-17.pt',weights_only=True);b=torch.load(learn.R/'results/interrupted/no_ice-normal-w8-17.pt',weights_only=True)
    def same(x,y):
     if isinstance(x,torch.Tensor):return torch.equal(x,y)
     if isinstance(x,dict):return x.keys()==y.keys() and all(same(x[k],y[k]) for k in x)
     if isinstance(x,(list,tuple)):return len(x)==len(y) and all(same(c,d) for c,d in zip(x,y))
     return x==y
    for k in ['model','optimizer','sampler_rng','torch_rng','cursor','step']:self.assertTrue(same(a[k],b[k]),k)
    self.assertEqual([x['indices'] for x in a['updates']],[x['indices'] for x in b['updates']])
   finally:learn.R=old
if __name__=='__main__':unittest.main()
