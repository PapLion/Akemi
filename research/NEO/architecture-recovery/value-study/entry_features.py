"""Post-hoc boundary localization: actual token embedding vs causal hidden at its value."""
import json,torch
from pathlib import Path
import extract,data_panel
import value_probes as probes
R=Path(__file__).resolve().parent

def main():
 torch.set_num_threads(1);rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};results=[]
 for arm in ['intact','event_fast','delta_fast']:
  m,_=extract.load_model(arm,17);data={'embedding':{},'token_hidden':{}}
  for split,rr in rows.items():
   chunks={'embedding':[],'token_hidden':[]}
   for i in range(0,len(rr),32):
    part=rr[i:i+32];x=torch.tensor([r['ids'] for r in part]);idx=torch.tensor([4*r['positions'][2 if r['regime'] in [1,2] else 0]+2 for r in part]);n=torch.arange(len(part))
    with torch.no_grad():chunks['embedding'].append(m.core.emb(x)[n,idx]);chunks['token_hidden'].append(m.core.hidden(x)[n,idx])
   for k in chunks:data[k][split]=torch.cat(chunks[k])
  for source,features in data.items():
   for kind in ['linear','mlp']:
    result,p=probes.fit(features,rows,'value',kind);results.append({'arm':arm,'seed':17,'source':source,**result,'predictions':p})
  print(arm,flush=True)
 (R/'results/entry-boundaries.json').write_text(json.dumps(results)+'\n')
if __name__=='__main__':main()
