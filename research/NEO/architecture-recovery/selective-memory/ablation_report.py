"""All executed policy ablations with matched-order artifact checks."""
import json,statistics,csv
from pathlib import Path
import torch,network
R=Path(__file__).resolve().parent
def main():
 rows=[json.loads(p.read_text()) for p in sorted((R/'results/ablations').glob('*.json'))];values=json.loads((R/'results/ablations-value-only.json').read_text())['results'];lookup={Path(v['checkpoint']).stem:v for v in values};validated=[]
 lines=['# Ablaciones de escritura desde entrenamiento','','Delta elegido en el piloto por17/45 frente a16/45Event; diferencia exploratoria de un ejemplo. Misma inicialización, foreground, IDs, receta y1000updates. Sin lectura equivale al control entrenado noHielo bajo las ecuaciones y tolerancias verificadas; no se duplican sus tres entrenamientos. Reset/intercambio son intervenciones de inferencia, no entrenamientos sin memoria.','','|Política|Semilla|Train|IID|IID fuera|Estructural fuera|Correcciones puras correctas /42|Segundos updates|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for r in rows:
  key=f"{r['arm']}-{r['mode']}-w{r['window']}-{r['seed']}";normal=json.loads((R/f"results/extend/{r['arm']}-normal-w16-{r['seed']}.json").read_text());assert [u['indices'] for u in r['updates']]==[u['indices'] for u in normal['updates']]
  s=torch.load(R/f'results/ablations/{key}.pt',weights_only=True,map_location='cpu');assert s['step']==1000 and s['cursor']==8000 and s['dataset_sha256']==normal['dataset_sha256'];c=s['config'];m=network.build(c['arm'],r['seed'],c['window'],c['mode'],random_budget=c.get('random_budget',.5));m.load_state_dict(s['model'],strict=True);o=network.optimizer(m);o.load_state_dict(s['optimizer']);assert len(o.state)==sum(p.requires_grad for p in m.parameters());assert all(torch.isfinite(t).all() for t in s['model'].values());assert all(int(v['step'])==1000 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in o.state.values())
  validated.append({'checkpoint':key,'matched_order':True,'strict_reload':True,'optimizer_tensors':len(o.state),'config':c})
  mm=r['metrics'];pure=lookup[key]['groups']['all'];lines.append(f"|{r['mode']}|{r['seed']}|{100*mm['train']['accuracy']:.2f}|{100*mm['iid']['accuracy']:.2f}|{100*mm['iid']['outside_accuracy']:.2f}|{100*mm['structural']['outside_accuracy']:.2f}|{pure['correct']}|{r['training_seconds']:.1f}|")
 lines+=['','Always fuerza solo el coeficiente aditivo de escritura a1; retención/borrado y recuperación siguen aprendiendo. No se llama eliminación de todo Trapos. En Delta las filas de control de escritura quedan sin gradiente de datos (32×33=1056parámetros), aunque comparten tensor optimizable con retención/borrado y pueden variar por weight decay. Se conservan para cambiar una sola política, no se cuentan como parámetros funcionales útiles.','','Random, si se ejecutó, usa Bernoulli por ejemplo/fragmento compartida entre características, con media fijada desde gates del piloto. Iguala coeficiente aditivo esperado, no varianza/amplitud de estado, borrado ni FLOPs omitidos. Todos los candidatos se calculan incluso con coeficiente0. La evaluación contrafactual random fija RNG991, conserva tamaño/posición de batches y usa las mismas máscaras para original/twins/reset. Es una realización de evaluación; no certifica promedios sobre infinitas máscaras.','','Los resultados mixtos borrado→escritura permanecen en diagnostics; la tabla aquí exige correcciones de VALOR sin cambiar operación. Ninguna pequeña diferencia global basta para acreditar selección aprendida.']
 (R/'ABLATIONS.md').write_text('\n'.join(lines)+'\n');(R/'results/ablation-artifact-validation.json').write_text(json.dumps(validated,indent=2))
 with (R/'results/ablation-curves.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['arm','mode','seed','step','loss','accuracy','seconds'])
  for r in rows:
   for u in r['updates']:w.writerow([r['arm'],r['mode'],r['seed'],u['step'],u['loss'],u['batch_accuracy'],u['seconds']])
 print('PASS ablation artifacts',len(validated))
if __name__=='__main__':main()
