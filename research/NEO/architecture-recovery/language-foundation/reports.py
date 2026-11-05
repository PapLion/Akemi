from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent;O=ROOT/'results'
def get(n):return json.loads((O/(n+'.json')).read_text())
fg=get('foreground');bl=get('baseline');cap=get('capacity');tok=get('tokenizer-analysis');audit=get('data-audit');docs=get('data');hist=get('history-exposure');uni=get('unigram')
def write(n,s):
 p=ROOT/n;assert not p.exists();p.write_text(s+'\n')
rows='| Modelo | Parámetros activos | NLL train final | NLL dev inicial → final | PPL dev | Targets/s | RAM MiB |\n|---|---:|---:|---:|---:|---:|---:|\n'
for r in [fg,bl]:
 k=r['kind'];rows+=f"| {k} | {cap[k]['trainable']} | {r['metrics']['128']['train']['all']['nll']:.4f} | {r['metrics']['0']['dev']['all']['nll']:.4f} → {r['metrics']['128']['dev']['all']['nll']:.4f} | {r['metrics']['128']['dev']['all']['ppl']:.2f} | {r['targets_s']:.1f} | {r['peak_process_rss_mib']:.1f} |\n"
write('README.md',f'''# Language Learning Foundation V1

Cerrada la cadena de microfits simbólicos. Piloto causal real CPU ejecutado, sin Hielo/Trapos, sin cambios al modelo ni a V3. Base eb2ee86; rama neo-language-learning-foundation-v1.

{rows}

Existe aprendizaje transferible a dos archivos de otro repositorio bajo este panel inglés de código. No existe un modelo lingüístico útil: generación repetitiva, sin prueba bilingüe ni generalización semántica. No autoriza pretraining significativo.

Ver DECISION.md, PROTOCOL.json, manifiestos y tests en results/. Reproducir scripts únicamente en una salida/worktree nuevo: pilot.py → analysis.py → checks.py → reports.py. Rechazan sobrescribir evidencia. Python CPU local usado: /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python; OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1. Los originales D0.1 se referencian por hash, no se descargan ni se modifican.
''')
write('ARCHITECTURE_CAPACITY.md',f'''# Capacidad real

Foreground actual: 299520 parámetros asignados, 296160 entrenables; 3360 de la ruta Hielo permanecen congelados e inactivos. Dos bloques causales width32, cuatro cabezas Q / dos KV, dimensión por cabeza8, RoPE sin posiciones aprendidas; MLP gated SiLU inner128 por bloque. Refinamiento rápido residual normalizado repetido dos veces, sin nueva atención ni estado temporal. Ventana piloto128, reset por ventana; los estudios de binding usaban119 IDs válidos y padding128. No hay KV cache ni persistencia oculta.

| Componente | Parámetros |
|---|---:|
| Embedding y salida compartida | 262144 |
| Q/K/V/O dos bloques | 6144 |
| MLP dos bloques | 24576 |
| Refinamiento rápido | 3104 |
| Normalizaciones activas | 192 |
| Memoria inactiva | 3360 |

Embedding = {262144/296160:.2%} de los parámetros activos ({262144/299520:.2%} del total). La cabeza es F.linear(hidden, emb.weight), sin bias ni una segunda matriz vocabulario×width. Quedan **34016 parámetros entrenables no embedding**; atención+MLP apenas30720. No se deduce imposibilidad de aprender, pero este reparto no es una base convincente para generalización lingüística amplia. La fracción de vocabulario es un diagnóstico de presupuesto, no una causa aislada demostrada.

Baseline disponible: vendor.cryo_historical.Baseline(v8192,d32,layers2,dropout0), 293024 activos, atención/MLP iguales, sin refinamiento rápido. Inicialización propia ya existente con escalado residual; no es idéntica a la del foreground. Diferencia3136 parámetros activos y receta de inicialización: contraste de referencia, no ablación causal perfecta. No se modificó ninguno.

Inventario tensor por tensor en results/capacity.json. Piloto: RSS high-water del proceso773MiB aproximadamente; temporales de logits8192×128 dominan más que 1,2MiB de pesos FP32. RAM observada no es pico independiente por brazo ni predicción para modelos mayores. Velocidades en CPU_LANGUAGE_PILOT.md.
''')
ht='| Experimento | Updates | IDs de entrada procesados | Targets respuesta |\n|---|---:|---:|---:|\n'
for k,v in hist.items():
 if 'processed_input_ids' in v:ht+=f"| {k} | {v['updates']} | {v['processed_input_ids']} | {v['answer_targets']} |\n"
write('TRAINING_OBJECTIVES.md',f'''# Señal de entrenamiento

{ht}

Las cifras son por corrida, no un corpus acumulado de tokens nuevos. No se suman snapshots ni reproducciones como datos independientes. Los estudios de bindings supervisaban **1 respuesta por119 IDs de entrada (0,8403%)**, aunque softmax siempre cubría8192 clases. A tiene4 respuestas únicas, C8: en400updates cada ejemplo A se repite800 veces y C400. El currículo supervisa5600 respuestas sobre8 combinaciones, con frecuencias desiguales deliberadas. Su diversidad estructural es mínima; los devs cambian estructura y nombres, no son una muestra natural diversa.

La escalera previa (200/200/300/400 updates) demostró memorización de1,2,4 respuestas y fallo al ampliar a48. La intervención factual densa añadía11 targets de hechos con peso0,1 y falló; **no era modelado causal de todo el texto**. No se repite.

Language Bridge V1 sí utilizó next-token sobre secuencias:12537 targets expuestos por brazo, tres brazos64updates, datos reales+32 relatos sintéticos; una capa, local16 salvo baseline transformer. Redujo NLL, generación repetitiva y recuperación distante25%. Bridge V2 y diagnósticos posteriores se centraron en respuestas; control positivo fallido, Hielo no validado en lenguaje. No llamar a toda esta historia pretraining LM.

Este piloto vuelve al **LM causal continuo**: cada token válido predice el siguiente; BOS/EOS explícitos, sin cruce documental ni padding. Ventanas de128 con stride127 conservan cada posición objetivo exactamente una vez por recorrido; reinicio de contexto entre ventanas. Train25355 posiciones objetivo, dev8637;32433 targets expuestos por brazo,25355 posiciones distintas vistas,21,823% de exposiciones repetidas. Train tiene1265 tipos de ID (no1265 ejemplos independientes), solo3 archivos de una familia. Densidad por ventana completa127/128, no garantiza calidad ni binding. No se concluye que LM completo resuelva automáticamente asociaciones.
''')
data='| Documento | Split | Idioma/dominio | Bytes | IDs con BOS/EOS |\n|---|---|---|---:|---:|\n'
for d in docs:data+=f"| {d['id']} | {d['split']} | {d['lang']}/{d['domain']} | {d['bytes']} | {len(d['ids'])} |\n"
write('DATA_READINESS.md',f'''# Datos admisibles y límites

D0.1 contiene49 train y16dev registros; el inventario por categoría/licencia está en data-audit.json. Sus conteos históricos usan V1: no reutilizarlos como targets V3. Solo train/dev de accepted.jsonl; ningún archivo sealed/, test D0 o Chinchilla se abrió para este trabajo.

**Seleccionado para ingeniería local:** Click8.1.7 BSD3 train y Requests2.31 Apache2 dev; URLs resueltas a commits inmutables, archivos completos y licencias archivadas. Se verificaron SHA del texto y bytes fuente, licencia local, roundtrip, parse AST de cuatro archivos Python y documentación RST. Avisos de licencia preservados en notices/. Esta evidencia es más fuerte que una etiqueta de hub; no se ofrece certificación jurídica universal ni auditoría exhaustiva de todo contenido de terceros.

{data}

Dos familias repositorio disjuntas. Cero hashes compartidos train/dev, cero pasajes normalizados de12 y64 palabras; no demuestra ausencia de toda paráfrasis ni contaminación histórica. Inicialización nueva para ambos modelos. Los documentos no se dividieron entre splits. No PII obvia por regex email; código público con procedencia específica, no datos personales de conversaciones.

**Excluido:**42 capítulos Gutenberg train y12 capítulos/ensayos dev: derechos condicionados territorialmente; no resueltos aquí. OASST4train/2dev: licencia de colección archivada, aportes individuales/PII/calidad pendientes, no autorizado por inferencia. Sintéticos y evaluaciones: no mezclados en el piloto. Los conjuntos finales sellados siguen cerrados.

Solo inglés, dos archivos de código train y un documento expositivo; dev únicamente código de otra biblioteca. ES no medido; narrativa y conversación ausentes. Es un subconjunto piloto admisible y pequeño, **no una dieta representativa ni corpus bilingüe listo**. No se rellena el vacío con texto sintético ni se descarga más corpus.
''')
write('TOKENIZER_ANALYSIS.md',f'''# NeoToken V3

Artefacto BPE8192 provisional sin cambios; SHA {tok['artifact_sha']}. PAD256/BOS257/EOS258. IDs/JSON y fingerprint anteriores verificados, sin pickle. Se mantiene V1 exclusivamente en históricoA4.

Seis fixtures adicionales roundtrip exacto: vacío, acentos ES/EN, combinados/emoji/Unicode, código, LaTeX y controles. Roundtrip de todos los5 documentos fuente exacto. Panel concatenado85328bytes/33987 IDs: encode {tok['encode_seconds']:.6f}s, decode {tok['decode_seconds']:.6f}s en esta máquina, medición única sin intervalo. Artefacto80964bytes. Esto certifica funcionamiento de esta integración, no optimalidad lingüística ni paridad ES/EN.

1265 de8192 tipos aparecen en train:15,44%. La matriz sigue reservando262144 parámetros. Desconocidos Unicode tienen ruta byte-level; no se ha repetido toda certificación adversarial histórica. El contrato de causalidad del modelo se valida sobre IDs ya fijados. BPE sobre texto no garantiza estabilidad de segmentación de un prefijo al añadir caracteres: generación opera sobre IDs y detokeniza, no retokeniza targets futuros.

NeoToken es multiescala; este experimento usa solamente su núcleo BPE. Las vistas adicionales existen como sidecars en el trabajo V3, pero no se entregan al modelo ni se atribuye su potencial a este resultado. SPEC3.0 completa, cobertura lingüística y multidominio siguen experimentales según CERTIFICATION.md original.
''')
write('CPU_LANGUAGE_PILOT.md',f'''# Piloto CPU ejecutado

Protocolo fijado antes de entrenar en PROTOCOL.json: seed17,128updates por brazo,batch2,128IDs,stride127,AdamW.003 betas.9/.95,wd.01,clip1,FP32,un thread. Techo32512targets y180s por brazo; ambos terminaron128updates con32433targets. Ninguna ampliación, ajuste dev o selección de checkpoint. Dos corridas pequeñas, no pretraining principal.

Forward foreground utiliza chunk_hidden sobre ventana completa128 y la misma cabeza tied. Es la interfaz de contexto completo de los diagnósticos, **no el forward local16 de Language Bridge V1**. No cambia pesos/módulos/ecuaciones; se declara la política de ventana. Una ventana pertenece a un documento y una fila: no packing mezclado ni estado entre documentos. Baseline usa misma visibilidad y ventanas, inicialización propia documentada.

{rows}

Por dominio al final: foreground train código NLL4,7463 / expositivo5,5448; baseline4,7731/5,5414. Dev código5,7674/5,8379; ES/dev expositivo no disponible. No promediar dominios ausentes ni atribuir la diferencia0,0705NLL a arquitectura con una semilla.

Control unigram calculado solo con targets train, smoothing0,1 fijado antes de calcular: train NLL{uni['train']['nll']:.4f}, dev{uni['dev']['nll']:.4f}. Ambos modelos superan este control marginal en dev; existe señal predictiva transferible adicional a frecuencias simples. No aísla semántica ni composicionalidad.

Generaciones greedy32tokens en3prompts prefijados guardadas por ID/texto: repetición de puntuación/espacios en ambos. Continuación técnica de prefijos nuevos funciona, pero calidad no útil. El descenso de NLL no convierte estas salidas en lenguaje competente. PPL depende de V3, dominio y máscara: no comparar contra otro tokenizer.

Contratos previos: causalidad por perturbación futura, aislamiento de filas, shift/máscara comparada con CE manual, AdamW exacto, gradientes finitos, reanudación7updates vs3+4 con igualdad exacta de parámetros/momentos/RNG/cursor. Verificación adicional: cada parámetro activo tiene gradiente no nulo y cambia, padding no afecta posiciones válidas. Checkpoints0/128, restauración final reproduce dev exactamente. Solo CPU mono-thread/dropout0; no certificado AMP/CUDA/DDP.

Tiempo solo updates foreground{fg['seconds_updates']:.3f}s, baseline{bl['seconds_updates']:.3f}s; incluye gradientes/clipping, excluye evaluación/encode/setup. RAM high-water del proceso, no comparativa de memoria aislada. Muestreo determinista idéntico, hashes de fuente/datos/orden en reproducibility.json.
''')
write('SCALING_PROPOSAL.md','''# Siguiente escalón: dos candidatos, no implementados

El prototipo width32 tiene suficiente capacidad para demostrar reducción de NLL y ajuste limitado; no evidencia suficiente de una base lingüística útil. El embedding consume88,5% del presupuesto activo. Proponer más capacidad se justifica por ese reparto y por la dieta mínima, no porque se haya aislado una ley de escalamiento con estos dos modelos casi iguales.

| Candidato futuro | Width / bloques | Parámetros activos estimados | Embedding tied | Contexto inicial | Targets propuestos |
|---|---:|---:|---:|---:|---:|
| F2 | 128 /4 | 2082176 | 1048576 (50,36%) | 128 | 5M |
| F8, condicionado al resultado F2 | 256 /6 | 8195840 | 2097152 (25,59%) | 256 | 50M |

Conteos algebraicos para la familia actual sin Hielo: P=8192d+L(15d²+2d)+3d²+3d; incluyen refinamiento rápido, tied head, GQA mismo ratio. No se construyeron modelos nuevos. Baseline futuro: Transformer causal estándar con mismos tokenizer/contexto/targets, presupuesto cercano y FLOPs informados; separar aporte de refinamiento del de Hielo. Primero F2 contra baseline, no entrenar ambos tamaños a la vez.

5M/50M son presupuestos de ingeniería inicial, no cantidades óptimas ni suficientes por ley para dominio del lenguaje. Exigir al menos esas posiciones de texto diverso, derechos revisados y reserva dev por familias, preferiblemente una pasada sin ciclos. El panel actual25355train obligaría a197/1972 pasadas: inadmisible como sustituto de esos corpus. No usar Chinchilla hasta cerrar compuertas de datos por autorización separada.

**Cómputo y dinero:** el modelo actual a5638targets/s tardaría14,8min por5M y2,46h por50M, extrapolación del mismo código/tamaño sin evaluación ni I/O; no es rendimiento esperado de F2/F8. Para esos candidatos se necesita preflight/benchmark propio antes de presupuestar. No hay medición CPU/GPU de ellos.

Referencia histórica concreta, no oferta actual: FIRST_CUDA_RUN.md midió B0~8M a1794,23targets/s, RTX3090,256FP32,batch1; tarifa total entonces0,15222222USD/h. Bajo exactamente ese rendimiento/tarifa:5M≈0,774h/0,118USD;50M≈7,741h/1,178USD. No incluye arranque/transferencias/evaluación/checkpoints, no presupuestar Cryo con esos valores ni asumir esa tarifa disponible hoy. Son escenarios de sensibilidad, no cotización ni permiso de gasto. Estimar coste real mediante C=(targets/throughput/3600 + horas setup/eval)×tarifa total + tráfico; imponer margen y destrucción. No se consultó Vast ni se gastó saldo.

Recomendación: preparar datos reales bilingües y medir F2 primero, con presupuesto futuro expresamente autorizado. No hay razón experimental para lanzar50M parámetros ni1Btargets ahora.
''')
write('HIELO_INTEGRATION_PLAN.md','''# Integración futura, sin implementación

Separar modelo base LM causal (embeddings/bloques/logits/entrenador), productor de escrituras, Hielo direccionable8×d, lectura y política. Addressable estable demuestra asociaciones en DSL; no demuestra extracción lingüística. Trapos V1/V2 congelado OFF.

Primero certificar base LM en datos diversos y dev independiente. Después conectar estados causales del foreground a las proyecciones clave/valor de Hielo, manteniendo una interfaz versionada y dimensionalidad definida. No migrar automáticamente pesos simbólicos ni interpretar IDs de entidad como claves mágicas. Cambio de width futuro exige contrato explícito de proyecciones/estado, no compatibilidad asumida.

Política temporal: escrituras solo al completar chunk, resumen causal o estado de frontera declarado; ninguna escritura del chunk actual influye en su principio. Estado conservado solo dentro del documento/sesión, reset al cambiar documento; lectura y escritura con gradientes a través de frontera según horizonte de BPTT documentado. Normalización Delta y reader se certifican de nuevo para la integración. Política determinista no detecta hechos ni correcciones semánticas.

Comparación futura mínima: mismo base/contexto local con y sin Hielo; full-context separado como control de acceso a más información. Evaluaciones lingüísticas fuera de ventana solo después de certificar aprendizaje neuronal de la tarea. Reset, lectura OFF y swap con seguimiento del valor donante, no meros cambios de logits. No repetir microfits simbólicos ni reactivar filtrado para ocultar un fallo de base LM.
''')
write('PRETRAINING_GATES.md','''# Compuertas de pretraining

| Compuerta | Estado |
|---|---|
| BPE8K carga/hash/roundtrip local | PASS de ingeniería; provisional lingüísticamente |
| Foreground/base causal128, shift, padding, aislamiento | PASS CPU del piloto |
| AdamW, gradientes, RNG/cursor, checkpoint seguro | PASS CPU monoproceso FP32; no GPU/DDP/AMP |
| Generación técnica | PASS; utilidad/calidad FAIL |
| Dataset piloto procedencia/permisos | PASS limitado Click/Requests y obligaciones preservadas |
| Corpus lingüístico ES/EN diverso y licencias suficientes | BLOQUEADO |
| Dev representativo por fuentes/idioma/dominio | BLOQUEADO; solo2archivos códigoEN |
| Revisión humana/PII/calidad amplia/contaminación near-duplicate | PENDIENTE |
| Base lingüística útil y generalización composicional | NO DEMOSTRADA |
| Dimensionamiento y benchmark F2/F8 | PROPUESTO, NO EJECUTADO |
| Presupuesto nuevo de entrenamiento significativo/GPU | NO AUTORIZADO |
| Utilidad lingüística Hielo / Trapos | Hielo no validado en lenguaje; Trapos congelado |

No iniciar pretraining significativo. Bloqueos concretos: datos con cobertura y derechos, dev independiente suficiente, base que produzca continuación útil, presupuesto/throughput de modelo candidato y nuevos contratos para el entorno elegido. No convertir la falta de Trapos en veto permanente al base LM: se puede investigar base causal sin memoria, integrarla después. No se cambia CURRENT_READINESS histórico; esta rama contiene su propio estado.
''')
write('DECISION.md',f'''# Decisión de ingeniería

**Cerrar definitivamente los microfits de bindings y currículos de orden. El siguiente trabajo es datos y aprendizaje causal de texto diverso, no otra memoria.**

Tenemos un foreground causal técnicamente entrenable y reproducible, con296160 parámetros activos,262144 en vocabulario y solo34016contextuales/noembedding. No hay evidencia de capacidad suficiente para una base lingüística general. Hielo simbólico estable se conserva, Trapos congelado, V3BPE8K provisional sin cambios.

El piloto de texto real admisible demuestra descenso dev8,9941→5,7674 y ventaja frente a unigram6,2673. Hay señal de transferencia entre repositorios, **no solamente memorización de train**; con2archivos dev de código no demuestra generalización lingüística amplia. Generación repetitiva y una sola semilla. Baseline5,8379 no establece superioridad del foreground.

Recomendación única de continuidad: preparar corpus piloto bilingüe/diverso con derechos verificados y dev por familias, y entonces presupuestar F2~2,08M/5Mtargets contra Transformer comparable. F8~8,20M/50Mtargets es segunda opción condicionada, no un entrenamiento autorizado. Datos actuales no alcanzan ese escalón; no compensar ciclando cientos de veces. Costes y límites explícitos en SCALING_PROPOSAL.md.

{rows}

Trainer CPU listo para ingeniería; faltan datos representativos, calidad de generación, presupuesto/benchmark a escala y validación lingüística. No se implementan configuraciones nuevas ni se inicia pretraining significativo. Sin GPU, Vast, Chinchilla, A4, cambios de tokenizer o acceso sellado. Artefactos negativos y positivos preservados.
''')
if __name__=='__main__':print('Reports generated')
