"""Query-only intervention over frozen V2 full-context foreground and trainer."""
from pathlib import Path
import sys,os
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'binding-diagnostic'))
import experiment as base
import runner
import setup
base.ROOT=HERE
runner.OUT=HERE
setup.OUT=HERE
from experiment import *
ROOT=HERE
from collections import Counter
PROTOCOL=json.loads((ROOT/'PROTOCOL.json').read_text())

def dataset(fmt,condition='short'):
 ds=base.datasets(condition)
 for rows in ds.values():
  for r in rows:
   name=NAMES[r['query_entity']];name_ids=TOK.encode(' '+name);original=r['query'][:]
   starts=[i for i in range(len(original)-len(name_ids)+1) if original[i:i+len(name_ids)]==name_ids];assert len(starts)==1
   i=starts[0];reordered=original[:i]+original[i+len(name_ids):]+name_ids
   r['original_query']=original;r['format']=fmt
   r['query']=original if fmt=='A' else reordered
   r['query_text']=TOK.decode(r['query'])
   assert TOK.encode(r['query_text'])==r['query'] and len(r['query'])==len(original) and Counter(r['query'])==Counter(original)
   if fmt=='B':assert r['query'][-1]==name_ids[-1]
 return ds

def state_sha(m):return digest({k:hashlib.sha256(v.detach().numpy().tobytes()).hexdigest() for k,v in m.state_dict().items()})

def inspect_attention(m,rows):
 x,last,labels=tensors(rows[:2]);b=m.blocks[0];embedding=m.emb(x);z=b.n1(embedding);B,T,D=z.shape;pos=torch.arange(T)[None].expand(B,-1)
 q=b.q(z).view(B,T,b.h,b.a);k=b.k(z).view(B,T,b.kv,b.a);v=b.v(z).view(B,T,b.kv,b.a)
 angle=pos[...,None]*(10000.**(-torch.arange(0,b.a,2).float()/b.a));angle=torch.cat([angle,angle],-1)[:,:,None]
 def rot(v):
  a,c=v.chunk(2,-1);return v*angle.cos()+torch.cat([-c,a],-1)*angle.sin()
 q=rot(q);k=rot(k).repeat_interleave(b.h//b.kv,2);v=v.repeat_interleave(b.h//b.kv,2)
 scores=(q[torch.arange(B),last][:,None]*k).sum(-1)/math.sqrt(b.a)
 scores=scores.masked_fill(torch.arange(T)[None,:,None]>last[:,None,None],float('-inf'));w=scores.softmax(1)
 start=97 if rows[0]['condition']=='short' else 1;end=start+rows[0]['fact_tokens'];fw=w[:,start:end];relative=fw/fw.sum(1,keepdim=True)
 # Check manually reconstructed attention against actual SDPA operation's input to output projection.
 capture=[]
 handle=b.o.register_forward_pre_hook(lambda mod,args:capture.append(args[0].detach()))
 h,_=m.chunk_hidden(x,torch.zeros(B,8,32),False);handle.remove()
 manual=(w[:,:,:,None]*v).sum(1).reshape(B,D)
 assert torch.allclose(manual,capture[0][torch.arange(B),last],atol=2e-6,rtol=1e-5)
 y=F.linear(h[torch.arange(B),last],m.emb.weight)
 # Fact spans from separately tokenized complete sentences; boundaries checked against actual prefix IDs.
 row=rows[0];indices=[0,1] if row['order']==0 else [1,0];lengths=[]
 for side in indices:
  phrase=(f"{NAMES[row['pair'][side]]} has {COLORS[row['values'][side]]}. " if row['layout']==0 else f"{NAMES[row['pair'][side]]} holds {COLORS[row['values'][side]]}. ")
  lengths.append(len(TOK.encode(phrase.rstrip())))
 assert TOK.encode(row['facts'])[:lengths[0]]==TOK.encode(row['facts'].split('. ')[0]+'.')
 lengths[1]=end-start-lengths[0]
 mass=torch.stack([fw[:,:lengths[0]].sum(1),fw[:,lengths[0]:].sum(1)],1)
 mass=mass/mass.sum(1,keepdim=True)
 tensor={'embedding_final':embedding[torch.arange(B),last].detach(),'q_final':q[torch.arange(B),last].detach(),'k_facts':k[:,start:end].detach(),'attention_relative_facts':relative.detach(),'attention_fact_mass':mass.detach(),'logits':y.detach(),'input_ids':x,'answer_positions':last,'labels':labels}
 summary={'query_texts':[r['query_text'] for r in rows[:2]],'final_ids':x[torch.arange(B),last].tolist(),'answer_positions':last.tolist(),'embedding_final_max_delta':float((tensor['embedding_final'][0]-tensor['embedding_final'][1]).abs().max()),'q_max_delta':float((tensor['q_final'][0]-tensor['q_final'][1]).abs().max()),'k_fact_max_delta':float((tensor['k_facts'][0]-tensor['k_facts'][1]).abs().max()),'relative_fact_attention_max_delta':float((relative[0]-relative[1]).abs().max().detach()),'fact_mass_by_query_order_head':mass.detach().tolist(),'logit_max_delta':float((y[0]-y[1]).abs().max().detach()),'manual_sdpa_equivalence':True,'fact_span':[start,end]}
 return summary,tensor

def certify(ds):
 for split in ds['A']:
  for a,b in zip(ds['A'][split],ds['B'][split]):
   assert a['prefix']==b['prefix'] and a['values']==b['values'] and a['answer']==b['answer']
   assert len(a['query'])==len(b['query']) and Counter(a['query'])==Counter(b['query'])
  for fmt in ds:
   rows=ds[fmt][split];assert len(rows)==48
   assert set(Counter((r['query_side'],r['gold']) for r in rows).values())=={6}
   assert rows[0]['query'][-1]==rows[1]['query'][-1] if fmt=='A' else rows[0]['query'][-1]!=rows[1]['query'][-1]
 for fmt in ds:
  rows=ds[fmt]['train'];m=model('full');o=optimizer(m);active=[p for p in m.parameters() if p.requires_grad];assert len({id(p) for g in o.param_groups for p in g['params']})==len(active)
  for step in range(3):update(m,o,rows,step,'full')
  initial={k:v.clone() for k,v in m.state_dict().items()};checkpoint(ROOT/'results'/f'{fmt}-engineering.pt',m,o,3,rows,'full',17)
  for step in range(3,8):update(m,o,rows,step,'full')
  rng=torch.get_rng_state().clone();prng=random.getstate();n,opt,cp=restore(ROOT/'results'/f'{fmt}-engineering.pt',rows)
  for step in range(3,8):update(n,opt,rows,step,'full')
  assert torch.equal(rng,torch.get_rng_state()) and prng==random.getstate()
  assert all(torch.equal(v,n.state_dict()[k]) for k,v in m.state_dict().items())
  assert any(not torch.equal(v,m.state_dict()[k]) for k,v in initial.items())
  for s,t in zip(o.state.values(),opt.state.values()):assert all(torch.equal(s[k],t[k]) for k in s)
  for p in active:assert p.grad is not None and torch.isfinite(p.grad).all()
  x,last,labels=tensors(rows[:2]);assert all(int(last[i])==len(rows[i]['prefix'])+len(rows[i]['query'])-1 and int(labels[i])==rows[i]['answer'] for i in range(2))
  for training in [True,False]:
   m.train(training);mem=torch.zeros(2,8,32);h,_=m.chunk_hidden(x,mem,False);xp=x.clone();xp[:,110:]=(xp[:,110:]+1)%8192;hp,_=m.chunk_hidden(xp,mem,False);assert torch.equal(h[:,:110],hp[:,:110])
   one,_=m.chunk_hidden(x[:1],mem[:1],False);assert torch.allclose(one,h[:1],atol=1e-6,rtol=1e-5)
  altered=[{**r,'answer':r['choices'][(r['gold']+1)%4]} for r in rows[:2]];assert torch.equal(logits(m,rows[:2],'full'),logits(m,altered,'full'))
  conditioning(model('full'),rows)
 return {'passed':True,'token_multisets_equal':True,'target_alignment':True,'balanced_queries':True,'causality_train_eval':True,'batch_isolation':True,'no_target_in_forward':True,'exact_resume_8_vs_3_plus_5':True,'optimizer_finite_gradients_updates':True}

def evaluate_arm(m,ds,tag):
 output={}
 for split,rows in ds.items():
  met,pred=metrics(m,rows);output[split]=met;save_json(tag+'-'+split+'-predictions',pred)
 save_json(tag+'-evaluations',output);return output

def main():
 assert not (ROOT/'results/short-A-17.pt').exists()
 ds={fmt:dataset(fmt) for fmt in ['A','B']};save_json('datasets',ds);save_json('contracts',certify(ds))
 before={};states={};hashes=[]
 for fmt in ds:
  m=model('full');hashes.append(state_sha(m));before[fmt],states[fmt]=inspect_attention(m,ds[fmt]['train'])
 assert hashes[0]==hashes[1];save_json('initial-identity',{'weights_sha':hashes[0],'model_sha':file_sha(BASE/'language-bridge/model.py'),'block_sha':file_sha(BASE/'vendor/cryo_historical.py'),'tokenizer_sha':file_sha(ARTIFACT),'protocol_sha':file_sha(ROOT/'PROTOCOL.json')});save_json('attention-before',before);torch.save(states,ROOT/'results/attention-before.pt')
 comparison={};after={};states={}
 for fmt in ds:
  m,report=train('full',ds[fmt]['train'],200,f'short-{fmt}-17');comparison[fmt]=evaluate_arm(m,ds[fmt],f'short-{fmt}')
  after[fmt],states[fmt]=inspect_attention(m,ds[fmt]['train']);save_json(fmt+'-query-gradients',conditioning(m,ds[fmt]['train']))
 save_json('short-comparison',comparison);save_json('attention-after',after);torch.save(states,ROOT/'results/attention-after.pt')
 gate=all(comparison['B'][s]['joint']['accuracy']>=.9 and comparison['B'][s]['strict_swap']['accuracy']>=.9 for s in ['dev-combinations','dev-layouts'])
 save_json('gate',{'passed':gate,'rule':'joint>=.9 and strict swaps>=.9 on BOTH declared dev sets; engineering already passed','long_experiment':'enabled' if gate else 'NOT EXECUTED','no_extra_seeds':True})
 if gate:
  longds=dataset('B','long');save_json('long-dataset',longds);m,report=train('full',longds['train'],200,'long-B-17');evaluate_arm(m,longds,'long-B')
 else:print('STOP: short-format B failed gate; no long experiment or further training.',flush=True)
if __name__=='__main__':main()
