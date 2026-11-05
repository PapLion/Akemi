import unittest,torch
class DeltaEdit(unittest.TestCase):
 def test_full_edit_replaces_key_and_preserves_orthogonal_key(self):
  # Exact algebra at a=1,e=1,w=1. Engineering property, not learned behavior.
  k=torch.tensor([1.,0.],dtype=torch.float64);h=torch.tensor([[2.,3.,4.],[7.,8.,9.]],dtype=torch.float64);v=torch.tensor([-1.,5.,6.],dtype=torch.float64)
  a=torch.eye(2,dtype=torch.float64)-k[:,None]*k[None,:];updated=a@h+k[:,None]*v
  torch.testing.assert_close(k@updated,v,rtol=0,atol=0)
  torch.testing.assert_close(updated[1],h[1],rtol=0,atol=0)
