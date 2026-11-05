"""Experimental visibility/intervention adapters over frozen b7d4b13 mechanisms."""
import sys,types,copy,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'mechanism-study'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
from torch import nn
import torch.nn.functional as F
from variants import build as original_build
from hybrid import build_hybrid,Hybrid
from capacity_control import build_control
from vendor.cryo_historical import segments,Baseline,CryoTiny
ARMS=['intact','no_ice','transformer','event_fast','delta_fast']
def local_hidden(self,ids,doc=None,valid=None):
 b,t=ids.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
 seg,_=segments(doc,valid);pos=torch.zeros_like(ids)
 for i in range(1,t):pos[:,i]=torch.where((seg[:,i]==seg[:,i-1])&valid[:,i],pos[:,i-1]+1,0)
 ar=torch.arange(t,device=ids.device);mask=(seg[:,:,None]==seg[:,None,:])&(ar[:,None]>=ar[None,:])[None]&valid[:,None,:]
 if self.visible_window:
  block=pos//self.visible_window;mask=mask&(block[:,:,None]==block[:,None,:]);pos=pos%self.visible_window
 mask=torch.where(valid[:,:,None],mask,torch.eye(t,dtype=torch.bool,device=ids.device)[None]);x=self.dropout(self.emb(ids))
 for block in self.blocks:x=block(x,mask,pos)
 return x*valid[...,None]
class ObservedHybrid(Hybrid):
 def forward(self,ids,doc=None,valid=None,trace=False,intervention=None):
  x=self.hidden(ids,doc,valid);b,t,d=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  head=self.memory_head;idx,keep,reset,*_=head._plans(doc,valid,None);n,c=idx.shape[1:];xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d)
  memory=x.new_zeros(b,head.cfg.slots if head.cfg.kind=='event' else head.cfg.key_dim,d);outs=[];records=[]
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory)
   if j==n-1:
    if intervention=='reset':memory=torch.zeros_like(memory)
    if intervention=='swap':memory=memory.roll(1,0)
   retrieved,recover=head._read(xx[:,j],memory);retrieved=self.read(retrieved-xx[:,j])
   if self.memory_mode=='no_read':retrieved=torch.zeros_like(retrieved)
   fast=xx[:,j]
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],retrieved],-1)).tanh())
   outs.append((fast+retrieved)*keep[:,j,:,None]);z=head._summarize(fast[:,None],keep[:,j:j+1])[:,0]
   if head.cfg.kind=='event':
    er,wr=head.signals(torch.cat([z,memory,z-memory],-1)).sigmoid().chunk(2,-1)
    if self.memory_mode=='always':wr=torch.ones_like(wr)
    elif self.memory_mode=='random':wr=(torch.rand_like(wr[...,:1])<self.random_budget).to(wr.dtype).expand_as(wr)
    new=(1-wr)*(1-er)*memory+wr*head.candidate(z).tanh()
   else:
    z=z[:,0];k=F.normalize(head.key(z),dim=-1,eps=1e-6);v=head.value(z).tanh();ctrl=head.control(z).sigmoid();a=.9+.09*ctrl[:,:1];er=ctrl[:,1:2];wr=ctrl[:,2:]
    if self.memory_mode=='always':wr=torch.ones_like(wr)
    elif self.memory_mode=='random':wr=(torch.rand_like(wr[:,:1])<self.random_budget).to(wr.dtype).expand_as(wr)
    pred=(k[:,None]@memory)[:,0];new=a[:,:,None]*(memory-er[:,:,None]*k[:,:,None]*pred[:,None,:])+k[:,:,None]*(wr*v)[:,None,:]
   delta=(new-memory).norm(dim=(-2,-1));memory=torch.where(keep[:,j].any(-1)[:,None,None],new,memory)
   if trace:
    if memory.requires_grad:memory.retain_grad()
    records.append({'write':wr,'erase':er,'recover':recover,'change':delta,'memory':memory,'indices':idx[:,j],'valid':keep[:,j]})
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d));logits=F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
  return (logits,records) if trace else logits
class Model(nn.Module):
 def __init__(self,arm,seed,window=8,mode='normal',random_budget=.5):
  super().__init__();self.arm=arm;self.window=window;self.mode=mode
  self.core=build_control(seed) if arm=='transformer' else (build_hybrid(arm,seed) if arm.endswith('_fast') else original_build(arm,seed))
  if arm.endswith('_fast'):
   self.core.__class__=ObservedHybrid;self.core.memory_mode=mode;self.core.random_budget=random_budget
   if mode=='no_read':
    for name,p in self.core.named_parameters():
     if name.startswith(('memory_head.','read.')):p.requires_grad_(False)
   if mode in ['always','random'] and arm=='event_fast':
    for p in self.core.memory_head.signals.parameters():p.requires_grad_(False)
  self.core.visible_window=window;self.core.hidden=types.MethodType(local_hidden,self.core)
 def forward(self,ids,doc=None,valid=None,trace=False,intervention=None):
  if self.arm.endswith('_fast'):return self.core(ids,doc,valid,trace=trace,intervention=intervention)
  if trace and self.arm=='intact':return CryoTiny.forward(self.core,ids,doc,valid,return_trace=True)
  return self.core(ids,doc,valid)
 def reference(self,ids):
  if self.arm.endswith('_fast'):return Hybrid.forward(self.core,ids)
  # Full-context original hidden bypasses the visibility adapter.
  old=self.core.hidden;self.core.hidden=types.MethodType(Baseline.hidden,self.core)
  try:return self.core(ids)
  finally:self.core.hidden=old
 def config(self):
  cfg={'arm':self.arm,'window':self.window,'mode':self.mode,'vocab':8192,'width':32,'dropout':0,'precision':'CPU FP32'}
  if self.mode=='random':cfg['random_budget']=self.core.random_budget
  return cfg
def build(arm,seed,window=8,mode='normal',random_budget=.5):
 if arm not in ARMS:raise ValueError(arm)
 return Model(arm,seed,window,mode,random_budget)
def optimizer(m):return torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
