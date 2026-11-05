"""Additional fixed heuristic diagnostics; not used to select checkpoints."""
import json,collections,statistics
from pathlib import Path
import panel
R=Path(__file__).resolve().parent
def first_entity(r):return next((int(v) for op,e,v in r['ops'] if e==r['entity'] and op in '=!'),4)
def presence(r):
 defined=set();goal=None
 for op,e,_ in r['ops']:
  if op in '=!':defined.add(e)
  elif op=='-':defined.discard(e)
  elif op=='>':goal=e
 q=goal if r['query']=='*' else r['query']
 return q,q in defined
def main():
 train=panel.load('train');tables=[];counts=collections.defaultdict(collections.Counter)
 for r in train:counts[presence(r)][r['answer']]+=1
 prior={k:max(c,key=lambda a:(c[a],-a)) for k,c in counts.items()}
 def presence_only(r):
  q,defined=presence(r)
  return prior.get((q,defined),4 if not defined else 0)
 for j in range(64):
  t=collections.defaultdict(collections.Counter)
  for r in train:t[r['ids'][j]][r['answer']]+=1
  tables.append({k:max(c,key=lambda a:(c[a],-a)) for k,c in t.items()})
 out={}
 for split in ['train','iid','compositional','structural','both']:
  rr=panel.load(split);by={}
  for where in ['all','outside','recent']:
   ss=[r for r in rr if where=='all' or r['outside_window']==(where=='outside')]
   by[where]={'n':len(ss),'first_accepted_queried_entity':statistics.mean(first_entity(r)==r['answer'] for r in ss),'presence_only_train_prior':statistics.mean(presence_only(r)==r['answer'] for r in ss),'first_global':statistics.mean(panel.heuristic(r,'first')==r['answer'] for r in ss),'last_global':statistics.mean(panel.heuristic(r,'last')==r['answer'] for r in ss),'last_entity_ignoring_acceptance':statistics.mean(panel.heuristic(r,'entity_last_any')==r['answer'] for r in ss),'accepted_entity_oracle':statistics.mean(panel.heuristic(r,'entity_valid')==r['answer'] for r in ss)}
  by['single_position_train_fitted_accuracy']=[statistics.mean(tables[j].get(r['ids'][j],0)==r['answer'] for r in rr) for j in range(64)]
  by['note']='First-entity resolves goal using declared entity metadata: full-prefix algorithmic control, not a window-equivalent neural model. Maximum over positions is descriptive multiple comparison, not held-out certification.'
  out[split]=by
 (R/'results/additional-shortcuts.json').write_text(json.dumps(out,indent=2))
 print({s:{k:round(v,3) for k,v in d['outside'].items()} for s,d in out.items()})
if __name__=='__main__':main()
