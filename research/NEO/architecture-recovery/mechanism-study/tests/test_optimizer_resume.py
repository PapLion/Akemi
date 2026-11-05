import sys,unittest,torch,copy,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gradient_audit import factory
from variants import VARIANTS
from experiment import optimizer

def equal(a,b):
 if isinstance(a,torch.Tensor):return torch.equal(a,b)
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
class ResumeState(unittest.TestCase):
 def test_full_adamw_state_after_real_updates_and_safe_reload(self):
  for arm in VARIANTS+['capacity_transformer','event_matched','delta_matched','event_fast','delta_fast']:
   a=factory(arm,17);op=optimizer(a);x=torch.randint(1,120,(2,16));y=torch.tensor([48,49])
   for _ in range(2):op.zero_grad();torch.nn.functional.cross_entropy(a(x)[:,-1],y).backward();op.step()
   state=copy.deepcopy({'model':a.state_dict(),'optimizer':op.state_dict(),'rng':torch.get_rng_state(),'cursor':4,'update':2});f=io.BytesIO();torch.save(state,f);f.seek(0);state=torch.load(f,weights_only=True)
   b=factory(arm,17);b.load_state_dict(state['model'],strict=True);ob=optimizer(b);ob.load_state_dict(state['optimizer'])
   for m,o in [(a,op),(b,ob)]:torch.set_rng_state(state['rng']);o.zero_grad();torch.nn.functional.cross_entropy(m(x)[:,-1],y).backward();o.step()
   self.assertTrue(equal(a.state_dict(),b.state_dict()),arm);self.assertTrue(equal(op.state_dict(),ob.state_dict()),arm)
if __name__=='__main__':unittest.main()
