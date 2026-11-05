"""Expose task-specific behavior hidden by a single aggregate accuracy."""
import sys,json,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tasks import load_tokenizer
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'cryo-next-generation/results';panel={r['id']:r for line in (OLD/'panel.jsonl').read_text().splitlines() if (r:=json.loads(line))['split']=='dev'};tok=load_tokenizer();records=[]
paths=[('intact',s,OLD/f'learning-1000/cryo_history-{s}-predictions.jsonl','final') for s in [17,29,43]]
paths += [(p.stem.removesuffix('-predictions').rsplit('-',1)[0],int(p.stem.removesuffix('-predictions').rsplit('-',1)[1]),p,'dev') for folder in ['ablations','capacity','matched','hybrid'] for p in (R/'results'/folder).glob('*-predictions.jsonl')]
for arm,seed,p,stage in paths:
 rows=[json.loads(s) for s in p.read_text().splitlines()];rows=[r for r in rows if r['stage']==stage]
 for task in sorted({r['task'] for r in rows}):
  rr=[r for r in rows if r['task']==task];records.append({'arm':arm,'seed':seed,'task':task,'accuracy':statistics.mean(r['correct'] for r in rr),'first_fact_prediction_rate':statistics.mean(r['prediction']==tok.encode(panel[r['id']]['semantics'][0][2])[0] for r in rr),'n':len(rr)})
(R/'results/task-metrics.json').write_text(json.dumps(records,indent=2));lines=['# Exactitud por tarea\n','Media de tres semillas a1000updates; cada tarea tiene32ejemplos dev por semilla.\n','|Brazo|'+ '|'.join(sorted({r['task'] for r in records}))+'|','|---|'+'---:|'*7]
for arm in dict.fromkeys(r['arm'] for r in records):lines.append('|'+arm+'|'+'|'.join(f"{100*statistics.mean(r['accuracy'] for r in records if r['arm']==arm and r['task']==t):.2f}%" for t in sorted({r['task'] for r in records}))+'|')
(R/'TASK_RESULTS.md').write_text('\n'.join(lines)+'\n\nPredicción del primer hecho, incluido cuando contradice la respuesta correcta: ver JSON. La media global no demuestra corrección de información.\n')
