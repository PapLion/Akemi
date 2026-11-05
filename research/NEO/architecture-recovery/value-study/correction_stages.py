"""Post-hoc stage localization restricted to genuine corrected facts.
Avoid comparing a current-value token with a chunk that only contains a rejected proposal.
"""
import json,torch
from pathlib import Path
import data_panel,extract
import value_probes as probes
R=Path(__file__).resolve().parent

def main():
 torch.set_num_threads(1);allrows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};indices={s:[i for i,r in enumerate(rr) if r['present'] and r['regime'] in [1,2] and r['old']!=r['current']] for s,rr in allrows.items()};rows={s:[allrows[s][i] for i in indices[s]] for s in allrows};results=[]
 for arm in ['intact','event_fast','delta_fast']:
  raw=torch.load(R/'results'/f'{arm}-17-normal-trained.pt',weights_only=True)
  for source in ['pooled_write','post_write','memory','read']:
   data={s:probes.features(raw['features'][s],allrows[s],source)[indices[s]] for s in rows}
   for kind in ['linear','mlp']:
    result,p=probes.fit(data,rows,'value',kind);results.append({'arm':arm,'seed':17,'source':source,**result,'predictions':p})
 (R/'results/correction-stages.json').write_text(json.dumps(results)+'\n');print('pure correction stage decoders',len(results))
if __name__=='__main__':main()
