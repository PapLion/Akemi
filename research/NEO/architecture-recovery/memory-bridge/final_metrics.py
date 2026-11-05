from runner import *
from collections import Counter

def main():
 rows=read('micro');m,o,c=restore(OUT/'results/micro-full-17.pt',rows);m.eval();pred=read('micro-full-17-train-predictions');by={(tuple(r['values']),r['query_side']):p for r,p in zip(rows,pred)};cf=[]
 for a,b in itertools.combinations(range(4),2):
  predictions=[by[((a,b),j)] for j in [0,1]]+[by[((b,a),j)] for j in [0,1]]
  cf.append({'values':[a,b],'swapped':[b,a],'all_four_responses_correct':all(p['correct'] for p in predictions),'per_query_strict':[predictions[j]['correct'] and predictions[2+j]['correct'] for j in [0,1]],'prediction_values':[p['pred_value'] for p in predictions]})
 total_ce=0.;targets=0
 with torch.no_grad():
  for start in range(0,len(rows),4):
   batch=rows[start:start+4];seq=[r['prefix']+r['query']+[r['answer']] for r in batch];n=max(map(len,seq));x=torch.full((len(batch),n),256,dtype=torch.long);valid=torch.zeros_like(x,dtype=torch.bool)
   for j,ids in enumerate(seq):x[j,:len(ids)]=torch.tensor(ids);valid[j,:len(ids)]=True
   h,_=m.chunk_hidden(x,m.emb.weight.new_zeros(len(batch),8,32),False);y=F.linear(h,m.emb.weight);mask=valid[:,:-1]&valid[:,1:];ce=F.cross_entropy(y[:,:-1][mask],x[:,1:][mask],reduction='sum');total_ce+=float(ce);targets+=int(mask.sum())
 confusion=[[0]*5 for _ in range(4)]
 for p in pred:confusion[p['gold']][p['pred_value'] if p['pred_value']>=0 else 4]+=1
 save_json('final-metrics',{'micro_full':read('micro-full-17')['train'],'micro_full_confusion_gold_rows_pred_columns_last_other':confusion,'counterfactual_pairs':cf,'counterfactual_both_entities_and_swap_accuracy':sum(r['all_four_responses_correct'] for r in cf)/len(cf),'text_nll_micro':{'nll':total_ce/targets,'ppl':math.exp(total_ce/targets),'targets':targets,'scope':'observed controlled prefix+query+answer, training optimized only answers; not natural external dev'},'primary_status':{'full':'NOT EXECUTED','no_ice':'NOT EXECUTED','ice':'NOT EXECUTED','reason':'full-context microfit gate FAIL; no400-update arms, no confirmation seeds'}})
 print('Final metrics recorded; no additional optimization')
if __name__=='__main__':main()
