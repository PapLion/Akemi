"""Minimal boundary adapter: historical blocks/refinement + unchanged Addressable Delta.
New token interface is explicit. No event parser, oracle, Trapos head or pretrained weight migration.
"""
from common import *
from dataclasses import dataclass,field
import torch
from torch import nn
import torch.nn.functional as F
from vendor.cryo_historical import Block
@dataclass
class Session:
 memory:torch.Tensor
 pending:list=field(default_factory=list)
 session_id:str='session'
 completed:int=0
class LanguageBridge(nn.Module):
 def __init__(self,vocab=8192,width=32,chunk=16,kind='ice'):
  super().__init__();self.kind=kind;self.chunk=chunk;self.width=width;self.vocab=vocab
  self.emb=nn.Embedding(vocab,width);self.blocks=nn.ModuleList([Block(width)]);self.address=nn.Linear(width,8,bias=False);self.event_value=nn.Linear(width,width);self.address_out=nn.Linear(width,width,bias=False);self.read=nn.Linear(width,width,bias=False);self.fast=nn.Linear(width*3,width);self.fast_norm=nn.RMSNorm(width,eps=1e-6);self.slow_norm=nn.RMSNorm(width,eps=1e-6)
  for m in self.modules():
   if isinstance(m,(nn.Linear,nn.Embedding)):
    nn.init.normal_(m.weight,std=.02)
    if isinstance(m,nn.Linear) and m.bias is not None:nn.init.zeros_(m.bias)
  if kind!='ice':
   for name,p in self.named_parameters():
    if name.startswith(('address.','event_value.','address_out.','read.')) or kind=='transformer' and name.startswith(('fast.','fast_norm.')):p.requires_grad_(False)
 def initial(self,session_id='session'):return Session(self.emb.weight.new_zeros(1,8,self.width),[],session_id,0)
 def chunk_hidden(self,ids,memory,write=True):
  b,t=ids.shape;ar=torch.arange(t,device=ids.device);mask=(ar[:,None]>=ar[None,:])[None].expand(b,-1,-1);pos=ar[None].expand(b,-1);x=self.emb(ids)
  for block in self.blocks:x=block(x,mask,pos)
  if self.kind=='transformer':return self.slow_norm(x),memory
  if self.kind=='ice':
   q=F.normalize(self.address(self.emb(ids)),dim=-1,eps=1e-6);retrieved=self.read(self.address_out(q@memory))
  else:retrieved=torch.zeros_like(x)
  fast=x
  for _ in range(2):fast=self.fast_norm(fast+torch.tanh(self.fast(torch.cat([fast,x,retrieved],-1))))
  hidden=self.slow_norm(fast+retrieved)
  if self.kind=='ice' and write:
   # Only completed boundary state influences later chunks. No within-chunk read-after-write.
   k=q[:,-1];v=self.event_value(fast[:,-1]).tanh();pred=(k[:,None]@memory)[:,0];memory=memory+k[:,:,None]*(v-pred)[:,None,:]
  return hidden,memory
 def forward(self,ids,doc=None,valid=None,trace=False):
  b,t=ids.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  rows=[];states=[]
  for i in range(b):
   out=self.emb.weight.new_zeros(t,self.width);j=0;rowstates=[]
   while j<t:
    if not valid[i,j]:j+=1;continue
    end=j+1
    while end<t and valid[i,end] and doc[i,end]==doc[i,j]:end+=1
    memory=self.emb.weight.new_zeros(1,8,self.width);step=(end-j) if self.kind=='transformer' else self.chunk
    for start in range(j,end,step):
     stop=min(start+step,end);h,memory=self.chunk_hidden(ids[i:i+1,start:stop],memory,write=stop-start==self.chunk);out[start:stop]=h[0];rowstates.append(memory)
    j=end
   rows.append(out);states.append(rowstates)
  logits=F.linear(torch.stack(rows),self.emb.weight)*valid[...,None]
  return (logits,states) if trace else logits
 def step(self,token,state,session_id='session'):
  if self.kind=='transformer':raise ValueError('Full-context control uses explicit full-prefix recomputation; not bounded Session')
  if state.session_id!=session_id:raise ValueError('New session requires explicit reset')
  pending=state.pending+[int(token)];x=torch.tensor([pending],device=self.emb.weight.device);h,mem=self.chunk_hidden(x,state.memory,write=len(pending)==self.chunk)
  logits=F.linear(h[:,-1],self.emb.weight)
  done=len(pending)==self.chunk
  return logits,Session(mem,[] if done else pending,session_id,state.completed+int(done))
def create(kind,seed=17):
 torch.manual_seed(seed);return LanguageBridge(kind=kind)
def loss(logits,ids,doc,valid):
 mask=valid[:,:-1]&valid[:,1:]&(doc[:,:-1]==doc[:,1:]);assert mask.any()
 return F.cross_entropy(logits[:,:-1][mask],ids[:,1:][mask]),int(mask.sum())
def optimizer(m):return torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
