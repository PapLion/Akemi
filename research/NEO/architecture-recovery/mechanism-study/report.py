"""Summarize every completed arm/seed, never select by best checkpoint."""
import json,statistics,csv
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 rows=[]
 for x in json.loads((R/'results/original-audit.json').read_text()):
  if x['arm']=='cryo_history':
   prior=json.loads((R.parents[1]/'cryo-next-generation/results/learning-1000'/f"cryo_history-{x['seed']}.json").read_text())
   rows.append({'arm':'intact','seed':x['seed'],'dev_accuracy':x['dev_accuracy'],'train_accuracy':statistics.mean(t['accuracy'] for t in prior['metrics']['train_final'].values()),'parameters':x['parameters'],'trainable_parameters':x['parameters'],'train_s':prior['train_s'],'source':'original-reproduced'})
 for p in sorted(p for folder in ['ablations','capacity','matched','hybrid'] for p in (R/'results'/folder).glob('*.json')):
  x=json.loads(p.read_text())
  if 'dev_accuracy' in x:rows.append({k:x.get(k) for k in ['arm','seed','dev_accuracy','train_accuracy','parameters','trainable_parameters','train_s','dev_nll','targets_consumed','per_task']})
 groups={}
 for arm in dict.fromkeys(r['arm'] for r in rows):
  rr=[r for r in rows if r['arm']==arm];v=[r['dev_accuracy'] for r in rr];groups[arm]={'n_seeds':len(rr),'mean':statistics.mean(v),'sd':statistics.stdev(v) if len(v)>1 else None,'seeds':{r['seed']:r['dev_accuracy'] for r in rr},'mean_train_accuracy':statistics.mean(x) if (x:=[r['train_accuracy'] for r in rr if r['train_accuracy'] is not None]) else None}
 (R/'results/summary.json').write_text(json.dumps({'rows':rows,'groups':groups},indent=2))
 with (R/'results/curves.csv').open('w') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['arm','seed','update','loss','batch_accuracy','gradient_norm','update_s'])
  for seed in [17,29,43]:
   prior=json.loads((R.parents[1]/'cryo-next-generation/results/learning-1000'/f'cryo_history-{seed}.json').read_text())
   for u in prior['updates']:w.writerow(['intact',seed,u['update'],u['loss'],u.get('batch_accuracy'),u.get('gradient_norm'),u['update_s']])
  for p in sorted(p for folder in ['ablations','capacity','matched','hybrid'] for p in (R/'results'/folder).glob('*.json')):
   x=json.loads(p.read_text())
   if 'dev_accuracy' not in x:continue
   for u in x['updates']:w.writerow([x['arm'],x['seed'],u['update'],u['loss'],u['batch_accuracy'],u['gradient_norm'],u['update_s']])
 lines=['# Resultados de ablación\n','Todos los finales a1000updates; no mejor checkpoint. Control intacto reproducido desde evidencia original. Semillas faltantes se mantienen pendientes.\n','| Brazo |17|29|43|Media dev|SD pp|Train media|','|---|---:|---:|---:|---:|---:|---:|']
 for arm,g in groups.items():
  fields=[f'{g["seeds"].get(s)*100:.2f}%' if s in g['seeds'] else 'PENDIENTE' for s in [17,29,43]];sd=f'{100*g["sd"]:.2f}' if g['sd'] is not None else '—';tr=f'{100*g["mean_train_accuracy"]:.2f}%' if g['mean_train_accuracy'] is not None else 'Ver original'
  lines.append('|'+ '|'.join([arm]+fields+[f'{100*g["mean"]:.2f}%',sd,tr])+'|')
 (R/'RESULTS.md').write_text('\n'.join(lines)+'\n\n`results/summary.json`, `curves.csv`, checkpoints y predicciones completas permiten inspeccionar cada caso. Dev es generalización composicional simbólica, no lenguaje natural. SD es entre tres semillas, no intervalo de confianza sobre otros corpus.\n')
if __name__=='__main__':main()
