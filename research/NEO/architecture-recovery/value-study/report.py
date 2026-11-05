"""Report all executed probes and state interventions, preserving negative outcomes."""
import json,csv,statistics,collections
from pathlib import Path
R=Path(__file__).resolve().parent

def main():
 allrows=[];predrows=[]
 for p in sorted((R/'results/probes').glob('*.json')):
  if p.stem.endswith('predictions'):continue
  d=json.loads(p.read_text());key=d.get('checkpoint_features',d.get('control'));source=d.get('feature','control')
  for r in d['results']:
   for split,m in r['splits'].items():allrows.append(dict(key=key,feature=source,task=r['task'],decoder=r['decoder'],permuted=r['permuted_train'],split=split,**m,parameters=r['parameters']))
   for c in r['curves']:predrows.append(dict(key=key,feature=source,task=r['task'],decoder=r['decoder'],permuted=r['permuted_train'],**c))
 for name,rr in [('probe-metrics.csv',allrows),('probe-curves.csv',predrows)]:
  with (R/'results'/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]),lineterminator='\n');w.writeheader();w.writerows(rr)
 lines=['# Decodificación de Hielo con pesos originales congelados','','Exactitud dev; train y estructural, curvas y predicciones completas en results/probes y CSV. Azar de valor25%, presencia/corregida50%. Cada decoder tiene cabezas separadas por entidad; no necesita inferir la consulta. No se selecciona el mejor hiperparámetro sobre dev. Se publican lineal y MLP32 fijados antes de medir.','','|Estado|Tipo|Presencia lineal|Valor lineal|Valor MLP|Inicial lineal|Corregida lineal|','|---|---|---:|---:|---:|---:|---:|']
 keys=sorted({r['key'] for r in allrows if r['feature']=='memory'})
 for key in keys:
  def get(t,k):return next(r['accuracy'] for r in allrows if r['key']==key and r['feature']=='memory' and r['task']==t and r['decoder']==k and not r['permuted'] and r['split']=='dev')
  lines.append('|'+key+'|Hielo antes de consulta|'+'|'.join(f'{100*get(t,k):.2f}' for t,k in [('presence','linear'),('value','linear'),('value','mlp'),('old','linear'),('corrected','linear')])+'|')
 lines+=['','## Controles','','|Control|Tarea|Dev lineal|','|---|---|---:|']
 for r in allrows:
  if r['feature']=='control' and r['split']=='dev':lines.append(f"|{r['key']}|{r['task']}|{100*r['accuracy']:.2f}|")
 lines+=['','Etiquetas permutadas solo en TRAIN: control negativo sin alterar la verdad dev. Resultados por checkpoint en CSV; tasas altas en train no cuentan como generalización. Inicialización aleatoria comparte algoritmo y capacidad, no es una memoria nula. MLP y decoder condicional pueden extraer información que el modelo original nunca usa. Una exactitud cercana al azar no prueba ausencia de todo código no lineal.']
 (R/'VALUE_DECODING.md').write_text('\n'.join(lines)+'\n')
 # Input-path/reading table for fixed seed17, not selected by performance.
 for filename,title,features in [('WRITE_PATH.md','Localización por etapas de escritura',['after_first','pooled_write','write_value','post_write','memory']),('READ_PATH.md','Memoria y lectura congeladas',['memory','read','local'])]:
  lines=['# '+title,'','Semilla17 prefijada para etapas detalladas; media de logits no sustituye decodificación. Probe por entidad sobre pesos congelados. El readout auxiliar se entrena200updates; el readout original no se modifica. Las proyecciones de candidato se reconstruyen mediante los mismos módulos congelados aplicados a las características observadas, sin sintetizar memoria.','','|Modelo|Etapa|Objetivo|Dev lineal|Dev MLP|','|---|---|---|---:|---:|']
  for arm in ['intact','event_fast','delta_fast']:
   key=f'{arm}-17-normal-trained.pt'
   for feature in features:
    rr=[r for r in allrows if r['key']==key and r['feature']==feature and r['split']=='dev' and not r['permuted']]
    if not rr:continue
    task='old' if feature=='after_first' else 'value';scores={r['decoder']:r['accuracy'] for r in rr if r['task']==task};lines.append(f"|{arm}|{feature}|{task}|{100*scores['linear']:.2f}|{100*scores['mlp']:.2f}|")
  lines+=['','El primer valor y el vigente son variables distintas en correcciones; no comparar sus porcentajes como si midieran el mismo objetivo. Los híbridos escriben por8IDs: post_write incluye el fragmento completo donde cae la corrección, no una actualización ficticia por token. No se ha entrenado una política de escritura nueva ni se ha inyectado memoria explícita en el modelo para afirmar compatibilidad.']
  (R/filename).write_text('\n'.join(lines)+'\n')
 rows=[json.loads(l) for l in (R/'results/interventions.jsonl').read_text().splitlines()];groups=collections.defaultdict(list)
 for r in rows:groups[(r['arm'],r['seed'],r['kind'])].append(r)
 lines=['# Intercambio causal de estados emparejados','','120programas dev con corrección real (inicial distinto del vigente), iguales salvo un valor. Se conserva presencia, estructura y último bloque visible. Donante real del mismo modelo/entidad/layout, no código artificial. Estado tras token55. Sham exacto. Histórico: intervención completa sobre slow antes56; híbridos: sustituir memoria de lectura del último fragmento, cuya escritura posterior no afecta respuestas.','','|Modelo|Seed|Cambio|Distancia relativa media|Predicción original cambia al inyectar|Acierta donante antes/después|L2 logits5|','|---|---:|---|---:|---:|---:|---:|'];summary=[]
 for (arm,seed,kind),rr in sorted(groups.items()):
  mean=lambda f:statistics.mean(f(r) for r in rr)
  v={'arm':arm,'seed':seed,'kind':kind,'n':len(rr),'relative_distance':mean(lambda r:r['relative_l2']),'prediction_changed':mean(lambda r:r['injected_prediction']!=r['prediction']),'donor_accuracy_before':mean(lambda r:r['prediction']==r['donor_answer']),'donor_accuracy_after':mean(lambda r:r['injected_prediction']==r['donor_answer']),'joint_value_follow':mean(lambda r:r['prediction']==r['base_answer'] and r['injected_prediction']==r['donor_answer']),'logits_l2':mean(lambda r:r['logits5_l2'])};summary.append(v)
  lines.append(f"|{arm}|{seed}|{kind}|{v['relative_distance']:.6f}|{100*v['prediction_changed']:.2f}%|{100*v['donor_accuracy_before']:.2f}% / {100*v['donor_accuracy_after']:.2f}%|{v['logits_l2']:.6f}|")
 lines+=['','Distancia positiva acredita sensibilidad representacional, no asociación correcta. El par original debe ser correcto y la intervención seguir el nuevo vigente; joint_value_follow se registra aparte en JSON. Cambiar el obsoleto debería preservar el vigente: que cambien logits no basta para declarar un fallo si la respuesta sigue correcta. Estados reales emparejados reducen, pero no eliminan, el riesgo de incompatibilidad al combinar estados con un receptor; no se declara causalidad universal fuera del alcance de la intervención.']
 (R/'CAUSAL_INTERVENTIONS.md').write_text('\n'.join(lines)+'\n');(R/'results/intervention-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('rendered',len(allrows),'probe rows',len(summary),'intervention groups')
if __name__=='__main__':main()
