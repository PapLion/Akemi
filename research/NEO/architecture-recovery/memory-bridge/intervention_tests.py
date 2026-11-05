from diagnostics import *
import unittest
class Interventions(unittest.TestCase):
 def test_state_continuation(self):
  m=model('ice');train=read('train');rows=[train[0],next(r for r in train if r['lang']=='es'),next(r for r in train if r['distance']==128 and r['lang']=='es')]
  with torch.no_grad():
   h,_=prefix_states(m,rows);self.assertTrue(torch.allclose(query_logits(m,rows,h),logits(m,rows,'ice'),atol=2e-6,rtol=1e-5))
 def test_no_write_and_no_read(self):
  m=model('ice');rows=read('micro')[:4]
  with torch.no_grad():
   zero,_=prefix_states(m,rows,False);self.assertEqual(float(zero.norm()),0)
   h1=torch.randn_like(zero);h2=torch.randn_like(zero);a=query_logits(m,rows,h1,'no_read');b=query_logits(m,rows,h2,'no_read');self.assertTrue(torch.equal(a,b))
 def test_reset_ignores_donor(self):
  m=model('ice');rows=read('micro')[:4]
  with torch.no_grad():
   self.assertTrue(all(len(r['query'])<=16 for r in rows));h,_=prefix_states(m,rows);z=torch.zeros_like(h);self.assertTrue(torch.equal(query_logits(m,rows,z,'no_write'),query_logits(m,rows,z,'normal')))
 def test_donor_compatibility(self):
  for r in read('micro'):
   d=donor_row(r);self.assertEqual(r['query'],d['query']);self.assertEqual(r['pair'],d['pair']);self.assertEqual(r['distance'],d['distance']);self.assertNotEqual(r['answer'],d['answer']);self.assertEqual(r['values'][1-r['query_side']],d['values'][1-r['query_side']])
 def test_full_context_sees_prefix(self):
  m=model('full');rows=read('micro')[:2]
  x,last,_=tensors(rows);h=m.emb(x);h.retain_grad();# direct embedding hook verifies the unhidden full-context route
  captured=[]
  handle=m.emb.register_forward_hook(lambda mod,args,out:(out.retain_grad(),captured.append(out))[1] or out)
  try:logits(m,rows,'full').square().sum().backward()
  finally:handle.remove()
  self.assertGreater(float(captured[0].grad[:,:rows[0]['fact_tokens']].norm()),0)
if __name__=='__main__':unittest.main(verbosity=2)
