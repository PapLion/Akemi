import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import panel
class CounterfactualTests(unittest.TestCase):
 def test_hidden_valid_fact_changes_label_without_changing_visible_query_block(self):
  for r in panel.load('iid')+panel.load('structural'):
   valid=panel.counterfactual(r,'valid');self.assertNotEqual(valid['answer'],r['answer'])
   if r['outside_window']:self.assertEqual(valid['ids'][-16:],r['ids'][-16:])
   obsolete=panel.counterfactual(r,'obsolete')
   if obsolete:self.assertEqual(obsolete['answer'],r['answer'])
 def test_final_loader_is_closed(self):
  with self.assertRaises(ValueError):panel.load('final')
if __name__=='__main__':unittest.main()
