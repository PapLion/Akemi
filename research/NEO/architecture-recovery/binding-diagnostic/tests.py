import unittest
from experiment import *
class DiagnosticContracts(unittest.TestCase):
 def test_pairing_balance(self):
  from collections import Counter
  for split in ['train','dev-combinations','dev-layouts']:
   a,b=datasets('short')[split],datasets('long')[split]
   for x,y in zip(a,b):
    self.assertEqual(x['answer'],y['answer']);self.assertEqual(x['query'],y['query']);self.assertEqual(Counter(x['prefix']),Counter(y['prefix']));self.assertEqual(len(x['prefix']),len(y['prefix']));self.assertNotEqual(*x['values'])
   self.assertEqual(set(Counter((r['query_side'],r['gold']) for r in a).values()),{6})
 def test_queries_reach_logits(self):
  for c in ['short','long']:
   d=conditioning(model('full'),datasets(c)['train']);self.assertGreater(d['max_logit_delta'],0);self.assertGreater(d['query_embedding_gradient_norm'],0)
 def test_snapshot_resume_evidence(self):
  d=read('contracts');self.assertTrue(d['passed']);self.assertTrue(d['exact_resume_both_conditions'])
 def test_checkpoints_and_optimizer(self):
  for c in ['short','long']:
   m,o,cp=restore(ROOT/'results'/f'{c}-17.pt',datasets(c)['train']);self.assertEqual(cp['cursor_updates'],200);self.assertEqual(len(o.state),sum(p.requires_grad for p in m.parameters()));self.assertTrue(all(torch.isfinite(p).all() for p in m.parameters()))
 def test_oracle_swaps(self):
  for c in ['short','long']:
   rows=datasets(c)['train'];lookup={(tuple(r['values']),r['order'],r['query_side']):r for r in rows}
   for r in rows:
    donor=lookup[(tuple(reversed(r['values'])),r['order'],r['query_side'])];self.assertEqual(donor['gold'],r['values'][1-r['query_side']]);self.assertNotEqual(donor['answer'],r['answer'])
if __name__=='__main__':unittest.main(verbosity=2)
