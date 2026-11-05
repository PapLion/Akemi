"""Research-only causal baseline + fast/slow selective recurrent cell. No tokenizer implementation."""
import torch,math
from torch import nn
import torch.nn.functional as F

def language_loss(logits, ids, doc=None, valid=None):
 """Next-token CE, excluding padding and transitions between documents."""
 doc=torch.zeros_like(ids) if doc is None else doc
 valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
 keep=valid[:,:-1]&valid[:,1:]&(doc[:,:-1]==doc[:,1:])
 if not bool(keep.any()):raise ValueError('No valid next-token targets')
 return F.cross_entropy(logits[:,:-1][keep],ids[:,1:][keep])

class Block(nn.Module):
 def __init__(self,d,h=4,kv=2):
  super().__init__();assert d%h==0 and h%kv==0 and (d//h)%2==0
  self.h=h;self.kv=kv;self.a=d//h;self.n1=nn.RMSNorm(d,eps=1e-6);self.n2=nn.RMSNorm(d,eps=1e-6);self.q=nn.Linear(d,d,bias=False);self.k=nn.Linear(d,kv*self.a,bias=False);self.v=nn.Linear(d,kv*self.a,bias=False);self.o=nn.Linear(d,d,bias=False);self.up=nn.Linear(d,8*d,bias=False);self.down=nn.Linear(4*d,d,bias=False)
 def forward(self,x,mask,pos):
  B,T,D=x.shape;y=self.n1(x)
  q=self.q(y).view(B,T,self.h,self.a);k=self.k(y).view(B,T,self.kv,self.a);v=self.v(y).view(B,T,self.kv,self.a)
  angle=pos[...,None]*(10000.**(-torch.arange(0,self.a,2,device=x.device).float()/self.a));angle=torch.cat([angle,angle],-1)[:,:,None]
  def rot(z):
   a,b=z.chunk(2,-1);return z*angle.cos()+torch.cat([-b,a],-1)*angle.sin()
  q=rot(q);k=rot(k).repeat_interleave(self.h//self.kv,2);v=v.repeat_interleave(self.h//self.kv,2)
  z=F.scaled_dot_product_attention(q.transpose(1,2),k.transpose(1,2),v.transpose(1,2),attn_mask=mask[:,None],dropout_p=0.)
  x=x+self.o(z.transpose(1,2).reshape(B,T,D));a,b=self.up(self.n2(x)).chunk(2,-1);return x+self.down(F.silu(a)*b)
def segments(doc,valid):
 reset=torch.ones_like(valid)
 reset[:,1:]=(doc[:,1:]!=doc[:,:-1])|(~valid[:,1:])|(~valid[:,:-1])
 return reset.long().cumsum(1),reset

class Baseline(nn.Module):
 def __init__(self,v=512,d=64,layers=2,dropout=0.):
  super().__init__();self.dropout=nn.Dropout(dropout);self.emb=nn.Embedding(v,d);self.blocks=nn.ModuleList([Block(d) for _ in range(layers)]);self.norm=nn.RMSNorm(d,eps=1e-6)
  self.apply(self.init_weights)
  for b in self.blocks:
   nn.init.normal_(b.o.weight,std=.02/math.sqrt(2*layers));nn.init.normal_(b.down.weight,std=.02/math.sqrt(2*layers))
 @staticmethod
 def init_weights(m):
  if isinstance(m,(nn.Linear,nn.Embedding)):
   nn.init.normal_(m.weight,std=.02)
   if isinstance(m,nn.Linear) and m.bias is not None:nn.init.zeros_(m.bias)
 def hidden(self,ids,doc=None,valid=None):
  B,T=ids.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  seg,_=segments(doc,valid);ar=torch.arange(T,device=ids.device);same=seg[:,:,None]==seg[:,None,:];mask=(ar[:,None]>=ar[None,:])[None]&same&valid[:,None,:]
  # Invalid queries get self only, then are zeroed; avoids undefined all-masked softmax.
  mask=torch.where(valid[:,:,None],mask,torch.eye(T,device=ids.device,dtype=torch.bool)[None]);pos=torch.zeros_like(ids)
  for i in range(1,T):pos[:,i]=torch.where((doc[:,i]==doc[:,i-1])&valid[:,i-1]&valid[:,i],pos[:,i-1]+1,0)
  x=self.dropout(self.emb(ids))
  for b in self.blocks:x=b(x,mask,pos)
  return x*valid[...,None]
 def forward(self,ids,doc=None,valid=None):return F.linear(self.norm(self.hidden(ids,doc,valid)),self.emb.weight)
class CryoTiny(Baseline):
 def __init__(self,v=512,d=64,layers=2,dropout=0.):
  super().__init__(v,d,layers,dropout);del self.norm;self.fast=nn.Linear(3*d,d);self.slow=nn.Linear(2*d,d);self.gate=nn.Linear(2*d,d);self.read=nn.Linear(d,d,bias=False);self.memory_init=nn.Parameter(torch.zeros(d));self.fast_norm=nn.RMSNorm(d,eps=1e-6);self.slow_norm=nn.RMSNorm(d,eps=1e-6)
  for m in [self.fast,self.slow,self.gate,self.read]:self.init_weights(m)
 def forward(self,ids,doc=None,valid=None,return_trace=False):
  x=self.hidden(ids,doc,valid);B,T,D=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  slow=self.memory_init.expand(B,-1);outs=[];trace=[];_,resets=segments(doc,valid)
  for t in range(T):
   reset=resets[:,t]
   slow=torch.where(reset[:,None],self.memory_init[None],slow);fast=x[:,t]
   fast_steps=[fast]
   for _ in range(2):
    fast=self.fast_norm(fast+torch.tanh(self.fast(torch.cat([fast,x[:,t],self.read(slow)],-1))));fast_steps.append(fast)
   z=torch.cat([slow,fast],-1);g=self.gate(z).sigmoid();candidate=torch.tanh(self.slow(z));new=(1-g)*slow+g*candidate;previous=slow;slow=torch.where(valid[:,t,None],new,self.memory_init[None])
   if return_trace:trace.append(dict(previous=previous,fast=fast,fast_steps=fast_steps,gate=g,candidate=candidate,slow=slow,reset=reset))
   outs.append(self.slow_norm(fast+self.read(slow)))
  logits=F.linear(torch.stack(outs,1),self.emb.weight)*valid[...,None]
  return (logits,trace) if return_trace else logits
