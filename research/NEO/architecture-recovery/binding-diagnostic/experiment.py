from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parent
os.environ['NEO_MEMORY_OUTPUT']=str(ROOT)
sys.path.insert(0,str(ROOT.parent/'memory-bridge'))
from runner import *
TOK=tokenizer()
NAMES=['Nora','Iris','Mira','Luna']
COLORS=['red','white','black','gold']

def rows_for(pair,layout,condition):
 rows=[]
 for a,b,order in itertools.product(range(4),range(4),range(2)):
  if a==b:continue
  values=[a,b];names=[NAMES[e] for e in pair];seq=[0,1] if order==0 else [1,0]
  facts=''.join((f'{names[j]} has {COLORS[values[j]]}. ' if layout==0 else f'{names[j]} holds {COLORS[values[j]]}. ') for j in seq)
  fact=TOK.encode(facts)
  neutral=TOK.encode('People discussed a timetable. A clock stood beside a bench. ')
  neutral=neutral*(96//len(neutral))+[32]*(96%len(neutral))
  prefix=[257]+(neutral+fact if condition=='short' else fact+neutral)
  pid=digest([pair,values,order,layout,condition])
  for side,e in enumerate(pair):
   q=f'What does {names[side]} have? Answer:' if layout==0 else f'What is {names[side]} holding? Answer:'
   choices=[TOK.encode(' '+c)[0] for c in COLORS];assert all(len(TOK.encode(' '+c))==1 for c in COLORS)
   rows.append(dict(prefix=prefix,query=TOK.encode(q),answer=choices[values[side]],choices=choices,gold=values[side],values=values,pair=list(pair),query_side=side,query_entity=e,lang='en',role='formation',layout=layout,distance=len(prefix),program_id=pid,example_id=pid+f'-{side}',order=order,first_value=values[seq[0]],last_value=values[seq[-1]],fact_tokens=len(fact),facts=facts,query_text=q,condition=condition))
 return rows

def datasets(c):return {'train':rows_for((0,1),0,c),'dev-combinations':rows_for((0,2),0,c),'dev-layouts':rows_for((0,1),1,c)}

def metrics(m,rows):
 pred=evaluate(m,rows,'full');a=aggregate(pred);by={r['example_id']:p for r,p in zip(rows,pred)};progs={}
 for r,p in zip(rows,pred):progs.setdefault(r['program_id'],[]).append((r,p))
 a['entity_sides']={str(s):sum(p['correct'] for r,p in zip(rows,pred) if r['query_side']==s)/sum(r['query_side']==s for r in rows) for s in [0,1]}
 a['same_answer_stories']=sum(v[0][1]['pred_id']==v[1][1]['pred_id'] for v in progs.values());a['stories']=len(progs)
 a['first_value_following']=sum(p['pred_value']==r['first_value'] for r,p in zip(rows,pred))/len(rows)
 a['last_value_following']=sum(p['pred_value']==r['last_value'] for r,p in zip(rows,pred))/len(rows)
 a['query_switch_both_correct']=sum(all(p['correct'] for r,p in v) for v in progs.values())/len(progs)
 swaps=[]
 for v in progs.values():
  r=v[0][0]
  if r['values'][0]>r['values'][1]:continue
  donor=next(w for w in progs.values() if w[0][0]['values']==list(reversed(r['values'])) and w[0][0]['order']==r['order'])
  swaps.append(all(p['correct'] for _,p in v+donor))
 a['strict_swap']={'n':len(swaps),'correct':sum(swaps),'accuracy':sum(swaps)/len(swaps)}
 return a,pred

def conditioning(m,rows):
 pair=rows[:2];x,last,_=tensors(pair);mem=torch.zeros(2,8,32)
 captured=[]
 def hook(mod,args,out):out.retain_grad();captured.append(out)
 h=m.emb.register_forward_hook(hook);hidden,_=m.chunk_hidden(x,mem,False);y=F.linear(hidden[torch.arange(2),last],m.emb.weight);F.cross_entropy(y,torch.tensor([r['answer'] for r in pair])).backward();h.remove()
 qstart=len(pair[0]['prefix']);different=(x[0]!=x[1]).nonzero().flatten().tolist();assert different and all(i>=qstart for i in different)
 grad=captured[0].grad
 result={'different_input_positions':different,'prefix_length':qstart,'query_texts':[r['query_text'] for r in pair],'query_ids':[r['query'] for r in pair],'max_logit_delta':float((y[0]-y[1]).abs().max().detach()),'max_hidden_delta':float((hidden[0,last[0]]-hidden[1,last[1]]).abs().max().detach()),'query_embedding_gradient_norm':float(grad[:,qstart:].norm()),'fact_embedding_gradient_norm':float(grad[:,:qstart].norm()),'answer_positions':last.tolist(),'targets':[r['answer'] for r in pair]}
 assert result['query_embedding_gradient_norm']>0 and result['fact_embedding_gradient_norm']>0
 m.zero_grad(set_to_none=True);return result

def contracts(ds):
 short,long=ds['short']['train'],ds['long']['train'];assert len(short)==len(long)==48
 from collections import Counter
 for a,b in zip(short,long):
  assert a['values'][0]!=a['values'][1] and a['query']==b['query'] and a['answer']==b['answer'] and len(a['prefix'])==len(b['prefix'])
  assert Counter(a['prefix'])==Counter(b['prefix'])
 for c in ds:
  for name,rows in ds[c].items():
   assert all(n==6 for n in Counter((r['query_side'],r['gold']) for r in rows).values())
 # End-to-end optimizer/RNG/order/cursor resume for both new datasets.
 for c in ds:
  rows=ds[c]['train'];m=model('full');o=optimizer(m)
  for i in range(3):update(m,o,rows,i,'full')
  checkpoint(ROOT/'results'/f'{c}-resume.pt',m,o,3,rows,'full',17)
  for i in range(3,8):update(m,o,rows,i,'full')
  rng=torch.get_rng_state().clone();m2,o2,cp=restore(ROOT/'results'/f'{c}-resume.pt',rows)
  for i in range(cp['cursor_updates'],8):update(m2,o2,rows,i,'full')
  assert all(torch.equal(v,m2.state_dict()[k]) for k,v in m.state_dict().items()) and torch.equal(rng,torch.get_rng_state())
  for p,q in zip(o.state.values(),o2.state.values()):assert all(torch.equal(p[k],q[k]) if torch.is_tensor(p[k]) else p[k]==q[k] for k in p)
 # Direct future perturbation, isolation and target alignment.
 m=model('full');r=short[:2];x,last,labels=tensors(r);mem=torch.zeros(2,8,32)
 for training in [True,False]:
  m.train(training);h,_=m.chunk_hidden(x,mem,False);xp=x.clone();cut=20;xp[:,cut:]=(xp[:,cut:]+1)%8192;hp,_=m.chunk_hidden(xp,mem,False);assert torch.equal(h[:,:cut],hp[:,:cut])
  lone,_=m.chunk_hidden(x[:1],mem[:1],False);assert torch.allclose(h[:1],lone,atol=1e-6,rtol=1e-5)
 assert all(int(last[i])==len(r[i]['prefix'])+len(r[i]['query'])-1 and int(labels[i])==r[i]['answer'] for i in range(2))
 return {'passed':True,'data_balance':True,'exact_resume_both_conditions':True,'causality_train_eval':True,'isolation':True,'target_alignment':True}

def main():
 ds={c:datasets(c) for c in ['short','long']}
 save_json('datasets',ds);save_json('contracts',contracts(ds))
 save_json('initial-query-conditioning',{c:conditioning(model('full'),ds[c]['train']) for c in ds})
 results={}
 for c in ds:
  m,r=train('full',ds[c]['train'],200,c+'-17');ev={}
  for name,rows in ds[c].items():
   met,pred=metrics(m,rows);ev[name]=met;save_json(c+'-'+name+'-predictions',pred)
  save_json(c+'-evaluations',ev);save_json(c+'-query-conditioning',conditioning(m,ds[c]['train']));results[c]=ev
 save_json('comparison',results)
if __name__=='__main__':main()
