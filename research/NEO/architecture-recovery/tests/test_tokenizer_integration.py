import unittest,torch
from tasks import load_tokenizer,FP
from models import CryoNext,Config,causal_loss
class TokenizerIntegration(unittest.TestCase):
 def test_real_special_ids_and_masked_conversation_fixture(self):
  # Mask engineering only: no SFT updates and no conversation corpus acquisition.
  tok=load_tokenizer();self.assertEqual(tok.fingerprint,FP);self.assertEqual(tok.vocab_size,8192)
  self.assertEqual(tok.special_id('<|pad|>'),256)
  ids,target=tok.encode_chat([{'role':'user','content':'á Python x_2 = 7 🧊'},{'role':'assistant','content':'x_2 = 8'}])
  original_len=len(ids);ids+= [256,256];target += [False,False]
  x=torch.tensor([ids]);valid=torch.arange(len(ids))[None]<original_len;targets=torch.tensor([target])
  self.assertFalse(targets[0,0]);self.assertEqual(ids[0],257)
  for kind in ['event','delta']:
   m=CryoNext(Config(vocab=tok.vocab_size,width=16,chunk=8,kind=kind))
   out=m(x,valid=valid);loss=causal_loss(out.logits,x,valid=valid,target_mask=targets)
   keep=valid[:,:-1]&valid[:,1:]&targets[:,1:]
   expected=torch.nn.functional.cross_entropy(out.logits[:,:-1][keep],x[:,1:][keep]);torch.testing.assert_close(loss,expected)
  for text in ['','á Python x_2 = 7 🧊','e\u0301','\\frac{a}{b}','<|assistant|>']:
   self.assertEqual(tok.decode(tok.encode(text)),text)
