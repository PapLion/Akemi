import unittest,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import composition,data_panel
class CompositionTests(unittest.TestCase):
 def test_supplement_is_new_with_same_query_values_and_windows(self):
  old=data_panel.generate('train');new=composition.generate();self.assertFalse({r['id'] for r in old}&{r['id'] for r in new})
  for a,b in zip(old,new):
   self.assertEqual(a['answer'],b['answer']);self.assertEqual(a['positions'],b['positions']);self.assertEqual(a['entity'],b['entity'])
   self.assertEqual(data_panel.panel.reverse_oracle(b['ops'],b['query']),b['answer'])
if __name__=='__main__':unittest.main()
