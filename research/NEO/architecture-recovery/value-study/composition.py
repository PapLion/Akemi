"""Post-hoc supplementary split: change distractor identities, keep write positions.
Does not replace the preregistered structural dev or tune decoder settings.
"""
import json,copy,torch
from pathlib import Path
import extract,data_panel
import value_probes as probes
R=Path(__file__).resolve().parent

def generate():
 rows=[]
 for r in data_panel.generate('train'):
  # New binding of distractor entity to same syntax; never alter query entity.
  q=copy.deepcopy(r);e=r['entity'];other='ABCDE'[('ABCDE'.index(e)+2)%5]
  for op in q['ops']:
   if op[1]!=e:op[1]=other
  rr=data_panel.panel.make_record(q['ops'],q['query'],q['task'],'compositional')
  for key in ['old','new','present','corrected','regime','layout','positions','current','entity_index']:rr[key]=r[key]
  rows.append(rr)
 return rows

def main():
 torch.set_num_threads(1);rr=generate();old=data_panel.generate('train');assert not {r['id'] for r in rr}&{r['id'] for r in old}
 (R/'data/compositional-supplement.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rr));rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};rows['compositional']=rr;out=[]
 for arm in ['intact','event_fast','delta_fast']:
  for seed in [17,29,43]:
   for trained in [True,False]:
    key=f'{arm}-{seed}-normal-'+('trained' if trained else 'initial');m,_=extract.load_model(arm,seed,trained=trained);raw=torch.load(R/'results'/f'{key}.pt',weights_only=True);parts=[]
    for i in range(0,len(rr),32):parts.append(extract.observe(m,torch.tensor([r['ids'] for r in rr[i:i+32]]))['states'][:,6])
    data={s:raw['features'][s]['states'][:,6] for s in data_panel.LAYOUTS};data['compositional']=torch.cat(parts)
    for task in ['value','presence']:
     (R/'results/readouts').mkdir(exist_ok=True)
     result,pred=probes.fit(data,rows,task,'linear',save_path=R/'results/readouts'/f'{key}-{task}.pt');out.append({'key':key,**result,'predictions':pred})
    print(key,flush=True)
 (R/'results/compositional-supplement.json').write_text(json.dumps(out)+'\n')
if __name__=='__main__':main()
