import json,csv,datetime
from pathlib import Path
import study as S
R=S.ROOT;O=S.O
load=lambda n:json.loads((O/(n+'.json')).read_text())
metrics={p.stem.removesuffix('-metrics'):json.loads(p.read_text()) for p in sorted(O.glob('[BC]-??-metrics.json'))}
g=load('primary-gate');rows=[]
for tag,m in metrics.items():
 for fam in ['held_pair','held_formation','new_layout','alternate','held_distractor']:
  d=m[fam];rows.append([tag,fam,d['normal'],d['joint'],d.get('corrected'),d.get('preserved')])
with (O/'summary.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['arm_seed','family','normal','joint_normal_both_queries','corrected_query','preserved_query']);w.writerows(rows)
table='| Brazo | Familia | Corregida | Preservada | Ambas consultas |\n|---|---|---:|---:|---:|\n'
for tag,fam,n,j,c,p in rows:
 pct=lambda x:'—' if x is None else f'{100*x:.2f}%'
 table+=f'| {tag} | {fam} | {pct(c)} | {pct(p)} | {pct(j)} |\n'
def write(n,s):(R/(n+'.md')).write_text(s.strip()+'\n')
write('README',f'''# Addressable V1.2 — estabilidad/plasticidad

Contraste CPU ejecutado en rama `cryo-addressable-stability-v1`, desde `74d8079`. Arquitectura Addressable V1 intacta. {'El piloto habilitó confirmaciones emparejadas.' if g['passed'] else 'El piloto NO habilitó confirmaciones; no se entrenaron semillas 29/43.'}

Esta carpeta contiene datos, protocolo congelado antes de entrenar, tests, curvas, predicciones, estados reales, checkpoints completos y hashes. Los `.pt` se conservan localmente y se enumeran en SHA256SUMS. No se abrió ninguna evaluación sellada. Sin GPU, servicios de pago ni corpus lingüístico.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
"$PY" addressable/test_contracts.py
"$PY" stability/test_contracts.py
# Entrenamiento: SOLO en otro worktree limpio, sin artefactos stability/results/.
"$PY" stability/study.py
"$PY" stability/diagnostics.py
"$PY" stability/write_reports.py
```

El script rechaza sobrescribir FREEZE o checkpoints finales. No borrar los resultados para repetir. Dependencias y rutas de warmstart son las mismas de V1.1. Leer DECISION.md y PROTOCOL.md antes de interpretar los porcentajes.
''')
write('PROTOCOL','''# Protocolo congelado

`protocol.json` y `results/FREEZE.json` preceden al primer entrenamiento. Semilla inicial 17; solo si supera todas las compuertas se permiten B/C 29 y 43. 300 updates por brazo, batch 8, CPU FP32, un thread, AdamW LR 0,003, betas (0,9;0,95), decay 0,01, clipping 1. Checkpoint final update 300; sin selección por dev, búsqueda ni prolongación.

**Diferencia declarada con V1.1:** antes se usaba CE de respuesta + 0,1 CE auxiliar inicial. La instrucción V1.2 exige únicamente respuesta, por lo que B y C usan exactamente CE del siguiente token de respuesta al final. B reproduce la distribución anterior, no el objetivo completo histórico. No atribuir diferencias frente a porcentajes publicados de V1.1 solo a datos. La comparación causal primaria es B frente a C dentro de esta ejecución.

El decoder auxiliar se crea idéntico, se congela, queda fuera de AdamW y no se usa en loss ni inferencia. No se añaden parámetros al modelo ni pérdidas. Cada brazo recibe 2.400 respuestas, cero targets auxiliares y 153.600 IDs. Misma arquitectura, inicialización, índices base y variantes por semilla; C transforma pares/layouts/distractores. Los cambios de distribución están agrupados: el contraste no identifica por separado cuál contribuye.

Compuertas en held_pair, new_layout, alternate y held_distractor: corregida y preservada ≥95%, ambas consultas correctas ≥90%, contrafactuales obsoleto/vigente ≥95%. Formación en par reservado ≥90%, intercambio ≥95%, caída conjunta ≤5 puntos frente a B en familias previstas. Son criterios prospectivos de ingeniería; no pruebas estadísticas. No cambiar umbrales tras observar resultados.

Se conservó el modo eval de la receta histórica durante updates (dropout=0; autograd activo). La causalidad también se comprobó expresamente en train. No transferir este resultado a dropout, CUDA, BF16 o entrenamiento de lenguaje.
''')
write('TRAINING_DATA','''# Datos y cobertura

B reconstruye literalmente los registros e índices del tratamiento V1.1: 50% sin corrección, 50% con una corrección, repartida entre la entidad consultada y la otra. Cada secuencia mantiene 64 IDs y la gramática de acontecimientos de cuatro IDs.

C conserva esos valores, roles, índices y presupuesto. Amplía a nueve pares no ordenados de cinco entidades; reserva **A–C**, en ambas direcciones, para evaluación. Varía escrituras iniciales entre (0,1),(2,3),(4,5), corrección entre registros 6/8/10 y añade una tercera entidad en el registro 11 en 25% de secuencias. La consulta queda al final. Los hechos válidos permanecen fuera de la ventana local de consulta; no hay caché oculta.

En cada brazo hay exactamente 1.200 secuencias corregidas: 600 consultan la corregida y 600 la preservada. Las 1.200 restantes no contienen corrección. Todos los valores tienen soporte en cada par/rol observado. El muestreo original de valores e identidades es aleatorio y emparejado: **no se afirma igualdad exacta de cada celda condicionada en las 2.400 exposiciones finitas**. Los conteos reales, transiciones, programas únicos y heurísticas están en *-frequencies.json. Las proporciones de roles sí son exactas; frecuencias finitas desiguales limitan el alcance del balance.

No se eliminaron registros después de mirar sus resultados. No hay duplicados exactos train/dev en ninguna familia evaluada. El par A–C completo no aparece en train C. Los layouts de dev usan (6,7)/11, (1,4)/9 y tercera entidad intermedia, excluidos de train. Los valores y símbolos individuales son conocidos: generalización composicional, no vocabulario nuevo.

El control última escritura por entidad resuelve el DSL por definición; primera escritura, última global y presencia constante se reportan como atajos. No se interpreta esta tarea como comprensión lingüística. La memoria recibe escrituras sintácticas deterministas: Trapos semántico no fue entrenado.

Se detectó antes de entrenar una correlación accidental entre el calendario de pares y el tipo de evento; preflight-draft-preserved.py conserva el borrador. Se corrigió antes del freeze y no hubo entrenamiento principal con ese borrador.
''')
write('CONTROL_VS_TREATMENT','# Comparación funcional B/C\n\nTodos los porcentajes siguientes son respuestas normales, sin decoder auxiliar. Exactitud conjunta exige dos consultas a la misma secuencia, una por entidad, ambas correctas. No es el producto de marginales.\n\n'+table+'\nCurvas, CE, gradientes por tensor, coste y exactitud sobre exposición train se conservan sin selección de ejemplos. Dos consultas requieren dos forwards de evaluación; no cambian supervisión de entrenamiento. Las familias comparten símbolos y algunas estructuras: no tratar sus filas como réplicas estadísticas independientes.\n')
write('GENERALIZATION','''# Generalización

Familias prospectivas: held_pair (A–C completamente reservado, correcciones en layout fijo), held_formation (dos asociaciones sin corrección en ese par), new_layout (iniciales 6/7 y corrección 11), alternate (iniciales separadas 1/4 y corrección 9), held_distractor (par reservado y tercera entidad en medio).

'''+table+'''
Todas las comparaciones utilizan el lector normal. Las entradas no contienen respuestas del oráculo; las etiquetas solo entran en CE/evaluación. La ventana activa final cubre IDs 48–63; acontecimientos de evaluación terminan antes de ella. El estado Hielo es la ruta declarada del prefijo; no se añade RAG ni caché.

Tres semillas preregistradas dan una confirmación acotada, no robustez poblacional. Se reutilizan los warmstarts históricos correspondientes; no son tres modelos desde cero ni una muestra de nuevas inicializaciones ilimitadas. No se abrió el conjunto confirmatorio sellado heredado ni se utilizó para diseñar filtros o checkpoints.
''')
cf=''
for tag,m in metrics.items():
 for fam in ['held_pair','new_layout','alternate','held_distractor','held_formation']:
  for kind,d in m[fam]['cf'].items():cf+=f"| {tag} | {fam} | {kind} | {100*d['joint_correct']:.2f}% | {100*d['prediction_invariance']:.2f}% |\n"
write('COUNTERFACTUALS','''# Contrafactuales e intervenciones

Obsoleto: cambiar solo la escritura inicial reemplazada. Vigente: cambiar solo la última escritura de la entidad consultada. Se requiere acertar ambas versiones; invariancia sin exactitud no basta. Intercambio cambia los dos valores iniciales. El agregado prospectivo de intercambio incluye valores iguales; el diagnóstico `valid-swaps.json` separa los pares realmente distintos y es el criterio estricto adicional de interpretación.

| Brazo | Familia | Cambio | Ambas correctas | Predicción igual |
|---|---|---|---:|---:|
'''+cf+'''
Los resultados completos también incluyen Hielo reseteado y estados intercambiados entre sesiones con entidades y layout compatibles, pero distinto valor vigente. Se reporta exactitud respecto al original y seguimiento del compañero; no confundir sensibilidad con utilidad. Las intervenciones no participan en entrenamiento.
''')
cost=''
for tag in metrics:
 d=load(tag+'-cost');cost+=f"- {tag}: {d['seconds']:.3f} s de entrenamiento, {d['parameters']} parámetros, RSS pico del proceso {d['rss_kib']} KiB.\n"
write('KEY_INTERFERENCE','''# Interferencia y coste

Cada *-metrics.json conserva la matriz Gram de claves A–E y errores condicionados por par. interference-diagnostics.json registra gradientes de respuesta por rol, cosenos entre ellos y cambios de la lectura kᵀH después de actualizar otra entidad. Se usa el checkpoint final congelado; cero updates diagnósticos.

Una correlación entre cosenos y errores no prueba causalidad. Un cambio de vector leído tampoco demuestra pérdida semántica por sí solo. Las exactitudes normales emparejadas y contrafactuales son el criterio funcional. Los gradientes diagnósticos de 32 ejemplos por rol son descriptivos, no una estimación exhaustiva de entrenamiento.

'''+cost+'''
Se conserva número y dimensiones de parámetros. C introduce más acontecimientos aceptados y modifica layouts, pero la implementación calcula candidatos en todas las posiciones en ambos brazos. Igual número de IDs/targets no implica igualdad exacta de FLOPs útiles o trayectoria de memoria. No se midió GPU ni se extrapola aceleración. No se separaron causalmente capacidad de claves, extracción de valores y lectura.
''')
passed=g['passed'];decision=('El piloto supera las compuertas prospectivas; revisar las confirmaciones y el control de intercambios válidos antes de afirmar robustez.' if passed else 'El piloto NO supera las compuertas prospectivas. Se detuvo la ampliación: semillas 29 y 43 NO entrenadas. No se encadenaron más variaciones de datos.')
write('DECISION',f'''# Decisión

{decision}

'''+table+'''
El resultado permite juzgar estabilidad/plasticidad en el protocolo simbólico probado, no capacidad lingüística ni éxito completo del aislamiento térmico. B/C comparten objetivo exclusivamente de respuesta; el histórico publicado incluía una pérdida auxiliar y no es un control numérico intercambiable.

La arquitectura y los históricos permanecen intactos. Contratos, inicialización emparejada, AdamW y reanudación exacta certificados. Ninguna evaluación sellada abierta. No GPU, gastos, pretraining ni aumento de updates.

Si persiste el fallo en el par reservado pese a cobertura ampliada, se cierra esta línea de ajustes de datos. En ese caso negativo, el siguiente contraste aislado a considerar es intervenir únicamente el **direccionamiento de claves compartidas de escritura/lectura**, preservando backbone, valores, regla Delta, dimensiones y receta, frente al modelo actual. Primero debe medirse si reducir solapamiento causalmente mejora la conservación; la geometría observada sola no prueba esa causa. No modificar simultáneamente el borrado y el reader. Este contraste se recomienda, NO se ejecuta aquí. Si predominan errores de formación o lectura en todos los pares, revisar los resultados antes de atribuirlo solo al direccionamiento.
''')

if passed:
 confirmations={str(seed):load(f'confirmation-{seed}-gate') for seed in [29,43]}
 allpass=all(v['passed'] for v in confirmations.values())
 if allpass:
  p=R/'DECISION.md';text=p.read_text();start=text.index('Si persiste el fallo');text=text[:start];p.write_text(text)
 with (R/'DECISION.md').open('a') as f:
  f.write('\nConfirmaciones: '+json.dumps({k:v['passed'] for k,v in confirmations.items()})+'\n')
  f.write(('Las tres semillas superan las compuertas. Se recomienda conservar la arquitectura y esta distribución como candidato de asociación simbólica; NO se justifica modificar representación ni regla Delta ahora. El próximo paso requiere un protocolo nuevo de selección semántica Trapos o capacidad mayor, con evaluación confirmatoria aún sellada. No ejecutado.\n' if allpass else 'Las confirmaciones no acreditan robustez completa. Conservar los fallos por semilla; no extender updates ni añadir más variaciones de datos.\n'))

# Concrete key geometry remains diagnostic, not a causal attribution.
kt='\n| Semilla | cos(A,C), B | cos(A,C), C |\n|---|---:|---:|\n'
for seed in [17,29,43]:
 if f'C-{seed}' in metrics:kt+=f"| {seed} | {metrics[f'B-{seed}']['key_gram'][0][2]:.6f} | {metrics[f'C-{seed}']['key_gram'][0][2]:.6f} |\n"
with (R/'KEY_INTERFERENCE.md').open('a') as f:f.write(kt+'\nA–C es el par reservado. Estos cambios son compatibles con menor interferencia de direccionamiento, pero la intervención fue sobre datos, no sobre el coseno. No se ha aislado el efecto de cobertura de pares del de layouts y distractores.\n')
write('ENGINEERING','''# Certificación ejecutada

Ocho tests históricos y cinco tests nuevos PASS. preflight.json certifica causalidad train/eval, padding, aislamiento por batch/documento, reset, identidad inicial, cobertura exacta de AdamW, gradientes de escritura y lectura, y trayectoria idéntica CPU de 10 updates continuos frente a 4 + restauración + 6. Incluye parámetros, decoder congelado, AdamW, RNG, cursor y orden materializado por semilla. La máscara de respuesta es equivalente a CE con ignore_index=-100 en todas las posiciones salvo la última; no existe pérdida auxiliar.

Los checkpoints finales guardan configuración, estado completo del modelo/decoder/optimizador, RNG, cursor, update, microstep, identidad del dataset y orden, y SHA del código arquitectónico. Carga weights_only=True y strict=True. diagnostics.py verifica restauración del checkpoint final y que los estados iniciales B/C coinciden por semilla. También cambia hechos del prefijo y mide las diferencias numéricas de hidden y logits con Hielo reseteado. Un chequeo adicional de igualdad bit a bit falló y se preserva en diagnostics-bitwise-failure.log: no se relajaron los tests preregistrados. Se añadió una comprobación estructural independiente del Jacobiano hacia embeddings del prefijo oculto, que debe ser exactamente cero; las discrepancias de punto flotante se registran por separado. No se confunde invariancia matemática con identidad de bits.

Se conserva la arquitectura original byte a byte. No se abrió ningún conjunto sellado, no se modificaron A4, NeoToken ni Chinchilla, y no se utilizó GPU o servicio de pago. Certificación limitada a CPU FP32, monoproceso y fixtures de 64 IDs. No implica certificación lingüística, CUDA, AMP o sesiones de producción.
''')
with (R/'ENGINEERING.md').open('a') as f:f.write('\nEn seis checkpoints, el Jacobiano del hidden final respecto al prefijo oculto tiene exactamente cero elementos no nulos. Las diferencias numéricas máximas al cambiar el prefijo fueron 1,91e-6 en hidden y 9,54e-6 en logits con Hielo reseteado. Se conservaron los umbrales y tests originales.\n')
print('Reports generated from measured results')
