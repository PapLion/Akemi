from harness import *

def trace(m,rows):
 x,last,labels=tensors(rows);inputs=[];outputs=[];hooks=[]
 for block in m.blocks:
  hooks.append(block.register_forward_pre_hook(lambda mod,args:inputs.append(tuple(a.detach().clone() for a in args))))
  hooks.append(block.register_forward_hook(lambda mod,args,out:outputs.append(out.detach().clone())))
 m.eval()
 with torch.no_grad():hidden,_=m.chunk_hidden(x,torch.zeros(len(rows),8,32),False);y=F.linear(hidden[torch.arange(len(rows)),last],m.emb.weight);embedding=m.emb(x)
 for h in hooks:h.remove()
 layers=[]
 for block,(inp,mask,pos),out in zip(m.blocks,inputs,outputs):
  norm=block.n1(inp);B,T,D=inp.shape;q=block.q(norm).view(B,T,block.h,block.a);k=block.k(norm).view(B,T,block.kv,block.a);v=block.v(norm).view(B,T,block.kv,block.a)
  angle=pos[...,None]*(10000.**(-torch.arange(0,block.a,2).float()/block.a));angle=torch.cat([angle,angle],-1)[:,:,None]
  def rot(z):
   a,b=z.chunk(2,-1);return z*angle.cos()+torch.cat([-b,a],-1)*angle.sin()
  q=rot(q);k=rot(k).repeat_interleave(block.h//block.kv,2);v=v.repeat_interleave(block.h//block.kv,2)
  score=(q[torch.arange(B),last][:,None]*k).sum(-1)/math.sqrt(block.a);selected_mask=mask[torch.arange(B),last];score=score.masked_fill(~selected_mask[:,:,None],float('-inf'));w=score.softmax(1)
  start=len(rows[0]['prefix'])-rows[0]['fact_tokens'];stop=len(rows[0]['prefix']);fw=w[:,start:stop];relative=fw/fw.sum(1,keepdim=True)
  capture=[];hook=block.o.register_forward_pre_hook(lambda mod,args:capture.append(args[0].detach()))
  with torch.no_grad():block(inp,mask,pos)
  hook.remove();manual=(w[:,:,:,None]*v).sum(1).reshape(B,D)
  assert torch.allclose(manual,capture[0][torch.arange(B),last],atol=2e-6,rtol=1e-5)
  assert selected_mask[:,start:stop].all()
  layers.append({'input':inp,'output':out,'q_last':q[torch.arange(B),last].detach(),'k':k.detach(),'v':v.detach(),'relative_fact_attention':relative.detach(),'fact_query_mask':selected_mask[:,start:stop]})
 return {'input_ids':x,'last':last,'embeddings':embedding.detach(),'layers':layers,'final_hidden':hidden.detach(),'logits':y.detach(),'predictions':y.argmax(-1),'labels':labels}

def swap_entity_names(r):
 # Facts retain colour tokens/positions; names are exchanged without changing the query.
 a,b=[NAMES[e] for e in r['pair']];newfacts=r['facts'].replace(a,'__SWAP__').replace(b,a).replace('__SWAP__',b);ids=TOK.encode(newfacts);assert len(ids)==r['fact_tokens']
 values=list(reversed(r['values']));gold=values[r['query_side']]
 return {**r,'prefix':r['prefix'][:-r['fact_tokens']]+ids,'facts':newfacts,'values':values,'gold':gold,'answer':r['choices'][gold]}

def pair_diagnostic(m,rows):
 original=trace(m,rows[:2]);counter=trace(m,[swap_entity_names(r) for r in rows[:2]])
 r=rows[0];start=len(r['prefix'])-r['fact_tokens'];value_positions=[p for p in range(start,len(r['prefix'])) if int(original['input_ids'][0,p]) in r['choices']];assert len(value_positions)==2
 assert torch.equal(original['embeddings'][:,value_positions],counter['embeddings'][:,value_positions])
 metrics={'value_positions':value_positions,'embedding_at_value_delta':0.,'logit_delta_name_swap':float((original['logits']-counter['logits']).abs().max()),'normal_correct':int((original['predictions']==original['labels']).sum()),'names_swapped_correct':int((counter['predictions']==counter['labels']).sum()),'layers':[]}
 for i,(a,b) in enumerate(zip(original['layers'],counter['layers'])):
  metrics['layers'].append({'layer':i,'value_input_delta_name_swap':float((a['input'][:,value_positions]-b['input'][:,value_positions]).abs().max()),'value_output_delta_name_swap':float((a['output'][:,value_positions]-b['output'][:,value_positions]).abs().max()),'value_key_delta_name_swap':float((a['k'][:,value_positions]-b['k'][:,value_positions]).abs().max()),'value_v_delta_name_swap':float((a['v'][:,value_positions]-b['v'][:,value_positions]).abs().max()),'q_delta_query_switch':float((a['q_last'][0]-a['q_last'][1]).abs().max()),'fact_key_delta_query_switch':float((a['k'][0,start:len(r['prefix'])]-a['k'][1,start:len(r['prefix'])]).abs().max()),'relative_attention_delta_query_switch':float((a['relative_fact_attention'][0]-a['relative_fact_attention'][1]).abs().max()),'both_facts_visible':bool(a['fact_query_mask'].all())})
 if len(original['layers'])==2:
  assert torch.equal(original['layers'][0]['output'],original['layers'][1]['input']);metrics['block1_output_equals_block2_input']=True
 return metrics,{'original':original,'swapped_entity_names':counter}

def main():
 ds=data();summary={};snapshots={}
 for arm in P['primary_arms']:
  initial=model(arm);fin,opt,c=restore(ROOT/'results'/f'{arm}-17-final.pt',ds['train']);summary[arm]={};snapshots[arm]={}
  for phase,m in [('initial',initial),('final',fin)]:
   aggregate={s:[] for s in ds};snapshot={}
   for split,rows in ds.items():
    for i in range(0,len(rows),2):
     met,states=pair_diagnostic(m,rows[i:i+2]);aggregate[split].append({'program_id':rows[i]['program_id'],**met})
     if i==0:snapshot[split]=states
   put(f'{arm}-{phase}-contextualization',aggregate);summary[arm][phase]=aggregate['train'][0];snapshots[arm][phase]=snapshot
  # Response gradients to actual token positions; finite, not evidence of semantic use.
  rows=ds['train'][:2];x,last,labels=tensors(rows);emb=[]
  def capture(mod,args,out):out.retain_grad();emb.append(out)
  h=fin.emb.register_forward_hook(capture);y=logits(fin,rows);F.cross_entropy(y,labels).backward();h.remove()
  vp=summary[arm]['final']['value_positions'];summary[arm]['response_gradients']={'value_positions':vp,'value_embedding_gradient_norms':[float(emb[0].grad[:,p].norm()) for p in vp],'query_embedding_gradient_norm':float(emb[0].grad[:,len(rows[0]['prefix']):].norm()),'block_gradient_norms':{n:float(p.grad.norm()) for n,p in fin.named_parameters() if n.startswith('blocks.') and p.grad is not None}}
  fin.zero_grad(set_to_none=True)
 torch.save(snapshots,ROOT/'results/contextualization-states.pt');put('contextualization-summary',summary)
if __name__=='__main__':main()
