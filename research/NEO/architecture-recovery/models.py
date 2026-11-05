"""Original research prototypes. CPU FP32 reference; no external architecture code copied."""
from dataclasses import dataclass
import math
import torch
from torch import nn
import torch.nn.functional as F

@dataclass
class Config:
 vocab:int=8192
 width:int=32
 layers:int=1
 chunk:int=32
 slots:int=4
 key_dim:int=8
 kind:str='event'
 ablation:str='none'
 hard_threshold:float=.5

@dataclass
class MemoryState:
 memory:torch.Tensor
 last_doc:torch.Tensor
 offset:torch.Tensor
 session_id:tuple|None=None

@dataclass
class Output:
 logits:torch.Tensor
 state:MemoryState|None
 stats:dict
 trace:dict

def affine_scan(a,b,initial):
 """Inclusive ordered affine prefix, Hillis-Steele. Dense proof reference, not optimized WY."""
 stride=1
 while stride<a.shape[1]:
  old_a,old_b=a,b
  a=torch.cat([old_a[:,:stride],old_a[:,stride:]@old_a[:,:-stride]],1)
  b=torch.cat([old_b[:,:stride],old_a[:,stride:]@old_b[:,:-stride]+old_b[:,stride:]],1)
  stride*=2
 return a@initial[:,None]+b

def causal_loss(logits,ids,doc=None,valid=None,target_mask=None):
 doc=torch.zeros_like(ids) if doc is None else doc
 valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
 keep=valid[:,:-1]&valid[:,1:]&(doc[:,:-1]==doc[:,1:])
 if target_mask is not None:keep=keep&target_mask[:,1:]
 if not keep.any():raise ValueError('No eligible targets')
 return F.cross_entropy(logits[:,:-1][keep],ids[:,1:][keep])

class ActiveBlock(nn.Module):
 def __init__(self,d):
  super().__init__();self.n1=nn.RMSNorm(d,eps=1e-6);self.n2=nn.RMSNorm(d,eps=1e-6)
  self.qkv=nn.Linear(d,3*d,bias=False);self.o=nn.Linear(d,d,bias=False)
  self.up=nn.Linear(d,4*d,bias=False);self.down=nn.Linear(2*d,d,bias=False)
 def forward(self,x,mask):
  b,t,d=x.shape
  q,k,v=[z.reshape(b,t,4,d//4).transpose(1,2) for z in self.qkv(self.n1(x)).chunk(3,-1)]
  y=F.scaled_dot_product_attention(q,k,v,attn_mask=mask[:,None],dropout_p=0.)
  x=x+self.o(y.transpose(1,2).reshape(b,t,d));u,v=self.up(self.n2(x)).chunk(2,-1)
  return x+self.down(F.silu(u)*v)

class CryoNext(nn.Module):
 def __init__(self,cfg):
  super().__init__();self.cfg=cfg;d=cfg.width
  assert d%4==0 and cfg.kind in ['b0','b0_full','event','delta']
  assert cfg.ablation in ['none','no_memory','no_filter','always_write','no_persist']
  self.emb=nn.Embedding(cfg.vocab,d);self.blocks=nn.ModuleList([ActiveBlock(d) for _ in range(cfg.layers)]);self.norm=nn.RMSNorm(d,eps=1e-6)
  if cfg.kind in ['event','delta']:
   self.read_query=nn.Linear(d,d if cfg.kind=='event' else cfg.key_dim,bias=False)
   self.read_out=nn.Linear(d,d,bias=False);self.recover=nn.Linear(d,1)
   self.summary_query=nn.Parameter(torch.randn(cfg.slots if cfg.kind=='event' else 1,d)*.02)
   if cfg.kind=='event':
    self.signals=nn.Linear(3*d,2*d);self.candidate=nn.Linear(d,d)
   else:
    self.key=nn.Linear(d,cfg.key_dim,bias=False);self.value=nn.Linear(d,d);self.control=nn.Linear(d,2+d)
  self.apply(self._init)
  if cfg.ablation in ['no_memory','no_persist']:
   for n,p in self.named_parameters():
    if not n.startswith(('emb.','blocks.','norm.')):p.requires_grad_(False)
  if cfg.kind=='event' and cfg.ablation=='always_write':
   # w=1 makes both learned update gates mathematically irrelevant. Explicit freeze.
   for p in self.signals.parameters():p.requires_grad_(False)
  if cfg.ablation=='no_filter':
   self.summary_query.requires_grad_(False)
   for p in self.recover.parameters():p.requires_grad_(False)
   for name in ['signals','control']:
    if hasattr(self,name):
     for p in getattr(self,name).parameters():p.requires_grad_(False)
 @staticmethod
 def _init(m):
  if isinstance(m,(nn.Linear,nn.Embedding)):
   nn.init.normal_(m.weight,std=.05)
   if isinstance(m,nn.Linear) and m.bias is not None:nn.init.zeros_(m.bias)
 def _active(self,x,valid,mask=None):
  # Positions relative to each complete chunk; no future statistics or normalization.
  t=x.shape[1];d=x.shape[2];p=torch.arange(t,device=x.device,dtype=x.dtype)[:,None]
  f=10000**(-torch.arange(0,d,2,device=x.device,dtype=x.dtype)/d)
  pos=torch.stack([(p*f).sin(),(p*f).cos()],-1).flatten(-2)
  x=x+pos[None]*.1
  if mask is None:mask=torch.ones(t,t,device=x.device,dtype=torch.bool).tril()[None]&valid[:,None,:]
  mask=torch.where(valid[:,:,None],mask,torch.eye(t,device=x.device,dtype=torch.bool)[None])
  for block in self.blocks:x=block(x,mask)
  return x*valid[...,None]
 def _plans(self,doc,valid,state):
  # Metadata only; per-document chunks make packing and batch composition invariant.
  # Python/ragged scheduling is a measured prototype limitation, not a CUDA fast path.
  ds=doc.detach().cpu().tolist();vs=valid.detach().cpu().tolist();plans=[];lasts=[];offsets=[]
  for row,(dd,vv) in enumerate(zip(ds,vs)):
   pp=[];i=0;last=-1;offset=0
   while i<len(dd):
    if not vv[i]:i+=1;continue
    start=i;di=dd[i]
    while i<len(dd) and vv[i] and dd[i]==di:i+=1
    length=i-start;continued=start==0 and state is not None and int(state.last_doc[row])==di
    base=int(state.offset[row]) if continued else 0
    if continued and base%self.cfg.chunk:raise ValueError('Continuation requires complete chunk boundary')
    for k in range(start,i,self.cfg.chunk):pp.append((list(range(k,min(k+self.cfg.chunk,i))),not continued if k==start else False))
    last=di;offset=base+length
   if not vv[-1]:last=-1;offset=0
   plans.append(pp);lasts.append(last);offsets.append(offset)
  n=max(map(len,plans),default=0)
  if not n:raise ValueError('No valid document tokens')
  b=doc.shape[0];c=self.cfg.chunk;idx=torch.zeros(b,n,c,dtype=torch.long,device=doc.device);keep=torch.zeros(b,n,c,dtype=torch.bool,device=doc.device);reset=torch.ones(b,n,dtype=torch.bool,device=doc.device)
  for row,pp in enumerate(plans):
   for j,(indices,r) in enumerate(pp):
    idx[row,j,:len(indices)]=torch.tensor(indices,device=doc.device);keep[row,j,:len(indices)]=True;reset[row,j]=r
  return idx,keep,reset,torch.tensor(lasts,device=doc.device),torch.tensor(offsets,device=doc.device),[len(x) for x in plans]
 def _summarize(self,x,valid):
  if self.cfg.ablation=='no_filter':
   z=(x*valid[...,None]).sum(-2)/valid.sum(-1,keepdim=True).clamp_min(1)
   return z[...,None,:].expand(*z.shape[:-1],self.summary_query.shape[0],z.shape[-1])
  score=torch.einsum('sd,bncd->bnsc',self.summary_query,x)/math.sqrt(self.cfg.width)
  score=score.masked_fill(~valid[:,:,None,:],-1e4)
  return torch.einsum('bnsc,bncd->bnsd',score.softmax(-1),x)*valid.any(-1)[:,:,None,None]
 def _read(self,x,memory):
  if self.cfg.kind=='event':
   q=self.read_query(x);attn=(q@memory.transpose(-1,-2)/math.sqrt(self.cfg.width)).softmax(-1);read=attn@memory
  else:
   q=F.normalize(self.read_query(x),dim=-1,eps=1e-6);read=q@memory
  gate=torch.ones_like(x[...,:1]) if self.cfg.ablation=='no_filter' else self.recover(x).sigmoid()
  return x+gate*self.read_out(read),gate
 def forward(self,ids,doc=None,valid=None,state=None,parallel=False,hard=False,answer_positions=None,session_id=None):
  b,t=ids.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  if isinstance(session_id,str):session_id=(session_id,)*b
  if session_id is not None:
   session_id=tuple(session_id)
   if len(session_id)!=b or any(not isinstance(s,str) or not s for s in session_id) or len(set(session_id))!=b:raise ValueError('Unique explicit session identity per batch row required')
  if state is not None and (session_id is None or state.session_id is None or session_id!=state.session_id):raise ValueError('Foreign, reordered, or unidentified session state')
  if hard and (self.training or self.cfg.kind!='event'):raise ValueError('Hard skip is inference-only Event')
  if self.cfg.kind=='b0_full':
   seg=torch.cat([torch.ones(b,1,device=ids.device,dtype=torch.long),((doc[:,1:]!=doc[:,:-1])|~valid[:,1:]|~valid[:,:-1]).long()],1).cumsum(1)
   mask=(seg[:,:,None]==seg[:,None,:])&torch.ones(t,t,device=ids.device,dtype=torch.bool).tril()[None]&valid[:,None,:]
   # Positional indices reset per document for unpacked parity.
   emb=self.emb(ids);outs=[]
   for row in range(b):
    xx=torch.zeros_like(emb[row]);start=0
    while start<t:
     end=start+1
     while end<t and seg[row,end]==seg[row,start]:end+=1
     xx[start:end]=self._active(emb[row:row+1,start:end],valid[row:row+1,start:end])[0];start=end
    outs.append(xx)
   h=torch.stack(outs);trace={};stats={};new_state=None
  else:
   idx,keep,reset,last,offset,lengths=self._plans(doc,valid,state);n,c=idx.shape[1:]
   xx=self.emb(ids).gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,self.cfg.width)).reshape(b*n,c,-1)
   x=self._active(xx,keep.reshape(b*n,c)).reshape(b,n,c,-1);outs=[];trace={'memory_before':[],'memory_after':[],'write':[],'erase':[],'recover':[]};stats={'candidate_slots_eligible':0,'candidate_slots_executed':0,'chunks':sum(lengths)}
   if self.cfg.kind=='b0':hchunks=x;new_state=None
   elif self.cfg.ablation=='no_memory':hchunks=x;new_state=None
   else:
    z=self._summarize(x,keep);shape=(b,self.cfg.slots,self.cfg.width) if self.cfg.kind=='event' else (b,self.cfg.key_dim,self.cfg.width)
    memory=x.new_zeros(shape) if state is None else state.memory
    if memory.shape!=shape:raise ValueError('State shape/session batch mismatch')
    memory0=memory
    if self.cfg.kind=='delta':
     zz=z[:,:,0];k=F.normalize(self.key(zz),dim=-1,eps=1e-6);value=self.value(zz).tanh();controls=self.control(zz).sigmoid();a=.9+.09*controls[...,:1];e=controls[...,1:2];w=controls[...,2:]
     if self.cfg.ablation=='no_filter':a=torch.ones_like(a)*.99;e=torch.ones_like(e);w=torch.ones_like(w)
     if self.cfg.ablation=='always_write':w=torch.ones_like(w)
     eye=torch.eye(self.cfg.key_dim,device=x.device,dtype=x.dtype)
     aa=a[...,None]*(eye-e[...,None]*k[...,None]*k[...,None,:]);bb=k[...,None]*(w*value)[...,None,:]
     aa=aa.masked_fill(reset[...,None,None],0)
     if self.cfg.ablation=='no_persist':aa=aa*0
     states=affine_scan(aa,bb,memory0) if parallel else None
    elif parallel:raise ValueError('Event gates depend on old memory: affine scan invalid')
    for j in range(n):
     r=reset[:,j] | (self.cfg.ablation=='no_persist');memory=torch.where(r[:,None,None],torch.zeros_like(memory),memory)
     trace['memory_before'].append(memory);out,rg=self._read(x[:,j],memory);trace['recover'].append(rg)
     if self.cfg.kind=='event':
      zz=z[:,j];er,wr=self.signals(torch.cat([zz,memory,zz-memory],-1)).sigmoid().chunk(2,-1)
      if self.cfg.ablation=='no_filter':er=torch.ones_like(er);wr=torch.ones_like(wr)
      if self.cfg.ablation=='always_write':wr=torch.ones_like(wr)
      eligible=keep[:,j].any(-1)[:,None].expand(-1,self.cfg.slots);stats['candidate_slots_eligible']+=int(eligible.sum())
      if hard:
       selected=(wr.mean(-1)>=self.cfg.hard_threshold)&eligible
       candidate=torch.zeros_like(zz)
       if selected.any():candidate=candidate.index_put(tuple(selected.nonzero(as_tuple=True)),self.candidate(zz[selected]).tanh())
       wr=wr*selected[...,None];er=er*selected[...,None];stats['candidate_slots_executed']+=int(selected.sum())
      else:candidate=self.candidate(zz).tanh();stats['candidate_slots_executed']+=b*self.cfg.slots
      new=(1-wr)*(1-er)*memory+wr*candidate
     else:
      wr=w[:,j];er=e[:,j];new=states[:,j] if parallel else aa[:,j]@memory+bb[:,j]
     present=keep[:,j].any(-1);memory=torch.where(present[:,None,None],new,memory)
     trace['memory_after'].append(memory);trace['write'].append(wr);trace['erase'].append(er);outs.append(out*keep[:,j,:,None])
    hchunks=torch.stack(outs,1)
    # Rows with fewer chunks must retain their last real state, not padded round reset.
    final=torch.stack([trace['memory_after'][lengths[row]-1][row] if lengths[row] else memory0[row]*0 for row in range(b)])
    new_state=MemoryState(final,last,offset,session_id)
   h=x.new_zeros(b,t,self.cfg.width).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,self.cfg.width),(hchunks*keep[...,None]).reshape(b,-1,self.cfg.width))
  h=self.norm(h)*valid[...,None]
  if answer_positions is not None:h=h[torch.arange(b,device=ids.device),answer_positions]
  return Output(F.linear(h,self.emb.weight),new_state,stats,trace)
