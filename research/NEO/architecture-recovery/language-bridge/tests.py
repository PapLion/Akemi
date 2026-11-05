from engine import *
import unittest,tempfile
class Contracts(unittest.TestCase):
 def test_tokenizer(self):
  t=tokenizer();self.assertEqual([t.special_id(k) for k in ['<|pad|>','<|bos|>','<|eos|>']],[256,257,258]);texts=['','Español: ¿qué pasó? niño.','English text\n\t  spacing','👩🏽‍💻 e\u0301 é \x00','def my_name(x):\n return x**2','\\frac{a}{b} = π','<|assistant|>','# Título\n\n**texto** `a_b`\n- uno\n','User: Hola\nAssistant: Buenos días']
  for text in texts:
   ids=t.encode(text);self.assertEqual(t.decode(ids),text);self.assertEqual(ids,t.encode(text));self.assertTrue(all(i<256 or i>=512 for i in ids))
  raw=bytes(range(256));self.assertEqual(t.decode_bytes(t.encode_bytes(raw)),raw)
  self.assertEqual(tokenizer().encode(texts[3]),t.encode(texts[3]))
 def test_future(self):
  for kind in ['ice','no_ice','transformer']:
   m=create(kind);x=torch.arange(48)[None]+512;y=x.clone();y[:,21:]+=100
   for mode in [True,False]:
    m.train(mode);a=m(x);b=m(y);self.assertTrue(torch.allclose(a[:,:21],b[:,:21],atol=1e-6,rtol=1e-6))
 def test_documents_batch_padding(self):
  m=create('ice');x=torch.arange(48)[None]+512;doc=torch.cat([torch.zeros(24),torch.ones(24)]).long()[None];p=m(x,doc);a=m(x[:,:24]);b=m(x[:,24:]);self.assertTrue(torch.allclose(p[:,:24],a,atol=1e-6));self.assertTrue(torch.allclose(p[:,24:],b,atol=1e-6));self.assertTrue(torch.allclose(m(x.repeat(2,1))[0],m(x)[0],atol=1e-6))
  valid=torch.ones_like(x,dtype=torch.bool);valid[:,40:]=False;ce,n=loss(m(x,doc,valid),x,doc,valid);self.assertEqual(n,38);self.assertTrue(torch.isfinite(ce))
 def test_streaming(self):
  m=create('ice');x=torch.arange(39)+512;full=m(x[None]);state=m.initial()
  for i,v in enumerate(x):
   logits,state=m.step(v,state);self.assertTrue(torch.allclose(logits,full[:,i],atol=2e-6,rtol=1e-5));self.assertLess(len(state.pending),16)
  with self.assertRaises(ValueError):m.step(513,state,'other')
 def test_gradients_optimizer(self):
  for kind in ['ice','no_ice','transformer']:
   m=create(kind);o=optimizer(m);expected={id(p) for p in m.parameters() if p.requires_grad};actual=[id(p) for g in o.param_groups for p in g['params']];self.assertEqual(len(actual),len(set(actual)));self.assertEqual(expected,set(actual));before={n:p.clone() for n,p in m.named_parameters()};r=update(m,o,0)
   for n,p in m.named_parameters():
    if p.requires_grad:self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n);self.assertFalse(torch.equal(p,before[n]),n)
   self.assertEqual(len(o.state),len(expected))
 def test_prefix_grad(self):
  m=create('ice');x=(torch.arange(40)+512)[None];logits=m(x);logits[:,35].square().sum().backward();self.assertGreater(float(m.emb.weight.grad[x[0,15]].norm()),0)
 def test_resume_full(self):
  for kind in ['ice','no_ice','transformer']:
   m=create(kind);o=optimizer(m)
   for c in range(3):update(m,o,c)
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'resume.pt';save(path,m,o,3)
    for c in range(3,8):update(m,o,c)
    rng_t=torch.get_rng_state();rng_p=random.getstate()
    n,p,cursor=restore(path);self.assertEqual(cursor,3)
    for c in range(cursor,8):update(n,p,c)
    self.assertTrue(torch.equal(rng_t,torch.get_rng_state()));self.assertEqual(rng_p,random.getstate())
    for a,b in zip(m.parameters(),n.parameters()):self.assertTrue(torch.equal(a,b))
    for a,b in zip(o.state.values(),p.state.values()):
     for key in a:self.assertTrue(torch.equal(a[key],b[key]))
 def test_aux_free(self):
  m=create('ice');self.assertFalse(any('trapos' in n or 'decoder' in n for n,_ in m.named_parameters()))
if __name__=='__main__':torch.set_num_threads(1);unittest.main(verbosity=2)
