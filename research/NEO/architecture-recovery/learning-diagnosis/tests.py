import unittest,tempfile
from diagnose import *
class Signal(unittest.TestCase):
 def test_targets_and_mean(self):
  rows=datasets()['3'];m=h.model('B');y=h.logits(m,rows);labels=torch.tensor([r['answer'] for r in rows]);manual=-y.log_softmax(-1)[torch.arange(4),labels].mean();self.assertTrue(torch.equal(manual,F.cross_entropy(y,labels)));d=grad_detail(m,rows);self.assertTrue(d['gradient_ce_matches_softmax']);self.assertTrue(all(v<0 for v in d['correct_logit_gradient']))
  changed=labels.roll(1);y0=y.detach().requires_grad_();y1=y.detach().requires_grad_();F.cross_entropy(y0,labels).backward();F.cross_entropy(y1,changed).backward();self.assertTrue(torch.allclose(y1.grad-y0.grad,(F.one_hot(labels,8192)-F.one_hot(changed,8192))/4,atol=1e-7))
 def test_data_and_no_target_leak(self):
  ds=datasets();self.assertEqual([len(v) for v in ds.values()],[1,2,4,48]);r=ds['3'];self.assertEqual(r[0]['values'],list(reversed(r[2]['values'])));self.assertEqual(Counter(x['answer'] for x in r),Counter({r[0]['answer']:2,r[1]['answer']:2}));m=h.model('B');ys=h.logits(m,r);changed=[{**x,'answer':(x['answer']+1)%8192} for x in r];self.assertTrue(torch.equal(ys,h.logits(m,changed)));x,last,y=h.tensors(r);self.assertTrue(all(last[i]==len(v['prefix'])+len(v['query'])-1 and y[i]==v['answer'] for i,v in enumerate(r)));self.assertGreater(float((ys[:2]-ys[2:]).abs().max().detach()),0)
 def test_mask_isolation_and_both_layers_gradient(self):
  rows=datasets()['3'];m=h.model('B');x,last,y=h.tensors(rows);mem=torch.zeros(4,8,32);hidden,_=m.chunk_hidden(x,mem,False);xp=x.clone();xp[:,110:]=(xp[:,110:]+1)%8192;alt,_=m.chunk_hidden(xp,mem,False);self.assertTrue(torch.equal(hidden[:,:110],alt[:,:110]));self.assertTrue(torch.allclose(h.logits(m,rows[:1]),h.logits(m,rows)[:1],atol=1e-6,rtol=1e-5));d=grad_detail(m,rows)
  for n,p in m.named_parameters():
   if p.requires_grad:self.assertIn(n,d['parameters']);self.assertTrue(torch.isfinite(p.grad).all())
  self.assertTrue(any(v['grad_norm']>0 for k,v in d['parameters'].items() if k.startswith('blocks.1.')))
 def test_exact_resume_and_repeated_initialization(self):
  rows=datasets()['3'];m=h.model('B');n=h.model('B');a=h.optimizer(m);b=h.optimizer(n)
  for u in range(3):h.update(m,a,rows,u,17);h.update(n,b,rows,u,17)
  self.assertEqual(h.state_sha(m),h.state_sha(n))
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'s.pt';snapshot(p,m,a,3,rows)
   for u in range(3,8):h.update(m,a,rows,u,17)
   rng=torch.get_rng_state();prng=random.getstate();n,b,c=restore(p,rows)
   for u in range(c['cursor'],8):h.update(n,b,rows,u,17)
   self.assertEqual(h.state_sha(m),h.state_sha(n));self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(prng,random.getstate())
   for x,y in zip(a.state.values(),b.state.values()):
    for k in x:self.assertTrue(torch.equal(x[k],y[k]))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Signal));
 if not r.wasSuccessful():sys.exit(1)
 evidence={'passed':True,'tests':r.testsRun,'script_sha':h.file_sha(ROOT/'diagnose.py'),'tests_sha':h.file_sha(Path(__file__)),'protocol_sha':h.file_sha(ROOT/'PROTOCOL.json'),'historical_sources':h.sources(),'tokenizer_sha':h.file_sha(h.ARTIFACT)}
 if (OUT/'signal-contracts.json').exists():assert json.loads((OUT/'signal-contracts.json').read_text())==evidence
 else:put('signal-contracts',evidence)
