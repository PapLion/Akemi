import unittest,collections,copy
import study as S
D=S.D
class DataContracts(unittest.TestCase):
 def test_reference_distribution(self):
  rows,order=S.schedule(17,'B');pool=D.treatment()
  self.assertEqual(rows,[pool[i*12+v] for i,v in order])
 def test_schedules_budgets_coverage(self):
  for seed in [17,29,43]:
   b,bo=S.schedule(seed,'B');c,co=S.schedule(seed,'C');self.assertEqual(bo,co)
   for rr in [b,c]:
    self.assertEqual(len(rr),2400);self.assertEqual(sum(r['kind']=='correct' for r in rr),1200);self.assertEqual(sum(r['kind']=='correct' and r['affected']==r['q'] for r in rr),600)
   self.assertEqual(len({S.pair(r['q'],r['other']) for r in c}),9)
   support=collections.defaultdict(set)
   for r in c:
    if r['kind']=='correct':support[r['q'],r['other'],r['q']==r['affected']].add(r['label']-48)
   self.assertTrue(all(v=={0,1,2,3} for v in support.values()))
   self.assertTrue(all(S.pair(r['q'],r['other'])!=('A','C') for r in c))
 def test_causal_oracles(self):
  rr,_=S.schedule(17,'C');D.verify(rr)
  for r in rr:
   self.assertEqual(r['label']-48,D.P.oracle(r['ops'],r['q']))
   # A correction can only change the corrected association.
   if r['kind']=='correct':
    other=r['other'] if r['affected']==r['q'] else r['q']
    self.assertEqual(D.oracle(r['ops'][:r['event']],other),D.oracle(r['ops'][:r['event']+1],other))
 def test_holdout_and_heuristics(self):
  for arm in ['B','C']:
   train,_=S.schedule(17,arm);ids={tuple(r['ids']) for r in train}
   for name,rr in S.evaluation().items():
    self.assertFalse(any(tuple(r['ids']) in ids for r in rr),name)
    f=S.frequencies(rr);self.assertEqual(f['heuristics']['last_query'],1)
    self.assertLess(f['heuristics']['last_global'],.8)
    self.assertEqual(f['heuristics']['presence_constant'],.25)
 def test_response_mask_only(self):
  import torch
  import torch.nn.functional as F
  rows,_=S.schedule(17,'C');m,d,o,_=S.setup(17);xx=torch.tensor([r['ids'] for r in rows[:8]]);yy=torch.tensor([r['label'] for r in rows[:8]])
  logits=m(xx);logits.retain_grad();labels=torch.full(xx.shape,-100);labels[:,-1]=yy
  direct=F.cross_entropy(logits[:,-1],yy);masked=F.cross_entropy(logits.reshape(-1,logits.shape[-1]),labels.flatten(),ignore_index=-100)
  self.assertTrue(torch.equal(direct,masked));direct.backward();self.assertEqual(int(torch.count_nonzero(logits.grad[:,:-1])),0);self.assertTrue(all(p.grad is None for p in d.parameters()))
if __name__=='__main__':unittest.main()
