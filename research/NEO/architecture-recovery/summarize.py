"""Rebuild tables from all saved runs. Never selects a best seed or checkpoint."""
import json,csv,statistics,collections
from pathlib import Path
from experiment import ARMS
R=Path(__file__).resolve().parent

def avg(d,stage,key):return statistics.mean(x[key] for x in d['metrics'][stage].values())
def main():
 rows=[];tasks=[]
 for stage in ['learning','learning-1000']:
  for arm in ARMS:
   runs=[json.loads(p.read_text()) for seed in [17,29,43] if (p:=R/f'results/{stage}/{arm}-{seed}.json').exists()]
   if not runs:continue
   acc=[avg(d,'final','accuracy') for d in runs]
   row={'stage':stage,'arm':arm,'seeds':len(runs),'parameters':runs[0]['parameters'],'trainable_parameters':runs[0]['trainable_parameters'],'targets_per_seed':runs[0]['targets'],'dev_accuracy':statistics.mean(acc),'dev_accuracy_seed_sd':statistics.stdev(acc) if len(acc)>1 else 0,'dev_accuracy_min':min(acc),'dev_accuracy_max':max(acc),'dev_nll':statistics.mean(avg(d,'final','nll') for d in runs),'train_accuracy':statistics.mean(avg(d,'train_final','accuracy') for d in runs),'train_nll':statistics.mean(avg(d,'train_final','nll') for d in runs),'train_s_mean':statistics.mean(d['train_s'] for d in runs)}
   rows.append(row)
   for task in runs[0]['metrics']['final']:
    tasks.append({'stage':stage,'arm':arm,'task':task,'seeds':len(runs),'dev_accuracy':statistics.mean(d['metrics']['final'][task]['accuracy'] for d in runs),'dev_nll':statistics.mean(d['metrics']['final'][task]['nll'] for d in runs)})
 for name,records in [('learning-summary',rows),('task-summary',tasks),('performance',json.loads((R/'results/performance.json').read_text()))]:
  # Nested seconds/stats serialized as JSON; source JSON remains authoritative.
  fields=list(records[0]);f=(R/f'results/{name}.csv').open('w');writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(records);f.close()
 (R/'results/learning-summary.json').write_text(json.dumps(rows,indent=2));(R/'results/task-summary.json').write_text(json.dumps(tasks,indent=2))
 lines=['# Resultados de aprendizaje CPU','', 'Todos los brazos y semillas; último checkpoint fijado. No selección de mejores casos. Exactitud = argmax sobre 8.192 IDs. SD entre tres semillas no es intervalo de confianza poblacional.','']
 for stage in ['learning','learning-1000']:
  lines+=['## '+stage,'','| Brazo | Semillas | Dev % ± SD | Train % | NLL dev | s entrenamiento/semilla |','|---|---:|---:|---:|---:|---:|']
  for r in rows:
   if r['stage']==stage:lines.append(f"| {r['arm']} | {r['seeds']} | {100*r['dev_accuracy']:.2f} ± {100*r['dev_accuracy_seed_sd']:.2f} | {100*r['train_accuracy']:.2f} | {r['dev_nll']:.3f} | {r['train_s_mean']:.2f} |")
  lines+=['']
 lines+=['## Alcance e interpretación','', '448 documentos train y 224 dev; siete tareas de un DSL con oráculo ejecutable. Cada documento tiene 64 IDs y una sola respuesta supervisada. El primer ensayo consumió 800 targets por brazo/semilla; la extensión exploratoria, 8.000, repitiendo el mismo train. No son 8.000 documentos distintos. Panel, predicciones completas y pérdidas por update permanecen en results/.','', 'La partición exige combinaciones entidad/valor consultadas y estructuras nuevas. Los valores siguen presentes incidentalmente en contexto train. Es un test composicional exigente y artificial, no una evaluación de español/inglés. Una baja loss de train no acredita retención generalizable. El 12,5% es la referencia de escoger uniformemente entre ocho valores, no el azar uniforme entre 8.192 IDs.','', 'La extensión se decidió después de ver el fracaso inicial, se fijó en EXTENSION_PROTOCOL.md y mantuvo los diez brazos, tres semillas, datos y optimizador. No es una confirmación preregistrada desde el primer ensayo. No se ejecuta una tercera extensión automática.','', 'Ver results/task-summary.csv para todas las tareas, results/*-probes para contrafactuales de la extensión y resultados iniciales en results/counterfactual-results.json. Cambiar una predicción tras editar un hecho no basta: se exige acertar ambas respuestas.']
 (R/'LEARNING_RESULTS.md').write_text('\n'.join(lines)+'\n')
 print('Runs summarized:',sum(r['seeds'] for r in rows))
if __name__=='__main__':main()
