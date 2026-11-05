"""Render measured interventions/counterfactuals; no training or sealed data."""
import json,statistics,collections
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 rows=json.loads((R/'results/extend-diagnostics.json').read_text());groups=collections.defaultdict(list)
 for r in rows:groups[(r['config']['arm'],r['config']['window'])].append(r)
 lines=['# Contrafactuales e intervenciones','','Medias de tres semillas; IID + estructural. Ambos correctos exige acertar original y contrafactual. Cambiar el hecho vigente fuera de ventana deja los últimos16IDs idénticos. Un control sin memoria no puede acertar ambas versiones. No usar sensibilidad sola como prueba de utilidad.','','|Modelo/ventana|N pares fuera por semilla: vigente/obsoleto|Vigente ambos correctos|Vigente sensibilidad|Obsoleto ambos correctos|Obsoleto sensibilidad|','|---|---:|---:|---:|---:|---:|']
 for (arm,w),rr in sorted(groups.items()):
  vals=[]
  for kind,key in [('valid','both_correct'),('valid','sensitive'),('obsolete','both_correct'),('obsolete','sensitive')]:vals.append(f"{100*statistics.mean(r['counterfactual_groups'][kind+'/outside/all'][key] for r in rr):.2f}")
  g=rr[0]['counterfactual_groups'];lines.append(f"|{arm}/{w}|{g['valid/outside/all']['n']}/{g['obsolete/outside/all']['n']}|"+'|'.join(vals)+'|')
 lines+=['','## Prueba crítica conjunta de corrección','','Solo replace/multiple fuera de ventana con valor inicial distinto del vigente. Hay que acertar original + cambio obsoleto + cambio vigente en el MISMO ejemplo. Separa contrafactual vigente dentro/fuera del soporte visto por entidad.','','|Modelo/ventana|N tripletes por semilla (todos/visto)|Exactitud tres versiones, todos|Exactitud tres versiones, par visto|','|---|---:|---:|---:|']
 for (arm,w),rr in sorted(groups.items()):
  g=rr[0]['critical_triplet_groups'];v=[statistics.mean(r['critical_triplet_groups'][k]['accuracy'] for r in rr) for k in ['all','seen_pair']]
  lines.append(f"|{arm}/{w}|{g['all']['n']}/{g['seen_pair']['n']}|{100*v[0]:.2f}|{100*v[1]:.2f}|")
 lines+=['','## Intervenciones de inferencia, después del entrenamiento','','Reset/intercambio se aplica al estado justo antes del último fragmento de8IDs. El query no atiende a los outputs híbridos previos: fuera de ventana, reset elimina su ruta declarada de acceso al prefijo. El intercambio usa el vecino del batch y no garantiza respuesta distinta; interpretar como perturbación, no un oráculo contrafactual.','','|Modelo|Semilla|Intervención|N fuera|Exactitud base|Exactitud intervenida|Predicciones cambiadas|','|---|---:|---|---:|---:|---:|---:|']
 for r in rows:
  seed=int(Path(r['checkpoint']).stem.rsplit('-',1)[1])
  for k,v in r['inference_interventions'].items():
   if k.endswith('/outside'):lines.append(f"|{r['config']['arm']}|{seed}|{k}|{v['n']}|{100*v['base_accuracy']:.2f}|{100*v['accuracy']:.2f}|{100*v['changed']:.2f}|")
 (R/'COUNTERFACTUAL_RESULTS.md').write_text('\n'.join(lines)+'\n')
 lines=['# Trapos: observaciones del filtro','','32ejemplos IID estratificados (dos recientes y dos fuera por tarea) por checkpoint. Histórico:64actualizaciones por token; híbridos:8por fragmento. La última escritura híbrida ocurre después de la respuesta y se excluye de estos agregados; permanece en los registros crudos. Categorías superpuestas. Estadística descriptiva condicionada a tarea/posición, sin causalidad identificada de cada dimensión de gate. Todas las actualizaciones densas se ejecutan, independientemente de gate.','','|Modelo|Semilla|Categoría de fragmento|N|Write medio|Erase medio|Delta Hielo|Fracción write<0.05|Fracción write>0.95|','|---|---:|---|---:|---:|---:|---:|---:|---:|']
 for r in rows:
  path=R/r['checkpoint'];gp=path.with_name(path.stem+'-gate-observations.jsonl');obs=[json.loads(s) for s in gp.read_text().splitlines()];obs=[o for o in obs if o.get('granularity')=='token' or o['chunk']<7]
  if not obs:continue
  for name,select in [('todos',lambda t:True),('escritura vigente',lambda t:t['contains_current_valid_write']),('actualización aceptada entidad',lambda t:t['contains_accepted_target_update']),('propuesta rechazada entidad',lambda t:t['contains_rejected_target_proposal'])]:
   ss=[t for t in obs if select(t)]
   if not ss:continue
   vv=[statistics.mean(t[k] for t in ss) if all(t[k] is not None for t in ss) else None for k in ['write_mean','erase_mean','memory_change','write_low_fraction','write_high_fraction']]
   lines.append(f"|{r['config']['arm']}|{path.stem.rsplit('-',1)[1]}|{name}|{len(ss)}|"+'|'.join(f'{v:.4f}' if v is not None else 'no aplica' for v in vv)+'|')
 (R/'GATE_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
