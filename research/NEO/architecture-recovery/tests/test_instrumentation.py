import unittest,sys,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import make_model,evaluate
from tasks import build_panel
class Instrumentation(unittest.TestCase):
 def test_baseline_has_no_memory_gates_to_report(self):
  rows=[r for r in build_panel(1,1) if r['split']=='dev']
  records,gates=evaluate(make_model('b0_local'),rows,'b0_local',17,'initial')
  self.assertEqual(len(records),7);self.assertEqual(gates,[])
if __name__=='__main__':unittest.main()
