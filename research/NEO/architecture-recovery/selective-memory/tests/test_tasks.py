import sys,unittest,collections,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import panel
class TaskTests(unittest.TestCase):
 def test_oracles_ignore_proposals_and_follow_correction(self):
  ops=[['=','A','0'],['~','A','3'],['!','B','2'],['!','A','1'],['x','A','2']]
  self.assertEqual(panel.oracle(ops,'A'),1);self.assertEqual(panel.reverse_oracle(ops,'A'),1)
  self.assertEqual(panel.oracle(ops+[['-','A','_']],'A'),4)
  self.assertEqual(panel.oracle(ops+[['>','B','_']],'*'),2)
 def test_generator_counterfactuals_and_balanced_splits(self):
  rows=panel.generate('train',per_cell=1)
  self.assertEqual(len(rows),120)
  for r in rows:
   self.assertEqual(panel.oracle(r['ops'],r['query']),r['answer']);self.assertEqual(panel.reverse_oracle(r['ops'],r['query']),r['answer']);self.assertEqual(len(r['ids']),64)
   self.assertNotIn(r['family_bucket'],[6,7,8,9]);self.assertFalse(panel.heldout_pair(r['entity'],r['answer']))
  for task in panel.TASKS:
   rr=[r for r in rows if r['task']==task];self.assertEqual(collections.Counter(r['entity'] for r in rr),dict.fromkeys('ABCDE',3))
  for r in rows:
   if r['answer']!=4:
    c=panel.counterfactual(r,'valid');self.assertNotEqual(c['answer'],r['answer']);self.assertEqual(panel.reverse_oracle(c['ops'],c['query']),c['answer'])
   c=panel.counterfactual(r,'obsolete')
   if c:self.assertEqual(c['answer'],r['answer'])
 def test_recency_heuristics_do_not_resolve_panel(self):
  rows=panel.generate('train',per_cell=2)
  for kind in ['first','last','entity_last_any']:
   self.assertLess(sum(panel.heuristic(r,kind)==r['answer'] for r in rows)/len(rows),.35,kind)
 def test_task_names_have_distinct_semantics(self):
  for r in panel.generate('train',1):
   accepted=[op for op,e,v in r['ops'] if e==r['entity'] and op in ['=','!','-']]
   if r['task']=='retain' and r['answer']!=4:self.assertEqual(accepted,['='])
   if r['task']=='multiple':self.assertGreaterEqual(len(accepted),3)
 def test_no_family_or_content_overlap(self):
  sets={s:panel.generate(s,per_cell=1) for s in ['train','iid','compositional','structural','both']}
  self.assertFalse({r['family'] for r in sets['train']}&{r['family'] for r in sets['structural']})
  self.assertTrue({r['family'] for r in sets['iid']} <= {r['family'] for r in sets['train']})
  self.assertTrue({r['family'] for r in sets['compositional']} <= {r['family'] for r in sets['train']})
  seen=set()
  for rows in sets.values():
   h={r['id'] for r in rows};self.assertFalse(seen&h);seen|=h
  self.assertTrue(all(panel.heldout_pair(r['entity'],r['answer']) for r in sets['compositional']))
if __name__=='__main__':unittest.main()
