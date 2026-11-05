from runner import *
from data import make,questions,TOK
from collections import Counter
V1=BASE.parent/'cryo-language-bridge-v1/language-bridge/results'

def prefix_states(m,rows,write=True):
 n=max(r['distance'] for r in rows);x=torch.full((len(rows),n),256,dtype=torch.long);memory=m.emb.weight.new_zeros(len(rows),8,32);saved=memory.clone();history=[]
 for i,r in enumerate(rows):x[i,:r['distance']]=torch.tensor(r['prefix'])
 for start in range(0,n,16):
  _,memory=m.chunk_hidden(x[:,start:start+16],memory,write);mask=torch.tensor([r['distance']==start+16 for r in rows]);saved=torch.where(mask[:,None,None],memory,saved);history.append(memory)
 return saved,history

def query_logits(m,rows,memory,mode='normal'):
 n=((max(len(r['query']) for r in rows)+15)//16)*16;x=torch.full((len(rows),n),256,dtype=torch.long);last=torch.tensor([len(r['query'])-1 for r in rows]);hidden=m.emb.weight.new_zeros(len(rows),32);h=memory.clone()
 for i,r in enumerate(rows):x[i,:len(r['query'])]=torch.tensor(r['query'])
 handle=m.read.register_forward_hook(lambda mod,args,out:torch.zeros_like(out)) if mode=='no_read' else None
 try:
  for start in range(0,n,16):
   z,h=m.chunk_hidden(x[:,start:start+16],h,mode!='no_write');hidden=torch.where((last//16==start//16)[:,None],z[torch.arange(len(rows)),last%16],hidden)
 finally:
  if handle:handle.remove()
 return F.linear(hidden,m.emb.weight)

def donor_row(r):
 values=r['values'].copy();values[r['query_side']]=(values[r['query_side']]+1)%4
 offset=(r['initial_values'][r['corrected']]-r['values'][r['corrected']])%4 if r['correction'] else 1
 p=make(tuple(r['pair']),values,r['lang'],r['correction'],offset,r['order'],r['layout'],r['distance'],r['corrected']);return questions(p)[r['query_side']]

def main():
 # Fixed micro checkpoint, no additional optimization after gate failure.
 rows=read('micro');m,o,c=restore(OUT/'results/micro-full-17.pt',rows);pred=read('micro-full-17-train-predictions');by={}
 for r in pred:by.setdefault(r['program'],[]).append(r)
 same=sum(v[0]['pred_id']==v[1]['pred_id'] for v in by.values());on_vocab=all(r['pred_value']>=0 for r in pred)
 short=[]
 for r in rows:short.append({**r,'prefix':[257]+TOK.encode(r['facts']),'distance':len([257]+TOK.encode(r['facts']))})
 shortened=evaluate(m,short,'full');save_json('micro-short-context-inference',{'metrics':aggregate(shortened),'predictions':shortened,'scope':'inference-only after fixed training; changing distance and positions jointly, not an isolated causal effect'})
 paired=[]
 with torch.no_grad():
  for i in range(0,len(rows),2):
   y=logits(m,rows[i:i+2],'full');paired.append({'program':rows[i]['program_id'],'max_logit_difference':float((y[0]-y[1]).abs().max()),'same_argmax':int(y[0].argmax())==int(y[1].argmax())})
 diagnosis={'control_train_accuracy':.5,'control_train_joint':.1875,'all_predictions_are_valid_color_tokens':on_vocab,'query_pairs_same_prediction':same,'query_pairs_n':len(by),'paired_query_logits':paired,'conclusion':'full-context foreground has not learned entity-conditioned retrieval under fixed microfit recipe; not evidence against Hielo; no unique cause isolated','source_versions':{'model':file_sha(BASE/'language-bridge/model.py'),'tokenizer':file_sha(ARTIFACT)},'primary_runs_executed':False}
 # Real V1 checkpoint: audit state and intervention plumbing only; no V2 learning claim.
 old=torch.load(V1/'ice-final.pt',weights_only=True);ice=create('ice');ice.load_state_dict(old['model']);ice.eval();sample=rows[:8]
 with torch.no_grad():
  h,history=prefix_states(ice,sample);direct=logits(ice,sample,'ice');stream=query_logits(ice,sample,h);assert torch.allclose(direct,stream,atol=2e-6,rtol=1e-5)
  donors=[donor_row(r) for r in sample];hd,_=prefix_states(ice,donors);zeros=torch.zeros_like(h);nw,_=prefix_states(ice,sample,False);assert torch.equal(nw,zeros)
  outputs={'normal':stream,'reset':query_logits(ice,sample,zeros),'swap':query_logits(ice,sample,hd),'no_write':query_logits(ice,sample,nw,'no_write'),'no_read':query_logits(ice,sample,h,'no_read')};interventions={}
  for mode,y in outputs.items():
   p=y.argmax(-1);interventions[mode]={'response_accuracy':float((p==torch.tensor([r['answer'] for r in sample])).float().mean()),'follows_donor_value':float((p==torch.tensor([r['answer'] for r in donors])).float().mean()),'max_logit_delta_normal':float((y-stream).abs().max()),'predicted_ids':p.tolist()}
  diagnosis['v1_state_audit']={'checkpoint_sha':file_sha(V1/'ice-final.pt'),'prefix_chunk_state_norms':[float(x.norm()) for x in history],'state_bytes':h.numel()*h.element_size(),'direct_vs_resumed_query_logits_match':True,'query_last_ids':sorted({r['query'][-1] for r in sample}),'query_token_lengths':sorted({len(r['query']) for r in sample}),'interventions':interventions,'scope':'V1 checkpoint never trained on this retrieval objective; selection of 8 mechanical fixtures, not a performance estimate'}
  torch.save({'source_checkpoint_sha':file_sha(V1/'ice-final.pt'),'normal':h,'donor':hd,'zero':zeros,'history':history,'example_ids':[r['example_id'] for r in sample],'tokenizer':FP},OUT/'results/v1-state-audit.pt')
 # Actual answer-loss gradient reaches real H and earlier writes; no target supplied to forward.
 ice.zero_grad();y,states=logits(ice,sample,'ice',True);F.cross_entropy(y,torch.tensor([r['answer'] for r in sample])).backward();diagnosis['v1_answer_gradients']={'first_memory_norm':float(states[0].grad.norm()),'write_value_norm':float(ice.event_value.weight.grad.norm()),'address_norm':float(ice.address.weight.grad.norm()),'reader_norm':float(ice.read.weight.grad.norm())}
 save_json('diagnosis',diagnosis);print(json.dumps(diagnosis,indent=2))
if __name__=='__main__':main()
