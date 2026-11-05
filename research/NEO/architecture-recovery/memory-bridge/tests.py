from runner import *
from data import make,questions,oracle,TOK
import unittest,tempfile
class Contracts(unittest.TestCase):
 def test_oracle_and_balance(self):
  rows=read('train');d=read('dev-combinations');s=read('dev-structures');self.assertFalse({r['program_id'] for r in rows}&{r['program_id'] for r in d+s})
  from collections import Counter
  counts={}
  for r in rows:
   self.assertEqual(oracle(r['events'])[r['query_entity']],r['gold']);self.assertEqual(len(r['prefix'])%16,0);self.assertGreaterEqual(len(r['prefix'])-r['fact_tokens'],16);self.assertEqual(len(TOK.encode(' '+__import__('data').COLORS[r['lang']][r['gold']])),1)
   k=(r['lang'],r['query_entity'],tuple(r['query']));counts.setdefault(k,Counter())[r['gold']]+=1
  for c in counts.values():self.assertEqual(len(set(c.values())),1)
 def test_head_parity(self):
  train=read('train');rows=[train[0],next(r for r in train if r['lang']=='es'),next(r for r in train if r['distance']==128),next(r for r in train if r['distance']==128 and r['lang']=='es')]
  for arm in ['ice','no_ice']:
   m=model(arm);y=logits(m,rows,arm);x,last,_=tensors(rows);reference=m(x);self.assertTrue(torch.allclose(y,reference[torch.arange(len(rows)),last],atol=2e-6,rtol=1e-5))
 def test_no_ice_hidden_prefix(self):
  a=questions(make((0,1),[0,1],'en'))[0];b=questions(make((0,1),[3,2],'en'))[0];m=model('no_ice');self.assertTrue(torch.equal(logits(m,[a],'no_ice'),logits(m,[b],'no_ice')))
 def test_future_and_sessions(self):
  m=model('ice');ids=torch.arange(64)[None]+512;other=ids.clone();other[:,27:]+=100
  for training in [True,False]:
   m.train(training);self.assertTrue(torch.allclose(m(ids)[:,:27],m(other)[:,:27],atol=1e-6))
  self.assertTrue(torch.allclose(m(ids.repeat(2,1))[0],m(ids)[0],atol=1e-6))
 def test_gradient_to_real_memory(self):
  m=model('ice');rows=read('micro')[:8];y,states=logits(m,rows,'ice',True);F.cross_entropy(y,torch.tensor([r['answer'] for r in rows])).backward();self.assertGreater(float(states[0].grad.norm()),0);self.assertGreater(float(m.event_value.weight.grad.norm()),0);self.assertGreater(float(m.address.weight.grad.norm()),0);self.assertGreater(float(m.read.weight.grad.norm()),0)
 def test_targets_not_forward_inputs(self):
  m=model('ice');rows=read('micro')[:2];changed=[{**r,'answer':r['choices'][(r['gold']+1)%4],'gold':(r['gold']+1)%4} for r in rows];self.assertTrue(torch.equal(logits(m,rows,'ice'),logits(m,changed,'ice')))
 def test_optimizer_and_resume(self):
  rows=read('micro')
  for arm in ['ice','no_ice','full']:
   m=model(arm);o=optimizer(m);active={id(p) for p in m.parameters() if p.requires_grad};params=[id(p) for g in o.param_groups for p in g['params']];self.assertEqual(len(params),len(set(params)));self.assertEqual(active,set(params));before={n:p.clone() for n,p in m.named_parameters()};update(m,o,rows,0,arm)
   for n,p in m.named_parameters():
    if p.requires_grad:self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n);self.assertFalse(torch.equal(p,before[n]),n)
   for c in range(1,3):update(m,o,rows,c,arm)
   with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'checkpoint.pt';checkpoint(path,m,o,3,rows,arm,17)
    for c in range(3,8):update(m,o,rows,c,arm)
    rng=torch.get_rng_state();prng=random.getstate();n,q,state=restore(path,rows);self.assertEqual(state['cursor_samples'],24)
    for c in range(state['cursor_updates'],8):update(n,q,rows,c,arm)
    self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(prng,random.getstate())
    for a,b in zip(m.parameters(),n.parameters()):self.assertTrue(torch.equal(a,b))
    for a,b in zip(o.state.values(),q.state.values()):
     for k in a:self.assertTrue(torch.equal(a[k],b[k]))
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts);r=unittest.TextTestRunner(verbosity=2).run(suite)
 if r.wasSuccessful():
  result={'passed':True,'tests':r.testsRun,'model_sha':file_sha(BASE/'language-bridge/model.py'),'tokenizer_sha':file_sha(ARTIFACT),'precision':'CPU FP32','protocol_sha':file_sha(CODE/'protocol.json')}
  if (OUT/'results/engineering.json').exists():assert read('engineering')==result;print('Existing engineering evidence retained; identities match')
  else:save_json('engineering',result)
 else:sys.exit(1)
