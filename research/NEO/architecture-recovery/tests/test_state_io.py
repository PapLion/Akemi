import unittest,torch,io,sys,dataclasses
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from models import CryoNext,Config
from state_io import pack_state,unpack_state
from vendor import next_training_v1 as old
class StateIO(unittest.TestCase):
 def test_detached_state_reload(self):
  for kind in ['event','delta']:
   torch.manual_seed(31);m=CryoNext(Config(vocab=64,width=16,chunk=4,kind=kind));x=torch.randint(1,60,(1,12));first=m(x[:,:8],session_id='session-A')
   data=io.BytesIO();torch.save(pack_state(first.state),data);data.seek(0);state=unpack_state(torch.load(data,weights_only=True));self.assertFalse(state.memory.requires_grad)
   a=m(x[:,8:],state=first.state,session_id='session-A');b=m(x[:,8:],state=state,session_id='session-A');torch.testing.assert_close(a.logits,b.logits,atol=0,rtol=0)
 def test_metadata_fixes_preserve_learning_math(self):
  for kind,ablation in [('event','none'),('delta','none'),('b0','none'),('b0_full','none'),('event','no_filter'),('event','always_write'),('event','no_memory'),('event','no_persist')]:
   cfg=Config(vocab=64,width=16,layers=1,chunk=4,kind=kind,ablation=ablation);torch.manual_seed(23);m=CryoNext(cfg);n=old.CryoNext(old.Config(**dataclasses.asdict(cfg)));n.load_state_dict(m.state_dict(),strict=True);x=torch.randint(1,60,(2,12));a=m(x).logits;b=n(x).logits;torch.testing.assert_close(a,b,atol=0,rtol=0)
   ma=[p for p in m.parameters() if p.requires_grad];na=[p for p in n.parameters() if p.requires_grad];ga=torch.autograd.grad(a.square().sum(),ma);gb=torch.autograd.grad(b.square().sum(),na)
   for u,v in zip(ga,gb):torch.testing.assert_close(u,v,atol=0,rtol=0)
if __name__=='__main__':unittest.main()
