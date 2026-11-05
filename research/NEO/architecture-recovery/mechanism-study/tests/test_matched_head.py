import sys,unittest,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from matched_head import build_matched
from experiment import make_model
class Matched(unittest.TestCase):
 def test_original_memory_initialization_exact(self):
  for kind in ['event','delta']:
   for seed in [17,29,43]:
    old=make_model(kind,seed);new=build_matched(kind+'_matched',seed)
    for k,v in new.memory_head.state_dict().items():torch.testing.assert_close(v,old.state_dict()[k],rtol=0,atol=0)
 def test_memory_rule_matches_old_for_same_hidden_inputs(self):
  for kind in ['event','delta']:
   old=make_model(kind,17);new=build_matched(kind+'_matched',17);ids=torch.randint(1,120,(2,16));doc=torch.zeros_like(ids);valid=torch.ones_like(ids,dtype=torch.bool)
   # Capture old local hidden chunks; run the replacement head on exactly these features.
   captured=[];active=old._active
   def capture(*args):
    x=active(*args);captured.append(x);return x
   old._active=capture;z=old(ids).logits;h=captured[0].reshape(2,16,32);out=torch.nn.functional.linear(old.norm(new.memory_head(h,doc,valid)),old.emb.weight)
   torch.testing.assert_close(z,out,rtol=2e-4,atol=2e-5)
if __name__=='__main__':unittest.main()
