"""Keep historical fast refinement; replace only slow-memory subsystem with chunk Event/Delta."""
import torch
import torch.nn.functional as F
from variants import Variant
from experiment import make_model
class Hybrid(Variant):
 def forward(self,ids,doc=None,valid=None):
  x=self.hidden(ids,doc,valid);b,t,d=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  head=self.memory_head;idx,keep,reset,*_=head._plans(doc,valid,None);n,c=idx.shape[1:];xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d)
  memory=x.new_zeros(b,head.cfg.slots if head.cfg.kind=='event' else head.cfg.key_dim,d);outs=[]
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory)
   retrieved,_=head._read(xx[:,j],memory);retrieved=self.read(retrieved-xx[:,j]);fast=xx[:,j]
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],retrieved],-1)).tanh())
   outs.append((fast+retrieved)*keep[:,j,:,None]);z=head._summarize(fast[:,None],keep[:,j:j+1])[:,0]
   if head.cfg.kind=='event':
    er,wr=head.signals(torch.cat([z,memory,z-memory],-1)).sigmoid().chunk(2,-1);new=(1-wr)*(1-er)*memory+wr*head.candidate(z).tanh()
   else:
    z=z[:,0];k=F.normalize(head.key(z),dim=-1,eps=1e-6);v=head.value(z).tanh();ctrl=head.control(z).sigmoid();a=.9+.09*ctrl[:,:1];er=ctrl[:,1:2];wr=ctrl[:,2:];pred=(k[:,None]@memory)[:,0];new=a[:,:,None]*(memory-er[:,:,None]*k[:,:,None]*pred[:,None,:])+k[:,:,None]*(wr*v)[:,None,:]
   memory=torch.where(keep[:,j].any(-1)[:,None,None],new,memory)
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d))
  return F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
def build_hybrid(arm,seed,width=32):
 kind=arm.removesuffix('_fast');ref=make_model('cryo_history',seed,width=width);m=Hybrid(v=8192,d=width,layers=1,dropout=0.);m.load_state_dict(ref.state_dict(),strict=True);m.configure(kind,seed)
 original=make_model(kind,seed,width=width);m.memory_head.load_state_dict({k:v for k,v in original.state_dict().items() if not k.startswith(('emb.','blocks.','norm.'))},strict=True)
 for name,p in m.named_parameters():
  if name.split('.')[0] in ['fast','fast_norm','read']:p.requires_grad_(True)
 m.arm=arm;return m
