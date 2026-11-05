import json,statistics
from pathlib import Path
R=Path(__file__).resolve().parent

def replace_append(path,marker,lines):
 old=path.read_text().split(marker)[0];path.write_text(old+'\n'+marker+'\n'+'\n'.join(lines)+'\n')
def main():
 comp=json.loads((R/'results/compositional-supplement.json').read_text());summary=[];lines=['# Resumen por tres semillas','','Probes lineales por entidad, modelos congelados. Dev cambia posiciones; suplemento composicional cambia entidad distractora manteniendo posiciones. Este último se declara post-hoc, no confirmatorio.','','|Modelo|Estado|Presencia dev|Valor dev|Valor estructural|Valor composicional suplemento|','|---|---|---:|---:|---:|---:|']
 for arm in ['intact','event_fast','delta_fast']:
  for trained in ['trained','initial']:
   rows=[]
   for seed in [17,29,43]:
    key=f'{arm}-{seed}-normal-{trained}';d=json.loads((R/'results/probes'/f'{key}-memory.json').read_text());get=lambda task:next(x for x in d['results'] if x['task']==task and x['decoder']=='linear' and not x['permuted_train']);v=get('value');p=get('presence');c=next(x for x in comp if x['key']==key and x['task']=='value');rows.append({'seed':seed,'presence_dev':p['splits']['dev']['accuracy'],'value_dev':v['splits']['dev']['accuracy'],'value_structural':v['splits']['structural']['accuracy'],'value_compositional':c['splits']['compositional']['accuracy']})
   result={'arm':arm,'state':trained,'seeds':rows,'mean':{k:statistics.mean(r[k] for r in rows) for k in rows[0] if k!='seed'},'sd':{k:statistics.stdev(r[k] for r in rows) for k in rows[0] if k!='seed'}};summary.append(result);lines.append(f'|{arm}|{trained}|'+'|'.join(f"{100*result['mean'][k]:.2f} ± {100*result['sd'][k]:.2f}" for k in result['mean'])+'|')
 lines+=['','SD entre tres semillas; los programas son factoriales y se reutilizan. No se suman como muestras independientes ni se declara significación poblacional. Las condiciones inicial/trained están emparejadas, no equivalen a modelos entrenados con otra receta.']
 (R/'REPRESENTATION_SUMMARY.md').write_text('\n'.join(lines)+'\n');(R/'results/representation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 boundary=json.loads((R/'results/entry-boundaries.json').read_text());pure=json.loads((R/'results/correction-stages.json').read_text());lines=['','El punto de entrada usa posición oracular del valor: acceso adicional para localizar, no un mecanismo aprendido.','', '|Modelo|Origen|Decoder|Train|Dev|Estructural|','|---|---|---|---:|---:|---:|---:|']
 for r in boundary+pure:lines.append(f"|{r['arm']}|{r['source']}|{r['decoder']}|{100*r['splits']['train']['accuracy']:.2f}|{100*r['splits']['dev']['accuracy']:.2f}|{100*r['splits']['structural']['accuracy']:.2f}|")
 replace_append(R/'WRITE_PATH.md','## Suplementos: frontera de entrada y correcciones genuinas',lines)
 validity=json.loads((R/'results/current-vs-obsolete.json').read_text());lines=['','Casos presente/corregido con inicial≠vigente, dev estructural. Exactitud de valor frente a copiar obsoleto; mismo decoder y semilla.','', '|Checkpoint|Decoder|Vigente probe|Obsoleto probe|Vigente modelo original|','|---|---|---:|---:|---:|']
 for r in validity:
  if 'normal-trained' in r['key'] and r['split']=='dev':lines.append(f"|{r['key']}|{r['decoder']}|{100*r['current_accuracy']:.2f}|{100*r['obsolete_follow']:.2f}|{100*r['original_current_accuracy']:.2f}|")
 replace_append(R/'READ_PATH.md','## Vigente frente a obsoleto',lines)
 print('summary complete')
if __name__=='__main__':main()
