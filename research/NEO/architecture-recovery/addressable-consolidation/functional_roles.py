"""Separate original-reader correctness for corrected vs preserved query entities."""
import json,collections
import runner_v11 as V
O=V.O;sets=V.D.dev_sets();report={}
for seed in [17,29,43]:
 for arm in ['A','B']:
  result={}
  for family in ['correction_fit','correction_fixed','correction_layout','correction_alternate','correction_distractor']:
   path=O/f'{arm}-{seed}-{family}.json'
   if not path.exists():continue
   pred=json.loads(path.read_text())['predictions'];rows=sets[family];assert len(pred)==len(rows);rr={}
   for role in ['corrected','preserved']:
    ix=[i for i,r in enumerate(rows) if (r['q']==r['affected'])==(role=='corrected')]
    rr[role]=dict(n=len(ix),normal_accuracy=sum(pred[i]['original_prediction']==pred[i]['original_label'] for i in ix)/len(ix))
   result[family]=rr
  report[f'{arm}-{seed}']=result
V.dump('functional-role-summary.json',report)
print(json.dumps({k:v.get('correction_fixed') for k,v in report.items()},indent=2))
