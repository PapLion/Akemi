import unittest,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from reader import Reader
class Contracts(unittest.TestCase):
 def test_approved_reader_target_coverage(self):
  r=Reader(R/'results/approved-selection.json',128,2)
  self.assertEqual(sum(len(ids)-1 for _,_,ids in r.windows),25355)
  self.assertTrue(all(ids[0]==257 for _,off,ids in r.windows if off==0))
 def test_deterministic_order_and_resume(self):
  a=Reader(R/'results/approved-selection.json');b=Reader(R/'results/approved-selection.json')
  a.next();a.next();b.load_state_dict(a.state_dict());self.assertEqual(a.next()[3],b.next()[3])
 def test_fail_closed_identity(self):
  r=Reader(R/'results/approved-selection.json')
  with self.assertRaises(AssertionError):r.load_state_dict(r.state_dict()|{'context':256})
 def test_conditional_not_approved(self):
  s=json.loads((R/'results/conditional-selection.json').read_text())
  self.assertFalse(s['authorized_for_training']);self.assertTrue(all(d['status']=='CONDITIONAL' for d in s['documents']))
 def test_candidate_isolation(self):
  d=json.loads((R/'results/conditional-selection.json').read_text())['documents']
  train=[r for r in d if r['split']=='train'];dev=[r for r in d if r['split']=='dev']
  for field in ['key','sha256','family','component']:
   self.assertFalse({r[field] for r in train}&{r[field] for r in dev},field)
  self.assertFalse(any(r['historical_split']=='test' for r in d))
 def test_attribution_one_per_candidate(self):
  d=json.loads((R/'results/conditional-selection.json').read_text())['documents'];a=[json.loads(x) for x in (R/'results/attribution.jsonl').read_text().splitlines()]
  self.assertEqual({r['key'] for r in d},{r['key'] for r in a})
  self.assertTrue(all(r['article_url'] and r['license_url'] and r['title'] for r in a))
 def test_count_cache_certificate(self):
  import sqlite3,array
  c=sqlite3.connect('file:'+str(R/'counts.sqlite')+'?mode=ro',uri=True)
  for d in json.loads((R/'results/conditional-selection.json').read_text())['documents']:
   n,blob=c.execute('select n,ids from counts where sha=?',(d['sha256'],)).fetchone();self.assertEqual(n,d['text_ids']);self.assertEqual(len(blob),2*n)
if __name__=='__main__':unittest.main()
