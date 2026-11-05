"""Descriptive baselines and gate statistics; no fitting of neural models."""
from pathlib import Path
from collections import Counter,defaultdict
import json,statistics
from tasks import oracle
R=Path(__file__).resolve().parent
def main():
 rows=[json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines()];train=[r for r in rows if r['split']=='train'];dev=[r for r in rows if r['split']=='dev'];counts=Counter(r['answer'] for r in train);conditional=defaultdict(Counter)
 for r in train:conditional[(r['entity'],r['query'])][r['answer']]+=1
 pick=lambda c:sorted(c,key=lambda v:(-c[v],v))[0]
 majority=pick(counts);entries=[]
 for r in dev:
  prediction=pick(conditional[(r['entity'],r['query'])]);entries.append({'id':r['id'],'label':r['answer'],'prediction':prediction,'correct':prediction==r['answer']})
 out={'train_answer_counts':dict(counts),'majority_label':majority,'majority_dev_accuracy':statistics.mean(r['answer']==majority for r in dev),'query_entity_lookup_dev_accuracy':statistics.mean(r['correct'] for r in entries),'oracle_accuracy':statistics.mean(oracle(r['semantics'],r['query'],r['entity'])==r['answer'] for r in dev),'uniform_over_eight_reference':.125,'hypothesis_deletion_identifiable':any(oracle([z for z in r['semantics'] if z[0]!='-'],r['query'],r['entity'])!=r['answer'] for r in dev if r['task']=='hypothesis'),'interpretation':'Query/entity lookup ignores context and cannot output held-out queried combinations under this split. This demonstrates a nuisance shortcut, not proof that each neural model uses it.'}
 (R/'results/baseline-diagnostics.json').write_text(json.dumps(out,indent=2));(R/'results/lookup-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in entries))
 gates=[]
 for stage in ['learning','learning-1000']:
  for arm in ['event','delta','event_no_filter','event_always_write']:
   for seed in [17,29,43]:
    p=R/f'results/{stage}/{arm}-{seed}-gates.jsonl'
    if not p.exists():continue
    g=[json.loads(s) for s in p.read_text().splitlines()]
    for relevant in [True,False]:
     sub=[r for r in g if r['task_relevant']==relevant]
     if sub:gates.append({'stage':stage,'arm':arm,'seed':seed,'relevant':relevant,'n':len(sub),'mean_write':statistics.mean(r['write_mean'] for r in sub),'mean_erase':statistics.mean(r['erase_mean'] for r in sub),'mean_state_norm':statistics.mean(r['memory_norm'] for r in sub),'scope':'descriptive gates, not supervised selectivity or evidence of correctness'})
 (R/'results/gate-summary.json').write_text(json.dumps(gates,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
