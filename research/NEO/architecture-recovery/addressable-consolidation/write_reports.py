"""Reports from recorded measurements only. No training or sealed-data parsing."""
import json,csv,statistics,datetime,hashlib,platform
from pathlib import Path
import runner_v11 as V
R=V.R;O=V.O
load=lambda n:json.loads((O/(n+'.json')).read_text())
def write(name,text):(R/name).write_text(text.strip()+'\n')
def pct(x):return f'{100*x:.2f}%'
def main():
 reports={(arm,seed):load(f'{arm}-{seed}-metrics') for seed in [17,29,43] for arm in ['A','B']}
 rows=[]
 for (arm,seed),d in reports.items():
  for family in ['formation','novel_pairs','correction_fit','correction_fixed','correction_layout','correction_alternate','correction_distractor']:
   x=d[family];rows.append(dict(arm=arm,seed=seed,family=family,n=x['n'],normal=x['normal_accuracy'],initial_joint=x['initial']['joint_accuracy'],post_joint=x['post']['joint_accuracy'],affected=x.get('affected',{}).get('accuracy'),unmodified=x.get('unmodified',{}).get('accuracy')))
 with (O/'summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 primary=load('primary-gate');grid=load('position-grid');shift=load('position-shift-invariance');stats=load('paired-summary');roles=load('functional-role-summary')
 p_present=(O/'P-17-metrics.json').exists();p=load('P-17-metrics') if p_present else None
 table='|Semilla|Brazo|Corrección: lector pares nuevos|Binding corregido (aux)|Binding no modificado (aux)|Lector layout alternativo|Conjunta pares nuevos (formación)|\n|---|---|---:|---:|---:|---:|---:|\n'
 for seed in [17,29,43]:
  for arm in ['A','B']:
   d=reports[arm,seed];c=d['correction_fixed'];table+=f"|{seed}|{arm}|{pct(c['normal_accuracy'])}|{pct(c['affected']['accuracy'])}|{pct(c['unmodified']['accuracy'])}|{pct(d['correction_alternate']['normal_accuracy'])}|{pct(d['novel_pairs']['initial']['joint_accuracy'])}|\n"
 cf='|Semilla|Brazo|Familia|Pareja obsoleto correcta|Invariancia obsoleto|Pareja vigente correcta|Invariancia vigente|\n|---|---|---|---:|---:|---:|---:|\n'
 for seed in [17,29,43]:
  for arm in ['A','B']:
   for family in ['correction_fixed','correction_layout']:
    d=reports[arm,seed][family]['counterfactuals'];a=d['obsolete'];b=d['current'];cf+=f"|{seed}|{arm}|{family}|{pct(a['normal_joint_correct'])}|{pct(a['normal_invariance'])}|{pct(b['normal_joint_correct'])}|{pct(b['normal_invariance'])}|\n"
 performance='|Brazo|Semilla|300 updates (s)|ms/update|Respuestas/s|\n|---|---|---:|---:|---:|\n';total=0
 for seed in [17,29,43]:
  for arm in ['A','B']:
   c=load(f'{arm}-{seed}-cost');sec=c['seconds'];total+=sec;performance+=f'|{arm}|{seed}|{sec:.3f}|{sec/300*1000:.2f}|{2400/sec:.2f}|\n'
 if p_present:
  c=load('P-17-cost');sec=c['seconds'];total+=sec;performance+=f'|P|17|{sec:.3f}|{sec/300*1000:.2f}|{2400/sec:.2f}|\n'
 write('README.md','''# Addressable V1.1 — consolidación por datos

Arquitectura Addressable V1 conservada byte a byte. Experimento ejecutado: control original A frente a50% de correcciones B,300updates por brazo,semilla17; gate prospectivo aprobado y confirmaciones emparejadas29/43 completadas. Diagnóstico de posiciones separado; resultados y límites en DECISION.md.

Todo el trabajo está en esta carpeta y rama cryo-addressable-consolidation-v1, origen7d203aa. Ningún checkpoint original, tokenizer, corpus o evaluación histórica sellada modificado. Sin GPU ni gastos. La nueva familia confirmatoria permanece sellada y sin evaluación de modelos.

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" addressable/test_contracts.py
"$PY" addressable-consolidation/test_data_contracts.py
# Solo en copia nueva de la rama, sin resultados de esta ejecución:
"$PY" addressable-consolidation/preflight.py
"$PY" addressable-consolidation/launch.py
# Si se conserva el launcher inicial que falló en un informe:
"$PY" addressable-consolidation/continue_diagnostics.py
"$PY" addressable-consolidation/position_invariance.py
"$PY" addressable-consolidation/final_checks.py
"$PY" addressable-consolidation/write_reports.py
```

No borrar evidencia para repetir: usar otro worktree y excluir results/ y confirmatory/ del nuevo destino. Los entrenadores rehúsan sobrescribir un checkpoint final. Los.pt locales están ignorados por Git; SHA256SUMS identifica los artefactos necesarios. Fuente histórica cargada con weights_only=True y strict=True. README de V1 conserva ubicación del entorno y dependencias.
''')
 write('TRAINING_PROTOCOL.md','''# Protocolo fijado antes de entrenar

`protocol.json` y results/FREEZE.json registran UTC y hashes de arquitectura,generador,trainer y preflight antes del primer brazo. Semilla17,CPU FP32,un hilo,300updates,batch8,AdamW lr0,003 betas(0,9;0,95),decay0,01,clip1. L=CE_respuesta+0,1 CE_inicial. No supervisión auxiliar posterior ni pérdida nueva.

A: los160registros originales literales y el mismo Random(17).randrange(160). B: mismo índice base, variante=(step*8+slot)%12, seis variantes sin corrección y seis con corrección(2entidades×3transiciones no nulas). 50% correcciones exacto en cada batch; cuatro respuestas nuevas por batch no necesariamente, pues solo la mitad corrige la entidad consultada. Longitud64IDs,consulta final,escrituras iniciales en registros2/3,corrección en8. Cada ejemplo conserva una respuesta y dos targets auxiliares iniciales; cada brazo consume2400/4800targets,153.600IDs de entrada. Supervisión inicial idéntica entre A y B antes de las correcciones. La única intervención primaria es distribución de acontecimientos de entrenamiento.

Las dos copias iniciales son exactamente iguales. A17 termina con modelo,decoder y AdamW exactamente iguales a V1: reconstrucción fuerte del control, no aproximación. Las órdenes de índices base de A/B coinciden los300updates por semilla. B expone1200correcciones adicionales y necesariamente otra distribución de estados/gradientes. No afirmar igualdad de exposición semántica ni de gradientes.

Gates prospectivos: valor corregido≥90% en familias fija/pares nuevos y nuevo layout; no modificada≥95%; intercambios normales y conjuntos≥95%; formación≥95%; conjunta de pares nuevos≥90%; respuestas de formación ambas entidades≥95%,correcciones≥90%; parejas contrafactuales normales≥90%. Ingeniería, no significación estadística. Final update300 fijo, sin búsqueda por dev.

Tras pasar17,confirmaciones A/B29y43 con mismos datos/hiperparámetros. Se reutiliza en cada semilla el warmstart histórico correspondiente(17/29/43), mismas congelaciones; nuevos módulos seed707+(s−17),decoder101+(s−17),sampler s. No son modelos independientes desde cero: comparten familia de datos, arquitectura y entrenamiento histórico; diferencias A/B emparejadas. No se cambian hiperparámetros tras fallos de confirmación.

La evaluación confirmatoria nueva no se usa para estos gates ni se consulta. El tercero P se autoriza solo por el criterio de posición prefijado y compara exclusivamente variedad posicional con B, desde la misma inicialización17.
''')
 f=load('data-frequencies');h=f['heuristics']
 write('CORRECTION_DATA.md',f'''# Datos, balance y separación

Control160programas. Tratamiento1920slots de mezcla, {f['treatment']['unique_programs']}programas únicos: duplicaciones deliberadas ponderan el50% sin corrección. Cinco entidades con pares cíclicos,cuatro valores,16combinaciones×dos órdenes×12variantes. Cada entidad aparece con los cuatro valores y las12transiciones viejo→nuevo diferentes,con frecuencias idénticas por entidad. Tablas exhaustivas desde los targets iniciales y acontecimientos reales en data-frequencies.json. El muestreo finito no garantiza igualdad exacta de frecuencias consumidas; actual-exposure.json registra lo observado.

Oráculo independiente por diccionario y oráculo histórico por prefijo coinciden; etiquetas después de escritura nunca contienen valores futuros. `test_data_contracts.py` verifica todos los prefijos,conservación,contrafactuales y presupuestos. No hay entidades del oráculo dentro del forward: solo etiquetas de pérdida/evaluación.

Dev:formation con inicial6/7;novel_pairs combina entidades no emparejadas en train;correction_fixed usa pares nuevos en mismas posiciones2/3y8;correction_layout mueve inicial6/7ycorrección10;alternate inicial4/5ycorrección10;distractor añade tercera entidad aceptada. Cero programas exactos de entrenamiento en esas familias, comprobado. `correction_fit` coincide intencionalmente con los casos de ajuste y no es un holdout. Las familias dev pueden compartir programas entre sí: no agregarlas como observaciones independientes. Todos los valores individuales son conocidos; la novedad es combinacional/estructural, no vocabulario.

Heurísticas en tratamiento completo: primer valor de entidad consultada {pct(h['treatment']['first_query_entity'])},última escritura global {pct(h['treatment']['last_global'])},presencia sin valores/constante0 {pct(h['treatment']['presence_only_constant0'])},última escritura por entidad100%. Esta última resuelve exactamente el DSL por diseño y constituye el oráculo práctico; no demuestra razonamiento general. Las heurísticas globales no resuelven el panel.

Posiciones,distancias y distractores varían en evaluación. No se mezclan con la intervención primaria de correcciones. P varía posiciones como contraste separado. Nueva confirmatoria:960casos de una estructura separada,initial1/4,corrección9,tercera entidad en6 y pares no cíclicos; solo generación,verificación de oráculo e integridad SHA,ninguna predicción o ajuste. No se declara revisión humana independiente ni se abren sellados anteriores.
''')
 role_table='|Semilla|Brazo|Lector: entidad corregida|Lector: entidad no modificada|\n|---|---|---:|---:|\n'
 for seed in [17,29,43]:
  for arm in ['A','B']:
   z=roles[f'{arm}-{seed}']['correction_fixed'];role_table+=f"|{seed}|{arm}|{pct(z['corrected']['normal_accuracy'])}|{pct(z['preserved']['normal_accuracy'])}|\n"
 write('CONTROL_VS_TREATMENT.md','''# Control frente a tratamiento

'''+table+'\n'+role_table+'''
Cada subgrupo funcional contiene480consultas; las columnas de binding de la primera tabla son del decoder auxiliar y no sustituyen al lector normal. El gate prospectivo usó esos bindings y la respuesta normal agregada; el desglose funcional se reporta además sin redefinir el triaje.

El efecto de añadir correcciones es positivo en la respuesta normal de las tres semillas en pares nuevos, pero falla el requisito de conservación en confirmaciones29y43. Ver summary.csv,predicciones y confusiones por entidad/valor en cada familia. `correction_fit` es ajuste, no prueba de generalización.

Diferencias emparejadas y rangos descriptivos en paired-summary.json. Solo tres semillas; las960variantes por familia reutilizan combinaciones y no son960pruebas independientes. No afirmar robustez poblacional ni inteligencia. El aumento de gradientes por exposición es parte de la intervención de datos, no una modificación del objetivo.
''')
 write('COUNTERFACTUALS.md','''# Contrafactuales y uso funcional

'''+cf+'''
Cada pareja altera solo el hecho obsoleto o el vigente y reconstruye el target con el oráculo. Si se corrige la otra entidad, el vigente de la consulta sigue siendo su escritura inicial: modificarlo debe cambiar la respuesta. Se reportan acierto conjunto e invariancia separadamente; no confundir cambiar de predicción con cambiar a la correcta.

Intercambios de formación:120parejas de valores distintos por modelo. Los JSON contienen criterio estricto de bindings y de respuestas normales, no solo marginales. Consultar ambas entidades separadamente también se registra.

Ablaciones de inferencia:reset y swap compatible antes del último chunk. El compañero mantiene entidades,orden,layout y valor de otra entidad,pero cambia el valor consultado al siguiente. Sin acceso al prefijo en foreground: máscara local16,consulta enIDs60..63,correcciones de familias principales≤43 y demás hechos previos a48. No KV cache ni estados entre llamadas. Las consultas dependen del estado declarado. Se conservan métricas de exactitud,de cambio de predicción y de seguir al compañero.

No se usa el decoder auxiliar en estas respuestas normales. No se atribuye filtrado aprendido a la escritura sintáctica determinista.
''')
 grid_table='|Brazo|Mín.lector rejilla|Máx.lector rejilla|Celdas|\n|---|---:|---:|---:|\n'
 for arm,cells in grid.items():
  vv=[x['normal_accuracy'] for x in cells.values()];grid_table+=f'|{arm}|{pct(min(vv))}|{pct(max(vv))}|{len(vv)}|\n'
 position_extra='No se habilitó P según el criterio prospectivo.'
 if p_present:
  hb=load('B-position-heldout-metrics');hp=load('P-position-heldout-metrics')
  position_extra=f'''Se habilitó un único P17:300updates desde la misma inicialización,no continuación de B. Misma mezcla50%,índices,semántica,targets y receta; inicial alterna(0,1),(2,3),(4,5),corrección6/8/10. La corrección sigue después de formar ambas asociaciones. Cambian inevitablemente estados/contexto y profundidad temporal de gradientes.

Holdout posicional nuevo inicial6/7,corrección11(segunda mitad de chunk): lector B={pct(hb['normal_accuracy'])},P={pct(hp['normal_accuracy'])};valor corregido B={pct(hb['affected']['accuracy'])},P={pct(hp['affected']['accuracy'])};no modificada B={pct(hb['unmodified']['accuracy'])},P={pct(hp['unmodified']['accuracy'])}. P no recibe confirmación multisemilla ni selecciona checkpoint por este resultado. Datos de cada brazo preservados por separado.'''
 write('POSITION_GENERALIZATION.md','''# Generalización de posiciones

'''+grid_table+'''
Rejilla congelada antes del entrenamiento:inicial(0,1),(2,3),(4,5),(6,7),(0,3),(3,6);corrección4,5,6,8,9,10,11,12 cuando está en chunk posterior;ambos órdenes.80casos/celda. Todas corrigen la entidad consultada; la tasa de cambios injustificados de una consulta no modificada no tiene denominador y se marca null. Métricas,confusiones y predicciones completas en position-grid.json y *position-grid-predictions.json. La celda con corrección12 entra en la ventana visible y no acredita retención fuera de ventana. Familias principales y holdout con corrección11 están completamente fuera.

El layout alternativo histórico movía escrituras de fase2/3 a0/1 dentro del bloque local de16IDs; desplazar4registros(16IDs) conserva fase,desplazar2registros(8IDs) la cambia. position-shift-invariance.json verifica sin updates desplazamientos comunes de ambas escrituras y corrección,conservando distancia entre hechos. Esto permite distinguir fase local de una simple posición absoluta en el alcance probado. No generaliza a todas las posiciones posibles.

Cambiar orden puede modificar contexto causal y orden de actualizaciones Delta. Separar chunks también cambia lectura de memoria durante la escritura. No atribuir diferencias exclusivamente a compresión,frontera o a una compuerta. Formato de cuatroIDs permanece constante:no se ha probado parsing de lenguaje natural.

'''+position_extra+'''

B corrige el layout alternativo original sin variar posiciones iniciales de entrenamiento: la cifra56,25% anterior no prueba una incapacidad arquitectónica fija. Exposición a correcciones basta para mejorar esa condición,pero no aísla qué parámetros compartidos produjeron la generalización. No se ha cambiado diseño ni hiperparámetros.
''')
 write('ENGINEERING.md','''# Certificación e integridad

Ocho tests originales PASS y ocho de datos PASS. preflight.json:causalidad train/eval,máscaras de padding,aislamiento de batch y dos documentos,prefijo inicial equivalente,gradientes haciaaddress/event_value,AdamW exactamente cubierto y copias iniciales idénticas. Reanudación continua8updates frente4+checkpoint+4 exactamente igual enA,B,P,conmodelo,decoder,AdamW,RNG torch/Python,sampler,cursor y orden. Configuración y datasets protegidos por hashes al restaurar. La variante de posición es un cambio de datos,con su elección recuperada del step y slot.

Se mantiene el comportamiento del entrenador original:el factory carga el modelo en modo eval,con dropout0 y LayerNorm; las actualizaciones tienen autograd y AdamW. La ruta model.train también fue probada y es causal. No hay BatchNorm ni comportamiento estocástico diferente en la ruta usada. No se hereda certificado CUDA/BF16.

A17 reproduce exactamente pesos,decoder y AdamW finales de Addressable V1. Todas las arquitecturas y el código congelado se verifican sin cambios,así como los85artefactos de SHA256SUMS V1. Iniciales y órdenesA/B exactos por semilla. Checkpoints nuevos y .pt de estados se guardan localmente,consha;no se sobreescriben los originales.

Incidencia preservada:después de completar seis entrenamientos y sus evaluaciones,la rejilla disparó división por cero en `unjustified_changes_A` cuando todos los valores consultados cambiaban. execution.log conserva la excepción. evaluation_guard.py es copia estática del evaluador con solo denominador0→null;reporting-guard.json prueba reproducción del fallo y equivalencia exacta de métricas/predicciones/estados en caso definido. No cambia modelo,targets,tolerancias ni aprendizaje. continue_diagnostics.py usa solo checkpoints completos y entrenaP únicamente si la compuerta prefijada lo habilita. launch_original_preserved.py conserva el launcher anterior;el launcher actual instala ese guard para futuras reproducciones. Los archivos congelados FREEZE permanecen intactos.

No GPU,Vast,Chinchilla,A4,NeoToken ni evaluaciones selladas previas. Nueva confirmatoria permanece sin evaluación;solo se verifica su hash. No se afirma revisión independiente.
''')
 write('PERFORMANCE.md','''# Rendimiento CPU

'''+performance+f'''
Tiempo de actualizaciones medido total:{total:.3f}s. No incluye pruebas,evaluación,escritura de informes ni todo el tiempo de sesión. Tiempos incluyen extracción de pérdidas y logging de gradientes/exposiciones; no son benchmark puro de kernels. RSS de cada cost.json es máximo acumulado del proceso,no medida aislada de cada brazo.

Todos292.067parámetros;284.096entrenables más decoder5.140;Hielo8×32(1KiBFP32porsecuencia). Longitud64,batch8 y número de cálculos dense idénticosA/B: se ejecutan proyecciones y candidatos Delta incluso cuando accepted es falso. Más escrituras aceptadas no implica más operaciones omitidas/ejecutadas aquí; la política usa torch.where, no ahorra selectivamente cómputo. Se registran4800escrituras aceptadasA y6000B por brazo(1200correcciones adicionales). No hay medición de FLOPs por profiler; igualdad de formas y bucles no demuestra igualdad exacta de coste efectivo de autograd.

No se han hecho afirmaciones sobreGPU,modelos50M o calidad lingüística. Estados y logs completos tienen coste de disco medido en final-resources.json.
''')
 b17=reports['B',17];b29=reports['B',29];b43=reports['B',43]
 write('DECISION.md',f'''# Decisión científica

**La exposición a correcciones mejora el uso funcional de Hielo sin rediseñarlo,pero no certifica conservación generalizada fiable.**

Semilla17 supera todos los gates prospectivos y habilita29/43. Las tres semillas aprenden a recuperar la asociación corregida al100% en pares nuevos del diagnóstico;sin embargo,la asociación no modificada queda en{pct(b17['correction_fixed']['unmodified']['accuracy'])},{pct(b29['correction_fixed']['unmodified']['accuracy'])},{pct(b43['correction_fixed']['unmodified']['accuracy'])}. Las confirmaciones29/43 incumplen≥95%. Por el lector normal, la conservación correspondiente es96,46%,79,58%,82,50%; la recuperación del valor corregido es100% en las tres. No declarar consolidación robusta ni ocultar el perjuicio sobre la entidad no modificada en29/43.

La respuesta normal mejora en pares nuevos en las tres semillas;no se trata solo del decoder. Layout alternativo:17y29 llegan100%,43 queda{pct(b43['correction_alternate']['normal_accuracy'])}. Se preservan resultados completos,intercambios y contrafactuales. La nueva confirmatoria sigue sellada.

La arquitectura puede actualizar valores conocidos con una señal de respuesta original:el fallo previo no era una imposibilidad de la reglaDelta. Exposición adicional causa la diferenciaA/B dentro de este diseño emparejado. No se aísla un parámetro ni se demuestra selecciónTrapos:el calendario sigue siendo sintáctico y determinista.

La brecha se concentra en conservar asociaciones no relacionadas al combinar entidades no emparejadas durante train. La regla Delta permite interferencia proporcional al producto entre claves;key-geometry.json aporta una observación representacional,pero no prueba causal por sí sola. No atribuir toda la brecha a claves,saturación o gates sin intervención.

El contraste posicionalP,si se habilitó,está separado;no atribuir su efecto solo a correcciones ni elegirlo como ganador por un holdout. Ver POSITION_GENERALIZATION.md. No más variantes automáticas,semillas extra,arquitecturas ni pretraining.

Siguiente intervención mínima recomendada:otro contraste exclusivamente de datos que incluya cobertura balanceada de pares de entidades y conservación de asociaciones durante correcciones,con las mismas ecuaciones y presupuesto,frente aB. No aumentar slots,dimensiones ni añadir regularizaciones. Antes de promover,exigir repetir conservación≥95% y respuestas conjuntas en combinaciones y estructuras independientes;usar la confirmatoria nueva solo al cerrar decisiones. No ejecutado en esta fase.

El resultado es aprendizaje simbólico de asociaciones y actualización parcial,no lenguaje general ni teoría completa de aislamiento térmico validada.
''')
 V.dump('report-generation.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='recorded final checkpoints and measurements; no sealed evaluation',reports=9,extra_position_arm=p_present))
 print('Reports written from measured results')
if __name__=='__main__':main()
