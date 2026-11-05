import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tasks import build_panel,load_tokenizer
class Tasks(unittest.TestCase):
 def test_panel_reproducible_independent(self):
  a=build_panel(64,32);b=build_panel(64,32);self.assertEqual(a,b)
  train=[r for r in a if r['split']=='train'];dev=[r for r in a if r['split']=='dev'];self.assertEqual(len(train),448);self.assertEqual(len(dev),224)
  for key in ['hash','structure','combination']:
   self.assertFalse({r[key] for r in train}&{r[key] for r in dev},key)
  self.assertEqual(len({r['task'] for r in a}),7)
 def test_real_canonical_tokenizer(self):
  tok=load_tokenizer()
  for r in build_panel(2,2):
   self.assertEqual(tok.encode(r['text']),r['ids']);self.assertEqual(tok.decode(r['ids']),r['text']);self.assertEqual(len(r['ids']),64)
   self.assertEqual(tok.encode(r['answer']),[r['label']])
if __name__=='__main__':unittest.main()
