"""Only policy is new. Addressable extraction/value/Delta/read/foreground copied intact."""
import torch
from torch import nn
import torch.nn.functional as F
import trapos_data as D
A=D.S.A
class Trapos(A.Addressable):
 def forward(self,ids,doc=None,valid=None,trace=False,intervention=None,oracle_mask=None,override=None):
  if self.policy!='D' and oracle_mask is not None:raise ValueError('Oracle forbidden in autonomous arms')
  if self.policy=='D' and oracle_mask is None:raise ValueError('Explicit diagnostic oracle required')
  x=self.hidden(ids,doc,valid);b,t,d=x.shape;doc=torch.zeros_like(ids) if doc is None else doc;valid=torch.ones_like(ids,dtype=torch.bool) if valid is None else valid
  idx,keep,reset,*_=self.memory_head._plans(doc,valid,None);n,c=idx.shape[1:]
  xx=x.gather(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d)).reshape(b,n,c,d);tok=ids.gather(1,idx.reshape(b,-1)).reshape(b,n,c)
  memory=x.new_zeros(b,8,d);outs=[];records=[]
  # Stateless random decisions depend only on prefix inside each isolated document.
  prefix=torch.zeros(b,device=ids.device,dtype=torch.long)
  for j in range(n):
   memory=torch.where(reset[:,j,None,None],torch.zeros_like(memory),memory);prefix=torch.where(reset[:,j],torch.zeros_like(prefix),prefix)
   if j==n-1:
    if intervention=='reset':memory=memory*0
    if intervention=='swap':memory=memory.roll(1,0)
   keys=F.normalize(self.address(self.emb(tok[:,j])),dim=-1,eps=1e-6);q=keys.clone()
   for off in range(0,c,4):
    if off+1<c:
     for pos in range(off+1,min(off+4,c)):q[:,pos]=keys[:,off+1]
   read=q@memory;retrieved=self.read(self.address_out(read));fast=xx[:,j]
   for _ in range(2):fast=self.fast_norm(fast+self.fast(torch.cat([fast,xx[:,j],retrieved],-1)).tanh())
   outs.append((fast+retrieved)*keep[:,j,:,None]);before=memory;writes=[]
   for off in range(0,c,4):
    if off+3>=c:continue
    candidate=torch.zeros(b,dtype=torch.bool,device=ids.device)
    for op in D.OPS:candidate|=(tok[:,j,off]==ord(op))
    candidate&=(tok[:,j,off+3]==ord(';'))&keep[:,j,off:off+4].all(-1)
    # The shared extractor does not inspect assertion flags, goal membership or oracle labels.
    score=self.trapos(fast[:,off+3]).squeeze(-1);prob=score.sigmoid()
    for kpos in range(off,off+4):prefix=(prefix*131+tok[:,j,kpos])%2147483647
    rnd=(prefix*1103515245+self.policy_seed*2654435761)%2147483647
    rnd=(rnd*48271+12345)%2147483647
    if self.policy=='C':
     hard=(prob>=.5).to(prob.dtype);gate=hard-prob.detach()+prob if self.training else hard
    elif self.policy=='B':gate=(rnd.double()/2147483647 < self.random_rate).to(prob.dtype)
    elif self.policy=='A':gate=torch.ones_like(prob)
    else:gate=oracle_mask.gather(1,idx[:,j,off+3:off+4])[:,0].to(prob.dtype)
    if override=='all':gate=torch.ones_like(prob)
    elif override=='none':gate=torch.zeros_like(prob)
    gate=gate*candidate
    k=keys[:,off+1];v=self.event_value(fast[:,off+2]).tanh();predicted=(k[:,None]@memory)[:,0]
    new=memory+k[:,:,None]*(v-predicted)[:,None,:]
    old=memory;memory=memory+gate[:,None,None]*k[:,:,None]*(v-predicted)[:,None,:]
    if trace:writes.append({'candidate':candidate,'score':score,'prob':prob,'gate':gate,'key':k,'value':v,'before':old,'after':memory,'end_index':idx[:,j,off+3]})
   if trace:
    if memory.requires_grad:memory.retain_grad()
    records.append({'memory':memory,'before':before,'read':read,'writes':writes,'indices':idx[:,j],'valid':keep[:,j]})
  h=x.new_zeros(b,t,d).scatter_add(1,idx.reshape(b,-1)[...,None].expand(-1,-1,d),torch.stack(outs,1).reshape(b,-1,d));logits=F.linear(self.slow_norm(h),self.emb.weight)*valid[...,None]
  return (logits,records) if trace else logits

def setup(seed,arm,rate=.6):
 m,d,_,_=D.S.setup(seed);source=D.R.parent.parent/'cryo-addressable-stability-v1/stability/results'/f'C-{seed}.pt';s=torch.load(source,weights_only=True,map_location='cpu');m.load_state_dict(s['model'],strict=True)
 m.core.__class__=Trapos;torch.manual_seed(2718+seed);m.core.trapos=nn.Sequential(nn.Linear(32,16),nn.Tanh(),nn.Linear(16,1));m.core.policy=arm;m.core.random_rate=rate;m.core.policy_seed=seed+101
 for p in m.core.trapos.parameters():p.requires_grad_(arm=='C')
 o=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 m.train();return m,o

def inputs(rows):
 x=torch.tensor([r['ids'] for r in rows]);y=torch.tensor([r['label'] for r in rows]);mask=torch.zeros_like(x,dtype=torch.bool)
 for i,r in enumerate(rows):
  for j,pos in enumerate([2,6,10,14,18]):mask[i,pos*4+3]=r['labels'][j]
 return x,y,mask

def forward(m,rows,**kw):
 x,y,mask=inputs(rows)
 # Oracle is confined to the explicit D upper-bound arm.
 return m.core(x,oracle_mask=mask if m.core.policy=='D' else None,**kw)

def selection(tr,rows):
 scores=[];gates=[];labels=[];types=[]
 for chunk in tr:
  for w in chunk['writes']:
   for i in range(len(rows)):
    if w['candidate'][i]:
     pos=int(w['end_index'][i]);j=(pos//4-2)//4;assert pos//4 in [2,6,10,14,18]
     scores.append(w['score'][i]);gates.append(w['gate'][i]);labels.append(rows[i]['labels'][j]);types.append(rows[i]['events'][j]['type'])
 return torch.stack(scores),torch.stack(gates),torch.tensor(labels,dtype=torch.float32),types
