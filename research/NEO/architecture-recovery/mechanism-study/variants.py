"""Historical-backbone ablations. All foreground weights start identically per seed."""
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
from torch import nn
import torch.nn.functional as F
from experiment import make_model
from models import CryoNext,Config
from vendor.cryo_historical import CryoTiny,segments
VARIANTS=['intact','transformer','no_ice','no_filter','depth1','event','delta','detach','chunk2']

class MemoryHead(CryoNext):
 def __init__(self,d,kind):
  super().__init__(Config(width=d,kind=kind,chunk=8));del self.emb,self.blocks,self.norm
 def forward(self,x,doc,valid):
  b,t,d=x.shape;idx,keep,reset,*_=self._plans(doc,valid,None);n,c=idx.shape[1:]
  xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d)
  z=self._summarize(xx,keep);memory=x.new_zeros(b,self.cfg.slots if self.cfg.kind=='event' else self.cfg.key_dim,d);outs=[]
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory)
   out,_=self._read(xx[:,j],memory);outs.append(out*keep[:,j,:,None])
   if self.cfg.kind=='event':
    zz=z[:,j];er,wr=self.signals(torch.cat([zz,memory,zz-memory],-1)).sigmoid().chunk(2,-1)
    new=(1-wr)*(1-er)*memory+wr*self.candidate(zz).tanh()
   else:
    zz=z[:,j,0];k=F.normalize(self.key(zz),dim=-1,eps=1e-6);value=self.value(zz).tanh();ctrl=self.control(zz).sigmoid();a=.9+.09*ctrl[:,:1];er=ctrl[:,1:2];wr=ctrl[:,2:]
    prediction=(k[:,None]@memory)[:,0];new=a[:,:,None]*(memory-er[:,:,None]*k[:,:,None]*prediction[:,None,:])+k[:,:,None]*(wr*value)[:,None,:]
   memory=torch.where(keep[:,j].any(-1)[:,None,None],new,memory)
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d))
  return h

class Variant(CryoTiny):
 def configure(self,arm,seed):
  self.arm=arm;self.write_chunk=2
  frozen=[]
  if arm=='transformer':frozen=['fast','slow','gate','read','fast_norm','memory_init']
  if arm=='no_ice':frozen=['slow','gate','read','memory_init']
  if arm=='no_filter':frozen=['gate']
  if arm=='detach':frozen=['memory_init'] # no answer-only gradient can cross the detached horizon to initialization
  if arm in ['event','delta']:
   frozen=['fast','slow','gate','read','fast_norm','memory_init'];torch.manual_seed(seed+999);self.memory_head=MemoryHead(self.emb.embedding_dim,arm)
  for name,p in self.named_parameters():
   if name.split('.')[0] in frozen:p.requires_grad_(False)
 def forward(self,ids,doc=None,valid=None):
  if self.arm=='intact':return super().forward(ids,doc,valid)
  x=self.hidden(ids,doc,valid);b,t,d=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  if self.arm=='transformer':h=x
  elif self.arm in ['event','delta']:h=self.memory_head(x,doc,valid)
  elif self.arm=='chunk2':h=self.chunk_features(x,doc,valid)
  else:
   slow=self.memory_init.expand(b,-1);outs=[];_,resets=segments(doc,valid)
   for i in range(t):
    if self.arm=='detach':slow=slow.detach()
    slow=torch.where(resets[:,i,None],self.memory_init[None],slow);fast=x[:,i]
    read=torch.zeros_like(slow) if self.arm=='no_ice' else self.read(slow)
    for _ in range(1 if self.arm=='depth1' else 2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,x[:,i],read],-1)).tanh())
    if self.arm=='no_ice':outs.append(fast);continue
    z=torch.cat([slow,fast],-1);g=torch.ones_like(slow) if self.arm=='no_filter' else self.gate(z).sigmoid();candidate=self.slow(z).tanh();slow=torch.where(valid[:,i,None],(1-g)*slow+g*candidate,self.memory_init[None]);outs.append(fast+self.read(slow))
   h=torch.stack(outs,1)
  return F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
 def chunk_features(self,x,doc,valid):
  # Per-document scheduling prevents packing offsets from changing write boundaries.
  planner=object.__new__(CryoNext);planner.cfg=Config(chunk=self.write_chunk)
  idx,keep,resets,*_=CryoNext._plans(planner,doc,valid,None);b,t,d=x.shape;n,c=idx.shape[1:];xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d);slow=self.memory_init.expand(b,-1);outs=[]
  for j in range(n):
   slow=torch.where(resets[:,j,None],self.memory_init[None],slow);fast=xx[:,j];read=self.read(slow)
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],read[:,None].expand(-1,c,-1)],-1)).tanh())
   z=torch.cat([slow,fast[:,-1]],-1);g=self.gate(z).sigmoid();new=(1-g)*slow+g*self.slow(z).tanh();full=keep[:,j].all(-1);new=torch.where(full[:,None],new,slow)
   h=fast+read[:,None];last=fast[:,-1]+self.read(new);h=torch.cat([h[:,:-1],last[:,None]],1);outs.append(h*keep[:,j,:,None]);slow=new
  return x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d))

def build(arm,seed,width=32):
 if arm not in VARIANTS:raise ValueError(arm)
 ref=make_model('cryo_history',seed,width=width);m=Variant(v=8192,d=width,layers=1,dropout=0.);m.load_state_dict(ref.state_dict(),strict=True);m.configure(arm,seed);return m
