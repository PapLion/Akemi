"""All-seed reports and paired exploratory statistics, no training or sealed reads."""
import json,statistics,math,random,csv,collections
from pathlib import Path
import panel
R=Path(__file__).resolve().parent
def load(stage):return [json.loads(p.read_text()) for p in sorted((R/'results'/stage).glob('*.json'))]
def main():
 rows=load('extend') or load('pilot');groups=collections.defaultdict(list)
 for r in rows:groups[(r['arm'],r['window'],r['mode'])].append(r)
 lines=['# Resultados completos','', 'CPU FP32. Porcentajes a corte final prefijado, sin elegir el mejor checkpoint. Diferencias de visibilidad y parámetros se informan; no son presupuestos FLOPs iguales. Las filas con una semilla no tienen dispersión estimable.','', '|Modelo/ventana/modo|Semillas|Train|IID|Composición|Estructura|Ambos|IID fuera|Estructura fuera|','|---|---|---:|---:|---:|---:|---:|---:|---:|'];summary=[]
 for (arm,win,mode),rr in sorted(groups.items()):
  val=[];entry={'arm':arm,'window':win,'mode':mode,'seeds':[r['seed'] for r in rr],'metrics':{}}
  for split,key in [('train','accuracy'),('iid','accuracy'),('compositional','accuracy'),('structural','accuracy'),('both','accuracy'),('iid','outside_accuracy'),('structural','outside_accuracy')]:
   vv=[r['metrics'][split][key] for r in rr];mean=statistics.mean(vv);sd=statistics.stdev(vv) if len(vv)>1 else None;entry['metrics'][split+'/'+key]={'values':vv,'mean':mean,'sd':sd};val.append(f'{100*mean:.2f}'+(f' ± {100*sd:.2f}' if sd is not None else ''))
  lines.append(f'|{arm}/{win}/{mode}|'+','.join(str(r['seed']) for r in rr)+'|'+'|'.join(val)+'|');summary.append(entry)
 (R/'RESULTS.md').write_text('\n'.join(lines)+'\n');(R/'results/summary.json').write_text(json.dumps(summary,indent=2))
 lines=['# Resultados por tarea y semilla','','Incluye exactitud fuera de ventana. No mezclar éxito reciente con memoria aprendida.','','|Modelo|Ventana|Semilla|Split|Tarea|N|Exactitud|N fuera|Exactitud fuera|','|---|---:|---:|---|---|---:|---:|---:|---:|'];entity=[]
 for r in rows:
  folder=R/'results'/('extend' if (R/'results/extend').exists() and (R/'results/extend'/f"{r['arm']}-{r['mode']}-w{r['window']}-{r['seed']}.json").exists() else 'pilot');pp=[json.loads(s) for s in (folder/f"{r['arm']}-{r['mode']}-w{r['window']}-{r['seed']}-predictions.jsonl").read_text().splitlines()]
  for split in ['train','iid','compositional','structural','both']:
   for task in panel.TASKS:
    ss=[p for p in pp if p['split']==split and p['task']==task];far=[p for p in ss if p['outside_window']];lines.append(f"|{r['arm']}|{r['window']}|{r['seed']}|{split}|{task}|{len(ss)}|{100*statistics.mean(p['correct'] for p in ss):.2f}|{len(far)}|{100*statistics.mean(p['correct'] for p in far):.2f}|")
   for ent in panel.ENTITIES:
    ss=[p for p in pp if p['split']==split and p['entity']==ent];entity.append({'arm':r['arm'],'window':r['window'],'seed':r['seed'],'split':split,'entity':ent,'n':len(ss),'accuracy':statistics.mean(p['correct'] for p in ss)})
 (R/'TASK_RESULTS.md').write_text('\n'.join(lines)+'\n');(R/'results/entity-results.json').write_text(json.dumps(entity,indent=2))
 with (R/'results/curves.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['arm','mode','window','seed','step','loss','batch_accuracy','gradient_norm','seconds'])
  for r in rows:
   for x in r['updates']:w.writerow([r['arm'],r['mode'],r['window'],r['seed'],x['step'],x['loss'],x['batch_accuracy'],x['gradient_norm'],x['seconds']])
 # Paired case comparisons; no false population p-values with3seeds and correlated program families.
 paired=[]
 for r in rows:
  if r['window']!=16 or r['arm'] not in ['intact','event_fast','delta_fast']:continue
  target=next((a for a in rows if a['arm']=='no_ice' and a['seed']==r['seed'] and a['window']==16),None)
  if target is None:continue
  folder=R/'results'/('extend' if (R/'results/extend'/f"{r['arm']}-normal-w16-{r['seed']}.json").exists() else 'pilot')
  def preds(arm):return {x['id']:x for x in [json.loads(s) for s in (folder/f'{arm}-normal-w16-{r["seed"]}-predictions.jsonl').read_text().splitlines()] if x['split']=='iid' and x['outside_window']}
  a,b=preds(r['arm']),preds('no_ice');assert a.keys()==b.keys();wins=sum(a[k]['correct'] and not b[k]['correct'] for k in a);loss=sum(b[k]['correct'] and not a[k]['correct'] for k in a)
  paired.append({'arm':r['arm'],'seed':r['seed'],'n':len(a),'wins':wins,'losses':loss,'paired_difference':(wins-loss)/len(a),'interpretation':'exploratory same-program contrast; not independent population superiority'})
 (R/'results/paired-statistics.json').write_text(json.dumps(paired,indent=2))
if __name__=='__main__':main()
