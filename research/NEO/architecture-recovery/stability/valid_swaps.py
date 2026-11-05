import json
import study as S
out={}
for p in sorted(S.O.glob('[BC]-??-metrics.json')):
 tag=p.stem.removesuffix('-metrics');pred=json.loads((S.O/(tag+'-predictions.json')).read_text());rows=S.evaluation()['held_formation'];base=pred['held_formation'];alt=pred['held_formation-swap'];idx=[i for i,r in enumerate(rows) if r['initial_values'][0]!=r['initial_values'][1]]
 out[tag]={'n':len(idx),'normal_joint_correct':sum(base[i]['prediction']==base[i]['label'] and alt[i]['prediction']==alt[i]['label'] for i in idx)/len(idx),'equal_values_excluded':len(rows)-len(idx)}
S.dump('valid-swaps',out);print(out)
