import unittest,json,hashlib,tempfile,sys
from pathlib import Path
import torch
import f2
import count_v3
from selection import build
ROOT=Path(__file__).resolve().parent
class ReadinessTests(unittest.TestCase):
 def test_tokenizer(self):
  t=count_v3.load()
  for s in ['Español: árbol y pingüino.','English text\n','🙂未知\x00']:
   self.assertEqual(t.decode(t.encode(s)),s);self.assertEqual(t.encode(s),t.encode(s))
 def test_parameter_counts(self):
  self.assertEqual(sum(p.numel() for p in f2.make('F2').parameters()),2082176)
  self.assertEqual(sum(p.numel() for p in f2.make('Transformer').parameters()),2032768)
 def test_contract_receipts(self):
  r=json.loads((ROOT/'results/f2-benchmark.json').read_text())
  for arm in r.values():
   for k,v in arm['contracts'].items():
    if k!='generation_ids':self.assertIs(v,True,k)
 def test_selection_gate_and_splits(self):
  r=build();self.assertFalse(r['ready']);self.assertEqual(r['train_independent_targets'],25355);self.assertEqual(r['dev_targets'],8637);self.assertEqual(r['known_train_dev_shared_word_shingles']['64'],0)
 def test_target_coverage(self):
  for n in [2,128,129,256,300]:
   ids=list(range(n));covered=[]
   for start in range(0,n-1,127):covered.extend(range(start+1,min(start+128,n)))
   self.assertEqual(covered,list(range(1,n)))
 def test_no_raw_content_manifest(self):
  for r in json.loads((ROOT/'results/f2-selection.json').read_text())['documents']:
   self.assertNotIn('text',r);self.assertEqual(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest(),r['sha'])
 def test_full_recovery_receipts(self):
  r=json.loads((ROOT/'results/integrity.json').read_text())
  for view,expected in [('raw1b',564789),('curated500',257043),('curated1b',555914)]:
   self.assertEqual(sum(g['documents'] for g in r['views'][view]['groups'] if g['track'] in ['BASE_LM','BASE_LM_CLEAN']),expected)
   self.assertEqual(r['views'][view]['base_exact_duplicate_excess'],0)
   for key in ['empty','text_sha_mismatch','byte_mismatch','missing_required']:self.assertEqual(r['views'][view]['issues'][key],0)
 def test_gates_honest(self):
  r=json.loads((ROOT/'results/gates.json').read_text());self.assertFalse(r['selected_5M_independent_targets']);self.assertFalse(r['full_training_started']);self.assertFalse(r['V3_whole_corpus_count_complete'])
 def test_resume_actual_trajectory(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertTrue(f2.contracts('F2',Path(d))['resume_6_vs_2_plus_4_exact_model_optimizer_rng_cursor'])
if __name__=='__main__':unittest.main(verbosity=2)
