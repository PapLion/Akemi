import unittest,torch
from models import Config,CryoNext
class SessionIdentity(unittest.TestCase):
 def test_duplicate_session_ids_rejected(self):
  m=CryoNext(Config(vocab=64,width=16,chunk=4));ids=torch.randint(1,60,(2,8))
  with self.assertRaises(ValueError):m(ids,session_id=('same','same'))
  with self.assertRaises(ValueError):m(ids,session_id='same')
