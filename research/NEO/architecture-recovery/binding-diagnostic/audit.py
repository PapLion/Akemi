from experiment import *
from collections import Counter

def attention_audit(m,rows):
 x,last,_=tensors(rows[:2]);b=m.blocks[0];z=b.n1(m.emb(x));B,T,D=z.shape;pos=torch.arange(T)[None].expand(B,-1)
 q=b.q(z).view(B,T,b.h,b.a);k=b.k(z).view(B,T,b.kv,b.a)
 angle=pos[...,None]*(10000.**(-torch.arange(0,b.a,2).float()/b.a));angle=torch.cat([angle,angle],-1)[:,:,None]
 def rot(v):
  a,c=v.chunk(2,-1);return v*angle.cos()+torch.cat([-c,a],-1)*angle.sin()
 q=rot(q);k=rot(k).repeat_interleave(b.h//b.kv,2)
 scores=(q[torch.arange(B),last][:,None]*k).sum(-1)/(b.a**.5)
 scores=scores.masked_fill(torch.arange(T)[None,:,None]>last[:,None,None],float('-inf'));weights=scores.softmax(1)
 boundary=len(rows[0]['prefix']);factstart=97 if rows[0]['condition']=='short' else 1;factstop=factstart+rows[0]['fact_tokens']
 factual=weights[:,factstart:factstop];normalized=factual/factual.sum(1,keepdim=True)
 return {'last_query_vector_max_delta':float((q[0,last[0]]-q[1,last[1]]).abs().max().detach()),'fact_attention_raw_max_delta':float((factual[0]-factual[1]).abs().max().detach()),'fact_relative_attention_max_delta':float((normalized[0]-normalized[1]).abs().max().detach()),'fact_attention_total':[float(v) for v in factual.sum((1,2)).detach()], 'fact_span':[factstart,factstop],'fact_last_to_query_start':boundary-factstop,'query_tokens':len(rows[0]['query']), 'fact_tokens':rows[0]['fact_tokens']}

def main():
 ds={c:datasets(c) for c in ['short','long']};out={};weights=[]
 for c in ds:
  rows=ds[c]['train'];m=model('full');initial={k:v.clone() for k,v in m.state_dict().items()};initialsha=digest({k:hashlib.sha256(v.numpy().tobytes()).hexdigest() for k,v in initial.items()});pre=attention_audit(m,rows)
  m,o,cp=restore(ROOT/'results'/f'{c}-17.pt',rows);weights.append(initialsha)
  idx=order(rows,17);consumed=[rows[idx[(u*8+j)%len(idx)]] for u in range(200) for j in range(8)]
  counts=Counter((r['query_side'],r['gold']) for r in consumed)
  with torch.no_grad():y=logits(m,rows,'full');predict=y.argmax(-1).tolist()
  out[c]={'initial_weights_sha':initialsha,'source_model_sha':file_sha(BASE/'language-bridge/model.py'),'source_block_sha':file_sha(BASE/'vendor/cryo_historical.py'),'tokenizer_sha':file_sha(ARTIFACT),'pre_attention':pre,'post_attention':attention_audit(m,rows),'effective_targets':{str(k):v for k,v in counts.items()},'query_counts':dict(Counter(r['query_side'] for r in consumed)),'target_counts':dict(Counter(r['gold'] for r in consumed)),'prediction_counts':dict(Counter(predict)),'heuristics':{'first_global':.5,'last_global':.5,'query_only_majority':.25,'oracle_entity_lookup':1.},'entity_tokenization':{n:TOK.encode(n) for n in NAMES},'checkpoint_updates':cp['cursor_updates'],'optimizer_states':len(o.state),'active_tensors':sum(p.requires_grad for p in m.parameters()),'checkpoint_cursor_samples':cp['cursor_samples']}
 assert weights[0]==weights[1]
 save_json('post-audit',out)
if __name__=='__main__':main()
