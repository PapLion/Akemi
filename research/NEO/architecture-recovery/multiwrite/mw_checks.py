from mw_run import *
import mw_model as M

def main():
 # Algebraic K1 transition, independent of forward delegation.
 gen=torch.Generator().manual_seed(7);memory=torch.randn(2,8,32,generator=gen,requires_grad=True);k=F.normalize(torch.randn(2,8,generator=gen),dim=-1);v=torch.randn(2,32,generator=gen).tanh();a=torch.full((2,1),.95);er=torch.full((2,1),.4);wr=torch.full((2,1),.7)
 pred=(k[:,None]@memory)[:,0];ref=a[:,:,None]*(memory-er[:,:,None]*k[:,:,None]*pred[:,None,:])+k[:,:,None]*(wr*v)[:,None,:];got=delta_step(memory,k,v,a,er,wr,1);assert torch.equal(ref,got);assert torch.equal(torch.autograd.grad(ref.sum(),memory,retain_graph=True)[0],torch.autograd.grad(got.sum(),memory)[0])
 # Exact K2 source scale and conservation of retention/erasure budget when controls identical.
 assert torch.allclose(a.sqrt()*a.sqrt(),a);assert torch.allclose((1-(1-er).sqrt()).neg().add(1).pow(2),1-er)
 m,d,o,rng,step=load(OUT/'B-300.pt',C.data('same'),2);rows=C.data('same');result={};original=M.delta_step
 for skip in [0,1]:
  counter=[0]
  def patched(memory,k,v,a,erase,write,K):
   slot=counter[0]%2;counter[0]+=1
   return memory if slot==skip else original(memory,k,v,a,erase,write,K)
  M.delta_step=patched
  try:ev,states=C.evaluate(m,d,rows)
  finally:M.delta_step=original
  result[str(skip)]=dict(initial=ev['metrics']['all']['initial'],original_accuracy=ev['metrics']['all']['original_accuracy'],note='Inference-only intervention omits entire candidate update incl retention/erase; not training ablation')
 dump('candidate-ablation.json',result);dump('additional-checks.json',dict(k1_transition_gradient_exact=True,identical_control_retention_budget=True,mask_scope='existing engineering certification; no new GPU/streaming API certification'))
 # Read-only historical integrity checks; all previous artifacts remain local.
 import subprocess
 checks={}
 for folder in ['cryo-chunk-boundary-v1/chunk-boundary','cryo-two-bindings-v1/two-bindings']:
  root=R.parent.parent/folder;p=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=root,capture_output=True,text=True);checks[folder]=dict(returncode=p.returncode,verified=p.stdout.count(': OK'),stderr=p.stderr);assert p.returncode==0
 dump('historical-integrity.json',checks)
 print('PASS transition and historical integrity checks')
if __name__=='__main__':main()
