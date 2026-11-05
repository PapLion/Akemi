"""Disentangle recovery of current versus obsolete values on actual corrections."""
import json,torch
from pathlib import Path
import data_panel
R=Path(__file__).resolve().parent

def main():
 rows={s:data_panel.generate(s) for s in data_panel.LAYOUTS};out=[]
 for p in sorted((R/'results/probes').glob('*-memory-predictions.json')):
  key=p.stem.removesuffix('-memory-predictions');raw=torch.load(R/'results'/f'{key}.pt',weights_only=True)
  for d in json.loads(p.read_text()):
   if d['task']!='value' or d['decoder']=='permuted-linear':continue
   for split in ['dev','structural']:
    pp=d['predictions'][split];ss=[(rows[split][idx],pred) for idx,pred in zip(pp['indices'],pp['prediction']) if rows[split][idx]['regime'] in [1,2] and rows[split][idx]['old']!=rows[split][idx]['current']]
    out.append({'key':key,'decoder':d['decoder'],'split':split,'n':len(ss),'current_accuracy':sum(pred==r['current'] for r,pred in ss)/len(ss),'obsolete_follow':sum(pred==r['old'] for r,pred in ss)/len(ss),'original_current_accuracy':sum(int(raw['features'][split]['prediction'][rows[split].index(r)])-48==r['current'] for r,pred in ss)/len(ss)})
 (R/'results/current-vs-obsolete.json').write_text(json.dumps(out,indent=2)+'\n')
 print('valid/obsolete rows',len(out))
if __name__=='__main__':main()
