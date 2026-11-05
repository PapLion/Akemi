"""Disaggregate value editing from delete->write operation changes, no model runs."""
import json,statistics,argparse
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['extend','ablations'],default='extend',nargs='?');a=p.parse_args();rows=json.loads((R/f'results/{a.stage}-diagnostics.json').read_text());out=[]
 for r in rows:
  cp=R/r['checkpoint'];details=[json.loads(s) for s in cp.with_name(cp.stem+'-counterfactuals.jsonl').read_text().splitlines()];lookup={(t['id'],t['kind']):t for t in details};triplets=[]
  for t in details:
   if t['kind']!='valid' or not t['outside_window'] or t['task'] not in ['replace','multiple'] or t['initial_equals_answer'] or t['operation_changed']:continue
   old=lookup[(t['id'],'obsolete')];triplets.append({'id':t['id'],'heldout_pair':t['changed_pair_heldout'],'correct_all_three':t['both_correct'] and old['changed_correct'],'valid_pair_both_correct':t['both_correct']})
  groups={}
  for name,ss in [('all',triplets),('seen_pair',[t for t in triplets if not t['heldout_pair']]),('heldout_pair',[t for t in triplets if t['heldout_pair']])]:
   groups[name]={'n':len(ss),'correct':sum(t['correct_all_three'] for t in ss),'accuracy':statistics.mean(t['correct_all_three'] for t in ss),'valid_pair_correct':sum(t['valid_pair_both_correct'] for t in ss)}
  out.append({'checkpoint':r['checkpoint'],'config':r['config'],'groups':groups,'triplets':triplets})
 (R/f'results/{a.stage}-value-only.json').write_text(json.dumps({'posthoc_disaggregation':True,'reason':'Delete-to-write changes the operation and cannot certify value binding. Keep original mixed metrics intact.','results':out},indent=2))
 target=R/('VALUE_BINDING.md' if a.stage=='extend' else 'ABLATION_VALUE_BINDING.md');lines=['# Corrección genuina de valores, sin cambio de operación','','Se desagrega después del diagnóstico mixto; se conservan ambos resultados. El modelo debe acertar original, cambio del valor obsoleto y cambio del valor vigente. Solo replace/multiple fuera de ventana con inicial distinto del vigente; el contrafactual mantiene la operación. Los42programas se reutilizan entre semillas: no son126ejemplos independientes.24cambios dejan el par entidad–valor dentro del soporte train,18fuera.','','|Modelo/ventana/modo|Semilla|Tres versiones correctas /42|Dentro de soporte /24|Fuera /18|','|---|---:|---:|---:|---:|']
 for r in out:
  c=r['config'];g=r['groups'];seed=Path(r['checkpoint']).stem.rsplit('-',1)[1];lines.append(f"|{c['arm']}/{c['window']}/{c['mode']}|{seed}|{g['all']['correct']}|{g['seen_pair']['correct']}|{g['heldout_pair']['correct']}|")
 lines+=['','Un cero no demuestra imposibilidad de aprender con otros datos/entrenamiento. Sí impide certificar edición fiable de valores en esta ejecución. Las métricas mixtas positivas por cambios borrado→escritura no se presentan como aprendizaje de valores.']
 target.write_text('\n'.join(lines)+'\n')
 print('value-only audit',a.stage,len(out),'checkpoints')
if __name__=='__main__':main()
