from factorial import *
import unittest,tempfile
class Contracts(unittest.TestCase):
 def test_data(self):
  r=validate_data();self.assertEqual([r[a]['dataset']['train']['responses'] for a in 'ABCD'],[4,24,8,48]);self.assertEqual(r['D']['dataset_sha'],h.digest(historical()['4']));self.assertEqual(r['A']['dataset_sha'],h.digest(historical()['3']));self.assertEqual([r[a]['effective_exposure']['responses'] for a in 'ABCD'],[3200]*4)
 def test_targets_causality_and_optimizer(self):
  for arm,ds in datasets().items():
   rows=ds['train'];m=h.model('B');o=h.optimizer(m);x,last,y=h.tensors(rows);hidden,_=m.chunk_hidden(x,torch.zeros(len(rows),8,32),False);xp=x.clone();xp[:,110:]=(xp[:,110:]+3)%8192;alt,_=m.chunk_hidden(xp,torch.zeros(len(rows),8,32),False);self.assertTrue(torch.equal(hidden[:,:110],alt[:,:110]));self.assertTrue(torch.allclose(h.logits(m,rows[:1]),h.logits(m,rows)[:1],atol=1e-6,rtol=1e-5));changed=[{**r,'answer':(r['answer']+3)%8192} for r in rows];self.assertTrue(torch.equal(h.logits(m,rows),h.logits(m,changed)));self.assertEqual({id(p) for p in m.parameters() if p.requires_grad},{id(p) for g in o.param_groups for p in g['params']});rec=h.update(m,o,rows,0,17);self.assertTrue(all(math.isfinite(v) for v in rec['gradients'].values()));self.assertGreater(sum(v for k,v in rec['gradients'].items() if k.startswith('blocks.1.')),0)
 def test_resume_all_arms(self):
  for arm,ds in datasets().items():
   rows=ds['train'];m=h.model('B');o=h.optimizer(m)
   for u in range(3):h.update(m,o,rows,u,17)
   with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'state.pt';checkpoint(p,m,o,3,rows,arm)
    for u in range(3,8):h.update(m,o,rows,u,17)
    rng=torch.get_rng_state();prng=random.getstate();n,q,c=restore(p,rows)
    for u in range(c['cursor_updates'],8):h.update(n,q,rows,u,17)
    self.assertEqual(h.state_sha(m),h.state_sha(n));self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(prng,random.getstate())
    for a,b in zip(o.state.values(),q.state.values()):
     for k in a:self.assertTrue(torch.equal(a[k],b[k]))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
 if not r.wasSuccessful():sys.exit(1)
 evidence={'passed':True,'tests':r.testsRun,'sources':sources(),'tests_sha':h.file_sha(Path(__file__)),'data':validate_data()}
 if (OUT/'contracts.json').exists():assert get('contracts')==json.loads(json.dumps(evidence))
 else:put('contracts',evidence)
