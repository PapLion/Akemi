import json,csv
from pathlib import Path
import trapos_train as T
R=T.R;O=T.O
load=lambda n:json.loads((O/(n+'.json')).read_text())
write=lambda n,s:(R/(n+'.md')).write_text(s.strip()+'\n')
metrics={p.stem.removesuffix('-metrics'):json.loads(p.read_text()) for p in sorted(O.glob('[AC]-??-metrics.json'))}
g=load('gate-17');v1=load('V1-frozen-on-V2-metrics');int1=load('V1-checkpoint-diagnostic');families=list(T.D.dev())
table='| Brazo | Panel | Objetivo activo | Ambas asociaciones | Corregida | Preservada |\n|---|---|---:|---:|---:|---:|\n'
selection='| Brazo | Panel | Precisión | Recall | FPR | Escrituras lógicas |\n|---|---|---:|---:|---:|---:|\n'
rows=[]
for tag,report in metrics.items():
 for fam in families:
  d=report[fam];s=d['selection'];rows.append([tag,fam,d['normal'],d['joint'],d['corrected'],d['preserved'],s['precision'],s['recall'],s['false_positive_rate'],s['accepted_rate']]);table+=f"| {tag} | {fam} | {d['normal']*100:.2f}% | {d['joint']*100:.2f}% | {d['corrected']*100:.2f}% | {d['preserved']*100:.2f}% |\n";selection+=f"| {tag} | {fam} | {s['precision']*100:.2f}% | {s['recall']*100:.2f}% | {s['false_positive_rate']*100:.2f}% | {s['accepted_rate']*100:.2f}% |\n"
with (O/'summary.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['tag','panel','normal','joint','corrected','preserved','precision','recall','fpr','write_rate']);w.writerows(rows)
write('DATA_CONTRACTS','''# Datos y balance

Train: 1.200 programas, dos consultas coherentes cada uno, 2.400 secuencias de 96 IDs y 2.400 respuestas. Cada secuencia tiene cinco propuestas (12.000 targets BCE adicionales solo en C). Ambas consultas comparten íntegro el prefijo de escrituras; el encabezado final indica causalmente el foco. El orden del par durante escrituras no identifica la consulta final. No se suministran entidades/valores del oráculo al forward.

Tres propuestas son válidas (dos hechos iniciales y corrección o repetición), dos inválidas. Estas cruzan las siete combinaciones inválidas de confirmado/negado/pertenencia al ámbito; la octava combinación es la aceptada. No puede balancearse aceptación dentro de una celda donde la definición lógica fija rechazo. Las frecuencias reales por factor, entidad/valor, posición de consulta, opcode y heurísticas se conservan en frequencies-*.json; no se afirma balance perfecto de cada cruce finito ni 50/50 global. Aceptación global60%.

Train excluye el par A–C, usa layouts0/1 y aliases $/#. Dev mantiene ese par fuera de train, añade layouts2/3 y aliases %/&. focus_change fuerza el cambio de foco entre la primera entidad histórica y la segunda conservada; no cambia el ámbito de conservación. clean reemplaza inválidos con repeticiones válidas. Cada panel tiene192 secuencias; no se agregan capacidades de filtración y recuperación en una única puntuación.

Los nuevos paneles no son evaluaciones selladas históricas ni certificación lingüística. La familia dev comparte alfabeto y reglas; sus filas no son réplicas independientes. El oráculo independiente analiza IDs y un diccionario exacto resuelve100%. Esto certifica realizabilidad, no aprendizaje neural.

Se preservó un preflight borrador en preflight-draft: revisión previa al entrenamiento detectó correlación accidental entre identidad consultada y rotación de foco. Se corrigió antes de medir V1 y antes de entrenar V2; el preflight final añade una aserción explícita de balance. No se ajustaron datos mirando resultados V2.
''')
vtable='| Panel | V1 respuesta | V1 conjunta | Precisión | Recall |\n|---|---:|---:|---:|---:|\n'
for fam in families:
 d=v1[fam];vtable+=f"| {fam} | {d['normal']*100:.2f}% | {d['joint']*100:.2f}% | {d['selection']['precision']*100:.2f}% | {d['selection']['recall']*100:.2f}% |\n"
write('V1_DIAGNOSTICS','# Checkpoint V1 inmutable, antes de entrenar V2\n\n'+vtable+'\nHash y coincidencia con heurística de confirmación en V1-checkpoint-diagnostic.json. Falsos positivos desglosados por negación/fuera de ámbito y otros tipos en V1-frozen-on-V2-metrics.json; predicciones por registro conservadas. Se midieron foco cambiado, conservación, layouts y contrafactuales sin actualizar pesos. El cambio de foco es dentro de un ámbito conservado, no una consulta a información previamente excluida.\n')
write('TRAINING_RESULTS','# Contraste A/C ejecutado\n\n'+table+'''\nAmbos parten de los mismos pesos Addressable V1.2 y la misma cabeza inicial, no del C final V1. Receta idéntica a V1: CPU FP32, AdamW0,003, betas0,9/0,95, decay0,01, clipping1, batch8, 300updates; solo C recibe BCE0,1. Checkpoint final fijo, sin selección según dev. Curvas completas, pérdidas y gradientes por update en *-curve.json. La comparación V1/V2 es descriptiva porque cambia la distribución; el contraste causal primario es A/C sobre la distribución nueva.\n''')
write('FILTER_METRICS','# Filtración por separado\n\n'+selection+'\nTP/FP/FN/TN, errores por tipo y cambios reales de Hielo en *-metrics.json. C-17-filter-decisions.json conserva score, decisión, factores y posición por propuesta. final-integrity.json compara decisiones con reglas simples. El extractor es byte-idéntico V1 y entrega todos los candidatos independientemente de la validez; un rechazo deja Hielo exactamente igual. No se confunde aceptar una corrección con rechazar contradicciones.\n')
ivtable='| Panel | Política sobre mismo C | Respuesta normal |\n|---|---|---:|\n'
for p in sorted(O.glob('C-??-interventions.json')):
 for fam,pol in json.loads(p.read_text()).items():
  for name,d in pol.items():ivtable+=f"| {fam} | {p.stem[:4]} {name} | {d['normal']*100:.2f}% |\n"
write('FUNCTIONAL_MEMORY','# Recuperación y controles de política\n\n'+table+'\n'+ivtable+'''\nLas intervenciones usan los mismos pesos C: todo, confirmación, pertenencia al ámbito, confirmado-no-negado, aleatorio y oráculo. No son nuevas trayectorias entrenadas ni un ranking imparcial de recetas. La tasa aleatoria proviene solo de TRAIN final, guardada en C-17-calibration.json. La conjunción determinista coincide con el oráculo por definición del DSL; no puede exigirse superarla ni llamarse selección semántica por imitarla.

Reset y swap compatibles se guardan en cada métricas. Los swaps conservan entidades, estructura y ámbito, cambiando valor vigente; siguen siendo diagnósticos de distribución limitada. La ventana visible final no contiene las propuestas: Hielo es la vía de prefijo, sin KV cache extra. Ambas consultas declaran su foco antes de leer y conservan etiquetas de escritura iguales. No se atribuye automáticamente una diferencia de exactitud conjunta a escritura o filtro.
''')
cf='| Brazo | Panel | Intervención | Pares | Ambos correctos | Invariancia |\n|---|---|---|---:|---:|---:|\n'
for tag,rep in metrics.items():
 for fam,d in rep.items():
  if not isinstance(d,dict) or 'counterfactuals' not in d:continue
  for kind,a in d['counterfactuals'].items():cf+=f"| {tag} | {fam} | {kind} | {a['n']} | {a['joint_correct']*100:.2f}% | {a['prediction_invariance']*100:.2f}% |\n"
write('COUNTERFACTUALS','# Valores válidos, inválidos y obsoletos\n\n'+cf+'\nInvalid cambia solo propuestas rechazables; current cambia valor vigente; obsolete cambia una escritura reemplazada. Se exige acierto en las dos versiones; invariancia por sí sola no es éxito. Las etiquetas se recalculan por oráculo causal, nunca por logits.\n')
cost='| Brazo | Tiempo train s | ms/update | Parámetros | Entrenables | RSS pico KiB |\n|---|---:|---:|---:|---:|---:|\n'
for tag in metrics:
 d=load(tag+'-cost');cost+=f"| {tag} | {d['seconds']:.3f} | {d['seconds']/300*1000:.3f} | {d['parameters']} | {d['trainable']} | {d['rss_kib']} |\n"
write('PERFORMANCE','# CPU\n\n'+cost+'\nLa cabeza sigue teniendo545 parámetros. A la conserva congelada y C la entrena. Los rechazos evitan la modificación de Hielo, pero el código aún calcula proyecciones y candidato Delta; no se afirma ahorro computacional. RSS es máximo acumulado del proceso, no medición aislada por brazo. No se midió CUDA.\n')
write('ENGINEERING','''# Certificación ejecutada

preflight.json: causalidad train/eval de logits y scores, máscaras, aislamiento de documentos/batch, reset, no escritura al rechazar, ecuación Delta intacta al aceptar, gradientes reales del filtro, AdamW sin omisiones/duplicados y actualización real. Reanudación exacta10updates frente4+save+6 en A/B/C/D; B/D son solo fixtures mecánicos, no nuevas trayectorias de300updates.

final-integrity.json: modelo byte-idéntico V1, código preregistrado sin cambios durante campaña, checkpoints finales y estados AdamW restaurados exactamente, inicializaciones A/C iguales, fuentes históricas intactas y consultas emparejadas sin cambiar prefijo/etiquetas. C no puede recibir oracle_mask; solo intervenciones explícitamente D reciben etiquetas de selección.

CPU FP32 monoproceso; no se certifica CUDA/AMP. No se abrió test sellado, no se usó GPU ni servicios pagos.
''')
fail=[k for k,v in g['checks'].items() if not v]
write('DECISION',f'''# Decisión Trapos V2

Piloto semilla17: **{'PASS' if g['passed'] else 'FAIL'}**. Compuertas incumplidas: {fail}.

'''+table+'''\nEl contrato se corrigió antes de entrenar: ambas entidades pertenecen al ámbito de conservación y las consultas/focos se balancean. V1 mezclaba esa semántica legítima con una composición consulta/posición no entrenada; esto no prueba que aquel fuera el único motivo de fallo. A/C distingue entrenamiento con o sin filtro bajo el mismo contrato nuevo; la señal BCE adicional sigue siendo una diferencia declarada.

Si falla alguna compuerta, Trapos V2 se congela: no se ejecutan semillas29/43, no se buscan lambdas, tamaños o arquitecturas. Hielo Addressable conserva su evidencia independiente. Puede continuar el desarrollo lingüístico mediante una ruta determinista/sintáctica explícita, con Trapos desactivado y conservación/restablecimiento documentados; esta alternativa no certifica que detectar acontecimientos en lenguaje libre esté resuelto. No se inicia pretraining ni se levantan sus compuertas de datos y entrenador.

Si el piloto pasa, las confirmaciones29/43 usan la misma receta. Aun así, el resultado sería selección aprendida en un DSL, no comprensión lingüística ni aislamiento térmico completo. La heurística de conjunción es una solución exacta disponible por definición, y nunca debe presentarse el aprendizaje de ese DSL como superioridad sobre ella.
''')
# Preserve initial design, replace only the generated closure on rerun.
readme=(R/'README.md').read_text().split('\n## Ejecución cerrada')[0]
(R/'README.md').write_text(readme.rstrip()+'\n')
with (R/'README.md').open('a') as f:
 f.write('\n## Ejecución cerrada\n\nEstado del piloto: '+('PASS' if g['passed'] else 'FAIL; Trapos congelado, sin más semillas')+'. Evidencia y límites en DECISION.md, resultados en results/summary.csv. Modelo original y resultados V1 preservados.\n\n```bash\nPY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python\n# En copia NUEVA: preflight y train rehúsan sobrescribir evidencia.\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/preflight.py\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/v1_diagnostics.py\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/trapos_train.py\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/final_checks.py\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/make_reports.py\n```\nLos checkpoints locales ignorados por git permanecen en results y están hasheados en SHA256SUMS.\n')
print('REPORTS WRITTEN')
with (R/'DATA_CONTRACTS.md').open('a') as f:
 f.write('''\n## Límites de balance observados\n\nTrain tiene clases de respuesta [620,540,620,620], y el panel base dev [56,40,56,40]. La mayoría dev es29,17%, no25%; focus_change sí tiene48 por valor. El balance de las dos posiciones de consulta es exacto, pero no todos los cruces entidad/posición/valor están completos: por ejemplo, A consultada desde la primera posición no tiene target1 en train. Estos cruces se publican en balance-audit.json y limitan atribuir los errores exclusivamente al filtro. No se corrigen retrospectivamente ni se ejecuta otra trayectoria para perseguir el resultado.\n\nLas frecuencias de respuesta se cuentan por secuencia y las de acontecimientos por propuesta, no se confunden los denominadores. Las combinaciones de factores inválidos son aproximadamente equilibradas, no una factorial exhaustiva de todos los atributos. El contraste mejora el contrato de consulta, pero no certifica cobertura composicional exhaustiva.\n''')
with (R/'DECISION.md').open('a') as f:
 f.write('''\n## Resultado medido y decisión estratégica cerrada\n\nC alcanza85,42% de respuesta base frente79,69% de A (+5,73pp), pero ambas asociaciones solo66,67% frente63,54%. C tiene precisión60,09%, recall97,22% y ejecuta97,08% de escrituras: no aprendió la selección requerida. Acepta54/54 negaciones confirmadas y219/220 propuestas fuera de ámbito, además de perder13/192 correcciones válidas.\n\nEn el MISMO C, forzar todo mejora a87,50%; la regla confirmado-no-negado y el oráculo alcanzan100%. La mejora C/A no es evidencia del beneficio causal de las decisiones aprendidas: la pérdida BCE también cambia las representaciones compartidas y el entrenamiento. La intervención sobre decisiones, limitada al mismo checkpoint/distribución, no favorece la política aprendida. No se aisló una causa única de fallo de optimización.\n\nEl oráculo100% acredita que la ruta funcional de ese checkpoint puede resolver las consultas base cuando se selecciona correctamente; no demuestra robustez universal ni que cada escritura individual sea perfecta. El fracaso de la política persiste bajo la semántica coherente de conservación y consulta; no puede atribuirse únicamente al error de consulta V1. La cobertura condicional incompleta restante limita conclusiones más amplias y queda publicada sin ocultarla.\n\n**Se congela Trapos V2, sin semillas29/43 ni transición a lenguaje natural como filtro aprendido.** Se conserva Hielo Addressable y se separa la investigación del filtro del desarrollo lingüístico. FALLBACK_CONFIG.json prepara la alternativa con escritura sintáctica/determinista original y Trapos desactivado. No declara detección de acontecimientos lingüísticos ni autoriza pretraining; datos, tokenizer, coste y entrenador deben cerrar sus compuertas independientes.\n''')
with (R/'PERFORMANCE.md').open('a') as f:f.write('\nCurvas SVG autocontenidas en results/learning-curves.svg; incluyen valores crudos por microbatch, sin suavizado ni selección del mejor checkpoint. No representan exactitud del corpus train completo.\n')
