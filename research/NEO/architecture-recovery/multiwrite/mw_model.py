"""Two learned pre-pooling queries; historical reader/backbone/refinement unchanged."""
import sys,math,time
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'chunk-boundary'))
import chunk_study as C
T=C.T;I=C.I
from network import ObservedHybrid

def delta_step(memory,k,v,a,erase,write,K):
 if K>1:
  # Divide retention/erase budgets multiplicatively; additive write budget by K.
  a=a.pow(1./K);erase=1.-(1.-erase).pow(1./K);write=write/K
 pred=(k[:,None]@memory)[:,0]
 return a[:,:,None]*(memory-erase[:,:,None]*k[:,:,None]*pred[:,None,:])+k[:,:,None]*(write*v)[:,None,:]

class MultiWrite(ObservedHybrid):
 def forward(self,ids,doc=None,valid=None,trace=False,intervention=None):
  if self.write_K==1:return ObservedHybrid.forward(self,ids,doc,valid,trace=trace,intervention=intervention)
  x=self.hidden(ids,doc,valid);b,t,d=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  head=self.memory_head;idx,keep,reset,*_=head._plans(doc,valid,None);n,c=idx.shape[1:];xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d)
  memory=x.new_zeros(b,head.cfg.key_dim,d);outs=[];records=[]
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory)
   if j==n-1:
    if intervention=='reset':memory=torch.zeros_like(memory)
    if intervention=='swap':memory=memory.roll(1,0)
   retrieved,recover=head._read(xx[:,j],memory);retrieved=self.read(retrieved-xx[:,j]);fast=xx[:,j]
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],retrieved],-1)).tanh())
   outs.append((fast+retrieved)*keep[:,j,:,None])
   # Same normalized token states and learned attention-pooling family, now two queries.
   score=torch.einsum('sd,bcd->bsc',head.summary_query,fast)/math.sqrt(d);score=score.masked_fill(~keep[:,j,None,:],-1e4);weights=score.softmax(-1)
   z=torch.einsum('bsc,bcd->bsd',weights,fast)*keep[:,j].any(-1)[:,None,None]
   keys=F.normalize(head.key(z),dim=-1,eps=1e-6);values=head.value(z).tanh();controls=head.control(z).sigmoid();before=memory;contributions=[]
   for slot in range(2):
    a=.9+.09*controls[:,slot,:1];er=controls[:,slot,1:2];wr=controls[:,slot,2:]
    new=delta_step(memory,keys[:,slot],values[:,slot],a,er,wr,2);contributions.append(new-memory);memory=new
   memory=torch.where(keep[:,j].any(-1)[:,None,None],memory,before)
   if trace:
    if memory.requires_grad:memory.retain_grad()
    if z.requires_grad:z.retain_grad()
    records.append(dict(memory=memory,write=controls[:,:,2:],erase=controls[:,:,1:2],recover=recover,change=(memory-before).norm(dim=(-2,-1)),indices=idx[:,j],valid=keep[:,j],weights=weights,candidates=z,keys=keys,values=values,controls=controls,contributions=torch.stack(contributions,1),before=before))
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d));logits=F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
  return (logits,records) if trace else logits

def setup(K=1):
 m,d,_,rng=T.setup();m.core.__class__=MultiWrite;m.core.write_K=K
 if K==2:
  old=m.core.memory_head.summary_query.detach();assert old.shape==(1,32)
  gen=torch.Generator().manual_seed(404);second=old+torch.randn(old.shape,generator=gen)*.2
  m.core.memory_head.summary_query=nn.Parameter(torch.cat([old,second],0))
 o=torch.optim.AdamW([p for p in [*m.parameters(),*d.parameters()] if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 return m,d,o,rng

def load(path,rows,K):
 m,d,o,rng=setup(K);s=torch.load(path,weights_only=True,map_location='cpu');assert s['dataset_sha256']==T.digest(rows) and s['K']==K
 m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True);o.load_state_dict(s['optimizer']);rng.setstate(s['rng']);torch.set_rng_state(s['torch_rng']);__import__('random').setstate(s['python_rng']);assert s['cursor']==s['step']*8
 return m,d,o,rng,s['step']
def save(path,m,d,o,rng,rows,K,step):
 T.save(path,m,d,o,rng,rows,'A',step)
 # New experimental artifact only; never touch original or prior evidence.
 s=torch.load(path,weights_only=True);s['K']=K;s['multiwrite']='sequential sqrt-retention sqrt-erase half-write';torch.save(s,path)
