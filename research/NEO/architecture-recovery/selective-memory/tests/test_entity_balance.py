import unittest,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import panel
class EntityBalanceTests(unittest.TestCase):
 def test_no_entity_determines_compositional_answer(self):
  for split in ['train','iid','compositional','structural','both']:
   rows=panel.generate(split,2)
   for e in panel.ENTITIES:self.assertGreaterEqual(len({r['answer'] for r in rows if r['entity']==e}),2,(split,e))
   counts=collections.Counter(r['answer'] for r in rows);self.assertEqual(len(set(counts.values())),1)
if __name__=='__main__':unittest.main()
