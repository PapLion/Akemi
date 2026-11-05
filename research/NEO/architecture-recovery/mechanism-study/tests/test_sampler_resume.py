import sys,unittest,torch,random,json,io,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gradient_audit import factory
from experiment import optimizer,batch
from test_optimizer_resume import equal
class SamplerResume(unittest.TestCase):
 def test_different_batches_rng_cursor_and_adamw(self):
  panel=[json.loads(s) for s in (Path(__file__).resolve().parents[2]/'results/panel.jsonl').read_text().splitlines()];panel=[r for r in panel if r['split']=='train']
  for arm in ['intact','no_ice','capacity_transformer','event_fast','delta_fast']:
   a=factory(arm,17);op=optimizer(a);sampler=random.Random(5017)
   def step(m,o,rng):
    indices=rng.sample(range(len(panel)),2);x,y=batch([panel[k] for k in indices]);o.zero_grad();loss=torch.nn.functional.cross_entropy(m(x)[:,-1],y);loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1,error_if_nonfinite=True);o.step();return indices
   step(a,op,sampler);step(a,op,sampler)
   state=copy.deepcopy({'model':a.state_dict(),'optimizer':op.state_dict(),'sampler':sampler.getstate(),'torch_rng':torch.get_rng_state(),'update':2,'cursor':4,'microstep':0,'accumulation':{'pending':False,'steps':1},'config':{'arm':arm,'seed':17,'width':32}});f=io.BytesIO();torch.save(state,f);f.seek(0);state=torch.load(f,weights_only=True);continuous_indices=step(a,op,sampler)
   b=factory(arm,17);b.load_state_dict(state['model'],strict=True);ob=optimizer(b);ob.load_state_dict(state['optimizer']);sr=random.Random();sr.setstate(state['sampler']);torch.set_rng_state(state['torch_rng']);resumed_indices=step(b,ob,sr)
   self.assertEqual(continuous_indices,resumed_indices);self.assertEqual(sampler.getstate(),sr.getstate());self.assertTrue(equal(a.state_dict(),b.state_dict()),arm);self.assertTrue(equal(op.state_dict(),ob.state_dict()),arm)
if __name__=='__main__':unittest.main()
