import unittest,copy,inspect
import torch
import address_model as A
class Contracts(unittest.TestCase):
 def setUp(self):
  self.m,self.d,self.o,self.r=A.setup();self.rows=A.C.data('same');self.x=torch.tensor([r['ids'] for r in self.rows[::20]])
 def test_no_oracle_forward_argument(self):
  self.assertEqual(list(inspect.signature(A.Addressable.forward).parameters),['self','ids','doc','valid','trace','intervention'])
 def test_foreground_preserved(self):
  old,_,_,_=A.T.setup()
  for n,p in old.state_dict().items():self.assertTrue(torch.equal(p,self.m.state_dict()[n]),n)
 def test_mask_excludes_written_prefix(self):
  masks=[];handle=self.m.core.blocks[0].register_forward_pre_hook(lambda module,args:masks.append(args[1].clone()))
  try:self.m(self.x)
  finally:handle.remove()
  mask=masks[0];self.assertFalse(bool(mask.triu(1).any()));self.assertFalse(bool(mask[:,63,:48].any()))
 def test_auxiliary_decoder_absent_from_inference(self):
  y=self.m(self.x)
  with torch.no_grad():
   for p in self.d.parameters():p.fill_(999.)
  self.assertTrue(torch.equal(y,self.m(self.x)))
 def test_events_observed_only(self):
  _,tr=self.m(self.x,trace=True)
  counts=torch.stack([torch.stack([w['accepted'] for w in t['writes']],1).sum(1) for t in tr],1).sum(1)
  self.assertTrue(torch.equal(counts,torch.full_like(counts,2)))
 def test_delta_realizability(self):
  # Algebraic control only: orthogonal explicit keys. Not learned success.
  M=torch.zeros(8,32);k=torch.eye(8);v=torch.randn(3,32)
  for key,value in [(k[0],v[0]),(k[1],v[1]),(k[0],v[2])]:M=M+key[:,None]*(value-key@M)[None]
  self.assertTrue(torch.allclose(k[0]@M,v[2],atol=1e-6));self.assertTrue(torch.equal(k[1]@M,v[1]))
 def test_all_trainable_used_and_changed(self):
  before={n:p.detach().clone() for n,p in self.m.named_parameters() if p.requires_grad}
  result=A.T.update(self.m,self.d,self.o,self.r,self.rows,'A')
  for n,p in self.m.named_parameters():
   if p.requires_grad:
    self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n)
    self.assertFalse(torch.equal(before[n],p),n)
 def test_oracle_prefix_not_future(self):
  r=copy.deepcopy(self.rows[0]);r['ops'][8]=['!',r['q'],'3'];ids=A.P.make_record(r['ops'],r['q'],'test','diagnostic')['ids']
  y,tr=self.m(torch.tensor([self.rows[0]['ids']]),trace=True);z,tt=self.m(torch.tensor([ids]),trace=True)
  self.assertTrue(torch.equal(tr[1]['memory'],tt[1]['memory']));self.assertTrue(torch.equal(y[:,:32],z[:,:32]))
if __name__=='__main__':unittest.main(verbosity=2)
