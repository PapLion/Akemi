import json,csv,statistics,hashlib
from pathlib import Path
import trapos_train as T
R=T.R;O=T.O
load=lambda n:json.loads((O/(n+'.json')).read_text())
metrics={p.stem.removesuffix('-metrics'):json.loads(p.read_text()) for p in sorted(O.glob('[ABCD]-??-metrics.json'))}
gate=load('gate-17');seeds=sorted({int(k.split('-')[1]) for k in metrics})
def write(n,t):(R/(n+'.md')).write_text(t.strip()+'\n')
rows=[]
for tag,met in metrics.items():
 for fam in ['contaminated_pair','layout','surface','clean']:
  d=met[fam];s=d['selection'];rows.append([tag,fam,d['normal'],d['joint'],d['corrected'],d['preserved'],s['precision'],s['recall'],s['accepted_rate']])
with (O/'summary.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['arm_seed','family','normal','joint','corrected','preserved','selection_precision','selection_recall','state_write_fraction']);w.writerows(rows)
table='| Brazo | Familia | Respuesta normal | Ambas consultas | Corregida | Preservada |\n|---|---|---:|---:|---:|---:|\n'
for tag,fam,a,j,c,p,*_ in rows:table+=f'| {tag} | {fam} | {a*100:.2f}% | {j*100:.2f}% | {c*100:.2f}% | {p*100:.2f}% |\n'
selection='| Brazo | Familia | Precisión | Recall | Escrituras lógicas |\n|---|---|---:|---:|---:|\n'
for tag,fam,a,j,c,p,precision,recall,rate in rows:selection+=f'| {tag} | {fam} | {precision*100:.2f}% | {recall*100:.2f}% | {rate*100:.2f}% |\n'
write('README',f'''# Trapos V1 — selección sobre Addressable

Rama `cryo-trapos-selection-v1`, desde `5f2a166`. Prototipo implementado y CPU ejecutado. {'Piloto aprobado; confirmaciones preregistradas habilitadas.' if gate['passed'] else 'Piloto negativo: no se habilitaron semillas 29/43.'} Semillas ejecutadas: {seeds}. Resultados funcionales y decisión en DECISION.md.

El diseño de Hielo, Delta, key/value, lector y foreground se conserva. Solo se añade una cabeza de aceptación de 545 parámetros. El extractor compartido ofrece también propuestas inválidas. No se usa lenguaje natural, tokenizer, corpus ni GPU. No se abrió evaluación sellada.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# Reproducción únicamente en copia nueva sin resultados; nunca borrar esta evidencia.
"$PY" trapos/preflight.py
"$PY" trapos/trapos_train.py
"$PY" trapos/final_checks.py
"$PY" trapos/reports.py
```

Los checkpoints .pt se conservan localmente e identifican por SHA256SUMS. El entrenador rechaza sobrescribir un checkpoint final y el preflight rechaza sobrescribir FREEZE. Fuentes y datos históricos son de solo lectura.
''')
write('THEORY',r'''# Teoría y ecuaciones

Primer plano: foreground causal histórico. Hielo: matriz acotada H∈R^(8×32). Trapos: decisión aprendida que controla incorporación de propuestas, no memoria externa de PA/RAG ni fenómeno termodinámico literal.

Se conserva k=normalize(W_address embedding(entidad)), v=tanh(W_value fast_valor), lectura qᵀH, address_out/read y dos refinamientos rápidos normalizados. La única modificación es:

H' = H + a · k (v − kᵀH)ᵀ.

El predictor de aceptación es z=W₂ tanh(W₁ fast_fin_registro+b₁)+b₂, p=sigmoid(z), a_hard=1[p≥0,5]. Durante train se usa a=a_hard−stopgrad(p)+p: forward discreto, derivada sustituta sigmoide. **Estimador sesgado straight-through**, no gradiente exacto de una decisión discreta ni REINFORCE. Evaluación hard determinista. BCE auxiliar 0,1 supervisa aceptación con etiquetas de prefijo; la respuesta usa CE original.

La escritura solo ocurre tras cerrar un registro candidato y afecta tokens de chunks posteriores. El score utiliza el estado causal de fin de registro, nunca una agregación futura. Un rechazo a=0 deja H exactamente igual. El extractor aplica solo framing/opcode compartido; no comprueba verdad, negación, objetivo ni etiquetas.

La aceptación oracular significa afirmación confirmada, no negada, y entidad dentro del objetivo disponible antes del evento. Las repeticiones válidas son aceptables y deben preservar su valor; no se ha intentado aprender rechazo por redundancia. No hay cabezas separadas de sorpresa/contradicción/confianza.
''')
write('SELECTION_PROTOCOL',json.dumps(T.PROTOCOL,indent=2,ensure_ascii=False)+'''

Interpretación de «congelar Hielo»: se congelan sus ecuaciones, dimensiones y organización, no todos sus pesos. Los parámetros compartidos parten idénticos de C V1.2 por semilla y siguen entrenables en los cuatro brazos. Solo C entrena la cabeza adicional; A/B/D la instancian idéntica pero congelada. No se atribuye por ello cualquier ganancia exclusivamente a la arquitectura: se evalúa la intervención sobre decisiones del mismo C.

Los ejemplos y su orden son idénticos por semilla. El control B se calibra después de entrenar C, exclusivamente sobre TRAIN, con la política final hard; nunca usa dev. Se registra fracción prevista y realizada. Sus decisiones son un hash pseudoaleatorio causal del prefijo por documento y semilla, estable entre batches y reanudaciones. No usa etiquetas ni el objetivo futuro.

D recibe explícitamente la máscara oracular: límite superior asistido, no resultado autónomo. La API prohíbe suministrar oracle_mask a A/B/C. C recibe 12.000 targets de aceptación extra frente a cero en A/B/D. La diferencia de supervisión es intencionada y declarada; no constituye comparación de igual señal total de entrenamiento.
''')
write('DATA_CONTRACTS','''# Datos

96 IDs ASCII por secuencia, 24 registros de cuatro IDs. Cinco bloques contienen objetivo @XY;, dos bits de confirmación/negación, una propuesta y relleno. El sexto bloque contiene la consulta. Todos los hechos relevantes terminan antes de la ventana activa final IDs 80–95; no hay KV cache ni lectura oculta.

Cada secuencia contiene dos asociaciones válidas, un evento de corrección o repetición y dos propuestas inválidas. Estas últimas incluyen hipótesis, citas no confirmadas, negaciones y afirmaciones fuera del objetivo. El objetivo es causal y explícito; cambia entre secuencias, no durante una secuencia. Semántica de objetivo dinámico queda pendiente. Cada opcode candidato aparece tanto en casos aceptados como rechazados: un único opcode no basta. No se afirma eliminar todos los atajos posibles en un DSL tan pequeño.

Train excluye por completo el par A–C. Dev usa A–C: layout conocido, layouts nuevos 2/3, aliases de marcador de modo %/& no entrenados y escenario limpio. Los cinco opcodes =!~^+ se comparten en la gramática; los aliases nuevos mantienen los mismos campos y bits. No se exige inferir el significado arbitrario de tokens sin contrato: se prueba transferencia de framing declarado, no comprensión libre.

Los conteos reales, targets, duplicados exactos, distribución entidad/valor, tasas de aceptación y heurísticas primera/última global/última por entidad/presencia están en frequencies-*.json. La distribución de roles y longitud se fija; las celdas finitas entidad/valor no son todas exactamente iguales. El panel dev no se considera estadísticamente independiente por cada fila: comparte símbolos y estructuras. No se abrió ningún conjunto sellado.

El oráculo independiente vuelve a interpretar los IDs y valida targets/etiquetas. Un diccionario explícito con la misma semántica resuelve 100%; es solo control de realizabilidad, no prueba de aprendizaje de Hielo. Las etiquetas supervisan BCE, pero no llegan al forward normal.
''')
write('ENGINEERING','''# Contratos ejecutados

preflight.json certifica causalidad de logits y scores en train/eval, perturbación futura, máscaras, aislamiento por batch y documentos, resets, parámetros iniciales idénticos, cobertura exacta AdamW, no escritura al rechazar y ecuación Delta conservada al aceptar. BCE produce gradientes no nulos en ambas capas del filtro y una actualización real AdamW modifica sus pesos.

La trayectoria CPU de 10 updates es idéntica a 4 + checkpoint + 6 en los cuatro brazos, incluidos parámetros, AdamW, RNG, cursor y orden materializado. La política aleatoria es determinista y causal por documento. C rechaza oracle_mask. Checkpoints con weights_only=True, carga strict=True; configuración, dataset SHA, fuente SHA y código SHA guardados.

La colisión inicial de nombre `run` con un módulo histórico se corrigió antes del freeze: los módulos nuevos tienen prefijo trapos_. El fallo original permanece en preflight-import-failure.log. No se modificó código histórico para resolverlo.

El certificado se limita a CPU FP32 y el DSL implementado. No acredita CUDA, AMP, entrenamiento lingüístico ni un filtro semántico general.
''')
write('TRAINING_RESULTS','# Resultados funcionales\n\n'+table+'\nCurvas completas y pérdidas separadas en *-curve.json. Una exactitud de selección alta no sustituye exactitud de respuesta. D utiliza supervisión oracular en inferencia y no cuenta como modelo autónomo. El checkpoint evaluado es siempre update300; no hubo selección de mejor dev.\n')
write('FILTER_BEHAVIOR','# Comportamiento del filtro\n\n'+selection+'''
Las matrices TP/FP/FN/TN, tasas de error y desglose por tipo de evento se guardan en cada *-metrics.json. La precisión/recall usa decisiones ejecutadas, no únicamente p>0 ni gradientes. El control aleatorio se compara con el presupuesto TRAIN del C final: calibration-*.json. Puede haber diferencias de frecuencia en dev, que se registran; no se recalibra allí.

El override-all usa exactamente los pesos del C entrenado y fuerza todas las escrituras: controla capacidad y entrenamiento compartido al intervenir decisiones. Esto no demuestra que cada neurona sea interpretable ni que el filtro sea general fuera del DSL.
''')
mem=''
for tag,d in metrics.items():
 m=d['contaminated_pair'];mem+=f"- {tag}: cambios de estado {json.dumps(m['state_change'])}; reset Hielo → {d['reset']['normal']*100:.2f}% de respuestas; intercambio compatible sigue compañero {d['compatible_swap']['follows_partner']*100:.2f}%.\n"
write('MEMORY_INTERFERENCE','''# Conservación y contaminación

La formación, corrección y conservación se miden con respuestas normales por entidad y consultas emparejadas. No se entrenó un decoder auxiliar de valores. Los estados de los ocho primeros ejemplos por familia se conservaron por selección determinista, incluyendo aciertos y fallos. Las propuestas rechazadas tienen cambio H exactamente cero por contrato; no se interpreta distancia de estado como binding correcto.

'''+mem+'''
Los intercambios emparejan mismo objetivo, entidades y estructura, cambiando únicamente valor vigente. No se interpreta una perturbación arbitraria fuera de distribución como causalidad concluyente.
''')
cf=''
for tag,d in metrics.items():
 for fam in ['contaminated_pair','layout','surface']:
  for kind,v in d[fam]['counterfactuals'].items():cf+=f"| {tag} | {fam} | {kind} | {v['n']} | {v['joint_correct']*100:.2f}% | {v['prediction_invariance']*100:.2f}% |\n"
write('COUNTERFACTUALS','''# Contrafactuales

Invalid: cambia solamente valores de propuestas que no deben aceptarse. Current: cambia la última escritura válida de la entidad consultada. Obsolete: cambia una escritura válida reemplazada posteriormente; solo se evalúan filas donde existe. Se requiere acertar ambas versiones, no solo invariancia. La intervención conserva framing, entidad, flags y objetivo. No se usa ninguna evaluación sellada.

| Brazo | Familia | Cambio | Pares | Ambos correctos | Predicción igual |
|---|---|---|---:|---:|---:|
'''+cf)
cost=''
for tag in metrics:
 d=load(tag+'-cost');cost+=f"| {tag} | {d['seconds']:.3f} | {d['seconds']/300*1000:.3f} | {d['parameters']} | {d['trainable']} | {d['rss_kib']} |\n"
write('PERFORMANCE','''# Coste CPU

| Brazo | Train s | ms/update | Parámetros modelo | Entrenables | RSS pico proceso KiB |
|---|---:|---:|---:|---:|---:|
'''+cost+'''
La cabeza nueva tiene 545 parámetros. Todos los brazos la instancian; solo C los entrena. Los pesos de inferencia existentes no aumentan de dimensión. Cada brazo consume 2.400 respuestas y 230.400 IDs. C añade 12.000 etiquetas BCE de aceptación.

Se mide tiempo completo de update, sin evaluación ni carga inicial. No se aisló un coste de filtro por sustracción entre brazos: sería confundir diferencias de backward/loss. El microbenchmark congelado, si se ejecuta, queda separado en policy-timing.json.

Las escrituras rechazadas se omiten **lógicamente en H**, pero la implementación sigue calculando key, value y el producto exterior candidato; **no ahorra esas operaciones**. No se declara reducción de FLOPs ni aceleración CUDA. La tasa de escritura no equivale a ahorro de cómputo. La prioridad de V1 es selección funcional verificable.
''')
passed=gate['passed'];fails=[k for k,v in gate['checks'].items() if not v]
text=('El piloto supera todas las compuertas; confirmaciones preregistradas ejecutadas sin cambiar receta.' if passed else 'El piloto NO supera las compuertas. Se cierra Trapos V1; no se entrenaron semillas29/43 y no se rediseñó el filtro.')
write('DECISION',f'''# Decisión científica

{text}

Compuertas incumplidas: {fails}.

'''+table+'''
La evidencia se refiere únicamente a selección en este DSL. Las escrituras sintácticas se extraen explícitamente; objetivos, confirmación y negación están codificados en registros. No demuestra comprensión libre, filtrado semántico general ni aislamiento térmico completo.

El contraste controla el diseño de Hielo/Delta/lector y datos por semilla. La pérdida adicional C cambia la señal de aprendizaje, declaradamente. Para atribuir beneficio a decisiones, revisar override-all del MISMO checkpoint; no basta comparar parámetros de C con A. D es límite asistido. El criterio decisivo exige selección Y respuestas funcionales frente a A y B, generalización, escenarios limpios y presupuesto de escritura comparable.

Si falla, conservar Addressable V1.2 como referencia válida. No iniciar búsqueda de lambda, head size, nuevas políticas ni arquitecturas. Los resultados delimitan el protocolo/receta; no prueban imposibilidad de filtración aprendida. Si pasa, preparar una transición posterior controlada hacia eventos expresados de otra forma, sin ejecutarla aquí. Ningún pretraining o gasto autorizado por este estudio.
''')
if passed:
 with (R/'DECISION.md').open('a') as f:
  for seed in [29,43]:f.write(f"\nConfirmación {seed}: {load(f'gate-{seed}')['passed']}.\n")
print('Measured reports generated')
# Limitaciones y diagnósticos ejecutados tras cerrar el piloto; sin nuevos updates.
lim='''\n\n## Alcance de las consultas emparejadas\n\nEl entrenamiento consulta siempre la primera entidad del encabezado de objetivo. La segunda consulta de evaluación conserva ese encabezado y cambia solo el token de consulta: introduce una composición consulta/posición de objetivo no entrenada. Por tanto, la exactitud conjunta combina conservación y generalización de lectura; sus fallos no aíslan interferencia ni selección. Se conserva este resultado y no se reentrena para corregirlo. La respuesta normal al 100% tampoco acredita ambas asociaciones.\n'''
for name in ['DATA_CONTRACTS','TRAINING_RESULTS','MEMORY_INTERFERENCE','DECISION']:
 with (R/(name+'.md')).open('a') as f:f.write(lim)
integ=load('final-integrity');timing=load('policy-timing')
with (R/'FILTER_BEHAVIOR.md').open('a') as f:
 f.write('\n## Diagnóstico de regla superficial\n\nEn las 960 decisiones por familia contaminada, las decisiones de C coinciden exactamente (100%) con «aceptar si el bit confirmado está activo», frente al 80% de coincidencia con el oráculo completo. Rechaza hipótesis y citas, pero acepta todas las negaciones confirmadas y afirmaciones fuera del objetivo. Esta equivalencia observada no identifica una neurona causal ni prueba el algoritmo interno; demuestra que el panel no distingue sus decisiones de esa heurística superficial. Evidencia: final-integrity.json y C-17-filter-decisions.json.\n')
with (R/'PERFORMANCE.md').open('a') as f:
 f.write(f'\nMicrobenchmark ejecutado: {timing["head_only_ms_per_model_forward"]:.4f} ms para las {timing["head_calls_per_forward"]} llamadas de cabeza de un forward batch8, 200 repeticiones, CPU sin gradientes. No incluye backward, extracción ni escritura y no es un ahorro end-to-end.\n')
with (R/'ENGINEERING.md').open('a') as f:
 f.write('\nCierre: final-integrity.json verifica restauración exacta de los cuatro checkpoints finales y AdamW, inicializaciones idénticas, hashes de los tres checkpoints históricos intactos y archivos preregistrados sin modificaciones. El Jacobiano del foreground final respecto al prefijo oculto es exactamente cero en el fixture medido; Hielo es la ruta declarada de acceso. final-checks.log: FINAL CHECKS PASS.\n')
with (R/'DECISION.md').open('a') as f:
 f.write('''\n## Conclusión del piloto cerrado\n\nC no supera escritura permanente: ambos logran 100% en consulta principal; C alcanza 76,56% conjunto frente a 79,69% de A en el par retenido. B alcanza 78,65% normal y 47,40% conjunto; D oracular 100% en ambos. C supera B pero no el conjunto de requisitos. Su precisión de aceptación es 75%, recall 100%, y conserva una heurística equivalente al bit confirmado; no aprende el predicado completo de negación y objetivo.\n\nForzar todas las escrituras en el mismo checkpoint C reduce la respuesta normal de 100% a 61,98%: sus decisiones aportan beneficio parcial, sin demostrar superioridad del entrenamiento C frente a A ni filtrado completo. D demuestra realizabilidad asistida en esta distribución. No se concluye imposibilidad representacional ni se atribuye el resultado a una única compuerta.\n\nSe cierra Trapos V1 con resultado negativo respecto al criterio prospectivo. Addressable V1.2 permanece intacto. No hay semillas adicionales ni búsqueda de hiperparámetros. Una continuación necesitaría autorización y un contrato que balancee también consulta frente a posición del objetivo y distinga explícitamente la heurística de confirmación; no se ejecuta aquí.\n''')
