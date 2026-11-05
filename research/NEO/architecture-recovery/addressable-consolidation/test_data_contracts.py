import unittest,collections,copy
import data_v11 as D
import runner_v11 as V
class DataContracts(unittest.TestCase):
 def test_original_control_exact(self):self.assertEqual(D.control(),D.C.data('same'))
 def test_all_prefix_oracles_independent(self):
  for r in D.treatment():
   for j in range(1,16):
    for e in [r['q'],r['other']]:self.assertEqual(D.oracle(r['ops'][:j],e),D.P.oracle(r['ops'][:j],e))
 def test_corrected_value_and_preserved_other(self):
  for r in D.treatment():
   if r['kind']!='correct':continue
   e=r['affected'];other=r['other'] if e==r['q'] else r['q'];j=r['event']
   self.assertNotEqual(D.oracle(r['ops'][:j],e),D.oracle(r['ops'][:j+1],e));self.assertEqual(D.oracle(r['ops'][:j],other),D.oracle(r['ops'][:j+1],other))
 def test_stale_and_current_counterfactual_semantics(self):
  for r in D.treatment():
   if r['kind']!='correct':continue
   stale=D.transform(r,'obsolete');current=D.transform(r,'current')
   self.assertEqual(stale['label'],r['label']);self.assertNotEqual(current['label'],r['label'])
 def test_exact_exposure_budget_and_matching_indices(self):
  import random
  aa,bb=D.control(),D.treatment();ra=random.Random(17);rb=random.Random(17);k=0
  for step in range(300):
   a,i,_=V.batch(aa,'A',step,ra);b,j,_=V.batch(bb,'B',step,rb);self.assertEqual(i,j)
   self.assertEqual(sum(r['kind']=='correct' for r in b),4)
   for x,y in zip(a,b):self.assertEqual(x['ids'][:16],y['ids'][:16])
   k+=len(b)
  self.assertEqual(k,2400)
 def test_phase_grid_targets_valid(self):
  for rr in D.grid().values():D.verify(rr)
 def test_independent_dev_no_train_programs(self):
  train={tuple(r['ids']) for r in D.treatment()+D.control()}
  for name,rr in D.dev_sets().items():
   if name=='correction_fit':continue
   self.assertFalse(any(tuple(r['ids']) in train for r in rr),name)
 def test_auxiliary_targets_balanced(self):
  f=D.frequencies(D.treatment());groups=collections.defaultdict(list)
  for r in f['auxiliary']:groups[r['entity']].append(r['count'])
  for counts in groups.values():self.assertEqual(len(counts),4);self.assertEqual(len(set(counts)),1)
if __name__=='__main__':unittest.main(verbosity=2)
