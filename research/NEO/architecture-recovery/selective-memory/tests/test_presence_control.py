import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import panel,shortcut_audit
class PresenceControlTests(unittest.TestCase):
 def test_presence_control_never_reads_values(self):
  for r in panel.load('iid'):
   c=copy.deepcopy(r)
   for event in c['ops']:
    if event[2]!='_':event[2]=str((int(event[2])+1)%4)
   self.assertEqual(shortcut_audit.presence(r),shortcut_audit.presence(c))
 def test_presence_tracks_accept_delete_and_goal(self):
  r={'ops':[['=','A','1'],['~','B','2'],['>','A','_'],['-','A','_']],'query':'*'}
  self.assertEqual(shortcut_audit.presence(r),('A',False));r['ops'].append(['!','A','3']);self.assertEqual(shortcut_audit.presence(r),('A',True))
if __name__=='__main__':unittest.main()
