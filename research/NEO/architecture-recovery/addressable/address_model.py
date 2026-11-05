"""Record-aware learned shared addressing. No oracle entity/value indices."""
import sys,random
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'multiwrite'))
import mw_model as M
T=M.T;C=M.C;P=C.P;I=M.I
class Addressable(M.MultiWrite):
 def forward(self,ids,doc=None,valid=None,trace=False,intervention=None):
  x=self.hidden(ids,doc,valid);b,t,d=x.shape
  doc=torch.zeros_like(ids) if doc is None else doc
  valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  idx,keep,reset,*_=self.memory_head._plans(doc,valid,None);n,c=idx.shape[1:]
  xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d)
  tok=ids.gather(1,idx.reshape(b,-1)).reshape(b,n,c)
  # Foreground input embeddings provide context-independent learned addresses.
  # Four-ID record framing is declared format metadata, never an oracle lookup.
  memory=x.new_zeros(b,8,d);outs=[];records=[]
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory)
   if j==n-1:
    if intervention=='reset':memory=memory*0
    if intervention=='swap':memory=memory.roll(1,0)
   keys=F.normalize(self.address(self.emb(tok[:,j])),dim=-1,eps=1e-6)
   # A record's entity is visible from offset 1 onwards. Before that use own key.
   q=keys.clone()
   for off in range(0,c,4):
    if off+1<c:
     for pos in range(off+1,min(off+4,c)):q[:,pos]=keys[:,off+1]
   read=q@memory
   retrieved=self.read(self.address_out(read));fast=xx[:,j]
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],retrieved],-1)).tanh())
   outs.append((fast+retrieved)*keep[:,j,:,None]);before=memory;writes=[]
   for off in range(0,c,4):
    if off+3>=c:continue
    # Deterministic observed grammar schedule. No parsing entity/value meaning.
    accepted=((tok[:,j,off]==ord('='))|(tok[:,j,off]==ord('!')))&(tok[:,j,off+3]==ord(';'))&keep[:,j,off:off+4].all(-1)
    k=keys[:,off+1];v=self.event_value(fast[:,off+2]).tanh()
    predicted=(k[:,None]@memory)[:,0]
    new=memory+k[:,:,None]*(v-predicted)[:,None,:]
    memory=torch.where(accepted[:,None,None],new,memory)
    writes.append(dict(accepted=accepted,key=k,value=v))
   if trace:
    if memory.requires_grad:memory.retain_grad()
    records.append(dict(memory=memory,before=before,change=(memory-before).norm(dim=(-2,-1)),indices=idx[:,j],valid=keep[:,j],writes=writes,read=read))
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d))
  logits=F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
  return (logits,records) if trace else logits

def setup():
 m,d,_,rng=T.setup();m.core.__class__=Addressable
 # Old memory head is retained for planning/checkpoint provenance, deliberately frozen.
 for p in m.core.memory_head.parameters():p.requires_grad_(False)
 torch.manual_seed(707)
 m.core.address=nn.Linear(32,8,bias=False)
 m.core.event_value=nn.Linear(32,32)
 m.core.address_out=nn.Linear(32,32,bias=False)
 o=torch.optim.AdamW([p for p in [*m.parameters(),*d.parameters()] if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 return m,d,o,rng

def save(path,m,d,o,rng,rows,step):
 T.save(path,m,d,o,rng,rows,'A',step)
def restore(path,rows):
 m,d,o,rng=setup();s=torch.load(path,weights_only=True,map_location='cpu')
 assert s['dataset_sha256']==T.digest(rows) and s['cursor']==s['step']*8
 m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True);o.load_state_dict(s['optimizer']);rng.setstate(s['rng']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng'])
 return m,d,o,rng,s['step']
