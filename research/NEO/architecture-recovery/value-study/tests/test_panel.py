import unittest,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import data_panel
class PanelTests(unittest.TestCase):
 def test_oracle_and_conditional_balance(self):
  for split in data_panel.LAYOUTS:
   rr=data_panel.generate(split)
   for e in range(5):
    for g in range(4):
     r=[x for x in rr if x['entity_index']==e and x['regime']==g and x['present']]
     self.assertEqual(len(set(collections.Counter(x['answer'] for x in r).values())),1)
   for r in rr:self.assertEqual(data_panel.panel.oracle(r['ops'],r['query']),data_panel.panel.reverse_oracle(r['ops'],r['query']))
 def test_no_value_access_in_foreground(self):
  rr=data_panel.generate('dev')
  grouped=collections.defaultdict(list)
  for r in rr:grouped[(r['entity'],r['regime'],r['present'])].append(r)
  for rows in grouped.values():self.assertEqual(len({tuple(r['ids'][-16:]) for r in rows}),1)
 def test_splits_have_disjoint_programs(self):
  sets=[{tuple(r['ids']) for r in data_panel.generate(s)} for s in data_panel.LAYOUTS]
  for i,a in enumerate(sets):
   for b in sets[i+1:]:self.assertFalse(a&b)
if __name__=='__main__':unittest.main()
