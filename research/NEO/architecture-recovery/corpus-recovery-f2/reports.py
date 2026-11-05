from pathlib import Path
import json,math,collections
ROOT=Path(__file__).resolve().parent;O=ROOT/'results'
def get(n):return json.loads((O/(n+'.json')).read_text())
def write(n,s):(ROOT/(n+'.md')).write_text(s.strip()+'\n')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in r)+' |' for r in rows)
r=get('integrity');v=get('v3-counts');vs=get('v3-summary');sel=get('f2-selection');b=get('f2-benchmark-isolated');audit=get('curation-audits');cat=get('catalog');cov=get('v1-current-view-coverage');g=get('gates')
summary=table(['Vista','BASE docs','BASE bytes UTF-8','SFT separados','JSONL bytes almacenados'],[(name,a['counts'].get('BASE_LM',a['counts'].get('BASE_LM_CLEAN')),a['counts'].get('BASE_LM_text_bytes',a['counts'].get('BASE_LM_CLEAN_text_bytes')),a['counts'].get('SFT_CANDIDATES',a['counts'].get('SFT_CANDIDATES_REVIEW')),a['stored_jsonl_bytes']) for name,a in r['views'].items()])
write('README',f'''# NEO — Corpus Recovery & F2 Readiness V1

**Corpus recuperado; F2 técnicamente verificado; entrenamiento5M BLOQUEADO por selección aprobada insuficiente.** Rama `neo-corpus-recovery-f2-readiness-v1`, origen6115bb6. Ningún entrenamiento completo, GPU, descarga de corpus o gasto.

{summary}

Los nombres1B/500M son objetivos históricos, no conteosV3. Vistas solapadas, nunca sumarlas. Se verificaron todos los shards de estas tres vistas por SHA, JSON, campos, bytes y texto; resultados en [integrity.json](results/integrity.json). Los originales no se modificaron. Se reutilizó la curación y sus índices en lectura, sin reiniciar trabajadores.

Selección admisible sin reservas de test: **{sel['train_independent_targets']:,} train / {sel['dev_targets']:,} dev targets**, tres archivosClick y dosRequests. No basta para5M ni para un piloto bilingüe diverso. CPython tiene evidencia de licencia, pero se excluye del train por reserva histórica de familia D0test. Wikipedia/web/math/OASST no se promueven automáticamente desde sus estados pendientes.

F2=2.082.176 parámetros, baseline=2.032.768, Hielo/Trapos OFF. Tests, checkpoint/RNG/cursor, generación técnica y benchmark CPU ejecutados. Ver [DECISION](DECISION.md), [inventario](SOURCE_INVENTORY.md), [conteos](NEOTOKEN_V3_COUNTS.md), [benchmark](F2_CPU_BENCHMARK.md), [compuertas](TRAINING_READINESS.md).

Reproducción: `bash corpus-recovery-f2/reproduce.sh` desde este worktree. Solo verificación/benchmark corto; jamás lanza5M. Gate explícito: `python corpus-recovery-f2/selection.py --check-training-gate` debe rechazar el entrenamiento. CachésSQLite y checkpoints quedan locales excluidos deGit; hashes y metadatos se conservan. No se copió el texto bruto aGit ni se abrieron evaluaciones selladas.
''')
write('CORPUS_RECOVERY',f'''# Recuperación ejecutada

Raíz real: `/PATH/TO/NEO_HOME/research/neo-architecture-recovery/chinchilla-corpus/`.

- Bruto: `releases/growth-1b-v1-estimated-1000000000/`.
- Curado500 preferido: `curation-v1/runs/500m-refined/release/`.
- Curado1B adicional encontrado: `curation-v1/runs/1b-refined/release/`.
- Versiones100M/250M/500M, stop y master-0001 siguen presentes. Solo documentadas a nivel manifiesto en esta ejecución, no recertificadas íntegramente.
- Ingesta/dedup/normalización/tokenización y logs recuperados: [pipeline-inventory](results/pipeline-inventory.json). Incluye hashes de los scripts y registros originales, sin reproducir su contenido.
- Metadatos de fuentes/licencias: `metadata/`; snapshotV1: `curation-v1/runs/500m/token-certificates-snapshot.sqlite`; cachéV1 actual `curation-v1/token-cache.sqlite`.

{summary}

Inventario de versiones, fechasmtime y hashes: [catalog.json](results/catalog.json). SHA de cada shard: [shard-receipts.json](results/shard-receipts.json). No se localizaron respaldos externos adicionales dentro del ámbito de investigación/evaluaciones inspeccionado; sí versiones locales y snapshot. No se afirma que esa búsqueda abarque medios externos desconectados.

Las vistas curadas son subconjuntos por identidad del maestro, pero no copias textuales estrictas:500Mcontiene2reparaciones y1Bcontiene3. Además411keys del500Mcurado no figuran en1Bcurado; decisiones posteriores distintas, no datos perdidos. Verresults/view-differences.json.

La vista1B refinada existe y está íntegra a nivel de exportación. Esto actualiza el antiguo estado «curación en curso»; no significa aprobación de entrenamiento, derechos o conteo completo.
''')
write('HISTORICAL_RECONCILIATION',f'''# Reconciliación histórica

565.554 bruto =564.789BASE +765SFT; 2.502.353.862bytes de texto total, no tamaño físicoJSONL. Curado500v1.1=257.043BASE,1.219.334.156bytes BASE;765SFT separados. El500bruto intermedio tiene262.168registros; no confundirlo con su derivado curado.

El identificador «1B» procedía de estimacionesV1 de hitos, no de una certificación de tokens. El release1B refinado posterior conserva555.914BASE. `master-0001` declara16.556registros; no es un corpus separado certificado de4.360BASE. La referencia4.360 localizada en `MEASURED_500M.md` significa4.025cuarentenas +335conflictos excluidos de la vista500. No se localizó evidencia de un release independiente con exactamente4.360BASE; esa interpretación histórica queda sin acreditar.

Corte congeladoV1:115.211.015IDs/24.562documentos maestros500;96.453.256IDs/23.108documentos curadosv1.1;233.935pendientes en ese corte. El96.567.319 anterior corresponde a curadov1.0, no se suma ni se transforma enV3.

CachéV1 actual:131.876certificados únicos,390.088.259IDs. Cruce nuevo por SHA con vistas recuperadas:

{table(['Vista','Docs vista','Docs certificadosV1','IDs parcialesV1','Targets parcialesV1'],[(k,x['documents'],*x['v1_partial_exact']) for k,x in cov.items()])}

Estos son certificadosV1 reutilizados, no una retokenización. V3 se informa aparte. Los targetsV1 históricos usanIDs−1; nuestra selecciónV3 usaBOS+texto+EOS y produceIDs_texto+1. Las convenciones difieren explícitamente.
''')
write('SOURCE_INVENTORY', '# Inventario de fuentes y procedencia\n\n'+table(['Fuente','Decisión nueva','Evidencia local','Condición'],[(x['source'],x['decision'],x['evidence'],x['condition']) for x in cat['source_inventory']])+'''\n\n[Catálogo](results/catalog.json) conserva rutas, hashes, tamaños, fechas y estado. [Composición completa](results/integrity.json) identifica fuente/idioma/dominio/split de todos los registros verificados. Las versiones históricas solo-manifiesto se distinguen de las tres vistas verificadas por contenido. CONTEXTUAL está vacío en el bruto1B; SFT no es BASE.\n''')
write('LICENSE_AUDIT','''# Derechos y procedencia

No se infiere permiso por disponibilidad pública. Se recuperó `curation-v1/RIGHTS_AND_PROVENANCE.md`, tarjetas y licencias archivadas, y se creó una decisión nueva sin modificar manifiestos antiguos. Es una compuerta operativa conservadora, no una garantía jurídica global.

**APROBADO:** Click BSD-3-Clause y Requests Apache-2.0, archivos exactos y licencias cotejados; preservar notices/atribución. CPython PSF y condiciones incluidas en suLICENSE, nueve archivos con SHA coincidente, siete retenidos por calidad; todo el repositorio queda fuera de F2train por reserva de familia de testD0, incluida otra revisión. No se inspeccionó el contenido de evaluaciones selladas.

**CUARENTENA:** Wikipedia (CC-BY-SA3.0/GFDL según tarjeta archivada, obligaciones de atribución/condiciones pendientes de cerrar para esta selección), OASST (condiciones/PII/procedencia individual), FineWeb2/FineWebEdu/Finemath (licencia de colección no resuelve derechos de documentos subyacentes). D0.1Gutenberg conserva incertidumbre territorial. No se usan para entrenarF2.

**EXCLUIDO para este uso:** registros corruptos/calidad rechazada/conflictos de evaluación y familias reservadas. No se eliminan los originales. SFT requiere otra evaluación y permanece separado.

Responsables y procedencia están identificados por fuente, revisión,URL y hashes en los registros originales; autoría/licencia individual de web no acreditada. No hay aprobación global del corpus masivo. Ver [source_inventory](results/catalog.json), [license hashes](results/v3-counts.json) y [CPython cotejo](results/provenance-checks.json). La siguiente tarea es cerrar condiciones/atribución de una selección recuperada suficiente, no recolectar otro corpus.
''')
write('DATA_INTEGRITY',f'''# Integridad de datos medida

{summary}

{table(['Vista','Problemas medidos'],[(k,json.dumps(a['issues'])) for k,a in r['views'].items()])}

Conteo exhaustivo por streaming, un registro enRAM, SHA dearchivo y texto, longitud UTF-8, JSON y campos obligatorios. Se guardan offsets/metadatos enSQLite derivado, sin duplicar texto. [Relaciones padre](results/integrity.json): `{json.dumps(r['relations'])}`. Diferencias de texto se verifican por key y SHA, no por coincidencia de tamaños.

Los detectores de email/secretos son patrones limitados; cero coincidencias no certifica ausencia de PII, teléfonos, direcciones, contenido sensible o benchmarks. Se reutilizan además las decisiones de calidad originales. Ambos índices refinados pasan `quick_check`; no equivale a auditoría legal ni semántica.

Errores de integración nuevos conservados enlogs: clave SHA distinta entre formatos de manifiesto; se adaptó el lector sin cambiar manifiestos. Errata del hash del tokenizer en el script nuevo corregida contra el artefacto y hash histórico idénticos. No se relajaron comparaciones ni se alteraron fuentes.
''')
write('DEDUPLICATION',f'''# Deduplicación no destructiva

{table(['Vista','Exceso duplicados texto SHA exacto'],[(k,a['base_exact_duplicate_excess']) for k,a in r['views'].items()])}

Las vistas se solapan por construcción. No sumar sus documentos/tokens. No asumir que500Mcurado es subconjunto estricto de1Bcurado:411identidades no retenidas en este último;3textos1B reparados frente al bruto. El muestreoV3 se cotejó contra los SHA de textos curados reales. Comparación de pertenencia por key y de contenido por SHA: `{json.dumps(r['relations'])}`.

Cercanos: se reutilizó el grafo histórico de curación, fingerprints y decisiones. Aristas registradas: {[(k,a['edges']) for k,a in audit.items()]}. Política v1.1: Jaccard.85, partial_shared_5grams64, partial_containment.2, bucket24 y pair_limit100000. No se certifica recall completo ni todas las versiones/forks posibles; no se ejecutó un análisis cuadrático nuevo.

La selección admisible de cinco documentos pasa dedupSHA y normalización whitespace, separación por repositorios y control de shingles train/dev: `{json.dumps(sel['known_train_dev_shared_word_shingles'])}`. Compartir shingles cortos de código no prueba duplicación; cero64-gramas tampoco garantiza independencia semántica. CPython se excluye por familia histórica, incluso archivos/revisiones no idénticos.
''')
rows=[]
for x in r['views']['curated1b']['groups']:
 if x['track']=='BASE_LM_CLEAN':rows.append([x['source'],x['lang'],x['domain'],x['split'],x['documents']])
write('CORPUS_COMPOSITION', '# Composición real\n\n'+table(['Fuente','Idioma declarado','Dominio','Split','Documentos BASE curados1B'],rows)+'''\n\nIdiomas según metadatos heredados/LID, no nueva clasificación independiente. Código=zxx CPython; prosa web/enciclopedia/educación/math tienen etiquetas de dominio, no una segmentación exacta de código incrustado. No se inventa un porcentaje exacto de código dentro de páginas mixtas. Los bytes y longitudes por vista están en [integrity](results/integrity.json), cuantiles completos0/25/50/75/90/99/100%.\n\nEl SFT765 separado incluye525ES/240EN; no se añade al BASE. La mezcla masiva dispone de español e inglés, pero la selección aprobada paraF2 conserva solo inglés de código/exposición. No imponer proporciones bilingües sin derechos cerrados.\n''')
fr=[]
for x in v['strata']:
 ss=[s for s in v['sample'] if s['source']==x['source'] and s['lang']==x['lang']];byt=sum(s['text_bytes'] for s in ss);chars=sum(s['characters'] for s in ss);ids=sum(s['v3_text_ids'] for s in ss);fr.append([x['source'],x['lang'],len(ss),ids,round(ids/byt,4) if byt else 'pendiente',round(ids/chars,4) if chars else 'pendiente'])
write('NEOTOKEN_V3_COUNTS',f'''# Conteos NeoTokenV3 BPE8K

Artefacto `{v['artifact_sha256']}`, fingerprint `{v['fingerprint']}`. PAD256/BOS257/EOS258. RoundtripES/EN/Unicode y determinismo comprobados, artefacto intacto. Solo núcleoBPE; no vistas multiescala como entradas adicionales. Tokens del BPE pueden cambiar al añadir sufijos de texto por merges: el contrato causal opera sobre la secuencia tokenizada fijada, no promete estabilidad de prefijos arbitrarios de caracteres.

Conteo nuevo **exacto parcial:** {vs['exact_sample_text_ids']:,}IDs en{vs['unique_sample_documents']}documentos masivos únicos; {vs['exact_sample_text_bytes']:,}bytes y{vs['exact_sample_characters']:,}caracteres. Además33.987IDs de texto en5documentosD0.1, con25355train/8637dev targetsBOS/EOS. Certificados content-addressed reanudables enSQLite local, no tokensV1 reutilizados comoV3.

{table(['Fuente','Idioma','Docs muestra','IDs exactos','IDs/byte','IDs/carácter'],fr)}

Muestra fija uniforme por estrato,24documentos por fuente/idioma/dominio, seed17005. Estimación exploratoria de los estratos no-code curados1B: **{vs['curated1b_non_code_estimate_ids']/1e6:.2f}M ±{vs['normal_95_halfwidth']/1e6:.2f}M** (intervalo normal95%, muestras pequeñas/colas pesadas). No es conteo certificado ni intervalo robusto en colas; siete documentosCPython reservados quedan fuera de esa estimación. No trasladar esta estimación al bruto o500M.

No hay totalV3 exhaustivo, tokens aprobados masivos ni desglose exacto global por idioma/fuente. [v3-counts](results/v3-counts.json) conserva cada certificado de muestra, pendientes y estimaciones por estrato; [v3-summary](results/v3-summary.json) separa cobertura. Reejecutar`count_v3.py` reutiliza certificados; aumentar muestra es una decisión explícita, no un contador completo oculto. Para terminar el total se debe extender la cola a todos los documentos únicos con checkpoint, previa política de reservas. El corpus entero no necesita completarse antes deF2: sí es obligatorio contar exactamente la selección aprobada suficiente.

Targets futuros: por documentoBOS+texto+EOS→n_text+1, ventanas stride=context−1 cubren cada target una vez, padding/fronteras enmascarados. IDs únicos, targets y exposiciones no son sinónimos. El presupuesto5M no está cubierto con repeticiones.
''')
write('F2_DATA_SELECTION',f'''# SelecciónF2 preparada y bloqueada

Manifiesto reproducible de referencias: [f2-selection.json](results/f2-selection.json). No incluye texto bruto. Fuentes, SHA de documento, ruta original, licencia, split, dominio, idioma y conteosV3 exactos por archivo.

Train3Click: **{sel['train_independent_targets']:,}targets**; dev2Requests: **{sel['dev_targets']:,}targets**. Déficit frente5M: **{sel['deficit_targets']:,}**. Usar197pasadas no sustituye diversidad. No se incorporaron textos en cuarentena ni SFT; CPython tiene reserva de test. No se creó un dev con chunks del mismo documento del train.

Esta selección reutilizaD0.1 como smoke/regresión técnica, no satisface el pilotoF2 bilingüe/diverso. La mezcla grande localizada es suficiente en volumen estimado, pero su selección utilizable no está aprobada. Primero cerrar derechos/atribución y dedup/splits de un subconjunto de las fuentes existentes; después manifestar y contar ese subconjunto. No hace falta descargar otro corpus ni completar todos los tokens del maestro para esa decisión.

`python corpus-recovery-f2/selection.py --check-training-gate` aborta sin entrenar. No hay configuración que rellene el déficit por repetición ni promoción silenciosa deWikipedia/web.
''')
write('F2_ARCHITECTURE','''# F2 construido, sin Hielo niTrapos

F2: vocab8192,width128,4bloquesGQA(4query/2KV),RoPE,preRMSNorm,residuales,MLPSwiGLU4d,refinamiento rápido normalizado2veces,embedding/head tied. **2.082.176parámetros**, todos entrenables. Embedding/head1.048.576=50,36%; atención196.608;MLP786.432;norms1.280;fast49.280. Fórmula8192d+L(15d²+2d)+3d²+3d coincide conSCALING_PROPOSAL.

BaselineTransformer: mismosV/d/L/atención/contexto/head tied, sinfast; **2.032.768parámetros**. Diferencia49.408,2,43% sobrebaseline. No se iguala añadiendo parámetros inútiles. Ambos usan bloques históricos sin alterar su implementación. F2 hereda inicialización normal.02, residuales escalados porsqrt(2L) delBaseline; la receta pequeña anterior no aplicaba ese escalado, diferencia explícita al construir el candidato nuevo, no migración de pesos. No se modifican checkpoints históricos.

`f2.py` implementa construcción/forward/loss/update/checkpoint; CPU FP32. Máscaras segmentadas impiden atención y targets entre documentos, posiciones reiniciadas y padding excluido. Generación por recomputación del prefijo, sinKVcache ni memoria oculta. No hay módulosHielo inactivos inflando el conteo.

Pruebas ejecutadas: perturbación futura, aislamiento de filas/documentos, shift/máscara, todos los gradientes finitos, parámetros actualizados, AdamW completo, seisupdates continuos vs2+checkpoint+4exactos (modelo/optimizador/RNG/cursor), generación técnica y unupdate con IDs realesV3 aprobados. Checkpoints técnicos no son modelos preentrenados. Tests9PASS; receipts enresults. El cursor de estas pruebas recorre fixtures deterministas; la integración del futuro lector corpus necesita una regresión equivalente con su manifiesto final antes del entrenamiento5M.

FLOPs orientativos6P/target:12,493M F2 y12,197M baseline, más atención O(LT²d), RoPE/norm/refinamiento/optimizador.6P sobrecuenta el lookup y no es perfil exacto; no se declara cómputo igual. La medida walltime prima para presupuesto.
''')
benchrows=[]
for k,a in b.items():
 for c in a['cases']:benchrows.append([k,c['context'],round(c['targets_per_second'],1),round(c['mean_update_ms'],2),round(c['stdev_update_ms'],2),round(c['checkpoint_seconds'],3),round(c['restore_seconds'],3),round(c['compute_only_5M_hours'],3),round(c['planning_5M_hours_with_30pct_allowance'],3)])
write('F2_CPU_BENCHMARK', '# Benchmark CPU técnico real\n\n'+table(['Modelo','Contexto','Targets/s','Update ms','SD ms','Save s','Restore s','5M h cómputo','h+30%reserva'],benchrows)+f'''\n\nIntelN100,CPU FP32,1thread,batch2,2warmup+5updates medidos porcaso. Medición final realizada después de terminar el escaneo del corpus; pase inicial concurrente conservado en`f2-benchmark.json`, no usado para presupuesto final. Resultados porupdate, forward/backward/AdamW+clipping: [benchmark](results/f2-benchmark-isolated.json). FixtureIDs sintéticos, sinI/O/tokenización de corpus en la medida. Variabilidad de solo5updates no caracteriza rendimiento largo.\n\nRAM pico proceso (incluye construir/guardar/restaurar modelos): {[(k,round(x['process_peak_rss_MiB'],1)) for k,x in b.items()]}MiB. No esRAM incremental exacta por modelo ni límite de un job largo. Checkpoint contiene modelo,AdamW,RNG,cursor,protocolo/hashfuente.\n\nCoste contratadoCPU:USD0, ningún servicio facturable. Electricidad/amortización no medidas: si potenciaPwatts y tarifaRUSD/kWh, coste=horas×P/1000×R. Dos brazos requieren sumar tiempos;30% es una reserva de planificación, no medición de evaluación/I/O ni garantía. No extrapolación desde296K, ni resultadoGPU. Estos son benchmarks, no5Mtargets entrenados.\n''')
write('TRAINING_READINESS','# Compuertas actuales\n\n'+table(['Compuerta','Estado'],[(k,str(x)) for k,x in g.items()])+'''\n\nEl candidato y baseline existen; la selección final para5Mno. Falta cerrar derechos y preservar atribución de un subconjunto del corpus recuperado, dedup y separación porfamilias/versiones, validar español/código/prosa, contar exactamente sus targets y conectar el lector final con checkpoint de orden/manifiesto. El conteo totalV3 del maestro puede continuar aparte; no es sustituto del permiso ni requisito de acabar todo antes de un subconjunto aprobado.\n\nReferencias de benchmarks globales siguen sinclearance: evaluation_references histórico vacío; no se abrieron sellados. La ausencia de coincidencias no se convierte enPASS. [Evaluación futura congelada](EVALUATION_PROTOCOL.md). Configuración prospectiva enF2_CONFIG.json; `training_authorized=false`, no hay ejecución5M.\n''')
write('DECISION',f'''# Decisión verificable

**NO ejecutarF2 todavía. El corpus existe; el bloqueo es aprobación/selección, no ausencia de datos ni incapacidad para construirF2.**

1. Recuperados bruto1Bobjetivo y500Mcurado en`chinchilla-corpus`, más1Brefinado. BASE564.789/257.043/555.914, respectivamente;765SFT separados, no sumar vistas.
2. Todos los shards de esas tres vistas pasanSHA/JSON/texto/bytes. Curados son subconjuntos por key delmaestro; relaciones exactas enintegrity. Derechos y calidad no se deducen del hash.
3. ConteoV3 nuevo exacto parcial: {vs['exact_sample_text_ids']:,}IDs en120documentos masivos +33.987IDsD0.1. No total1Bcertificado. Datos por fuente/idioma enNEOTOKEN_V3_COUNTS; incertidumbre explícita.
4. Retenidos1B:335.316ESweb+15.756ESenciclopedia;147.986ENweb educativo+41.158ENmath+15.691ENenciclopedia;7CPythonzxx. Son documentos, no tokens. Fuentesweb/enciclopedia pendientes de derechos, no datos aprobados listos.
5. CPython7archivos calidad/permiso documentados, pero familia reservadaD0test; Click/Requests aprobados y conservando train/dev. Seleccióntrainsolo{sel['train_independent_targets']:,}targets, déficit{sel['deficit_targets']:,}. No basta paraF2ni bilingüismo; no llenar con exposiciones repetidas.
6. Reutilizable: shards/inventarios/provenance/curación/grafo/offsets/snapshotsV1, tokenizerV3 y trainer técnico. No repetir ingesta ni auditoríaV1. Cerrar condiciones/atribución de una selección existente, no pedir otro corpus.
7. F2real2.082.176 yTransformer2.032.768 pasan contratos ybenchmarkCPU propio. Horas/coste enF2_CPU_BENCHMARK; no entrenados5M. Falta certificar el lector/orden del dataset final con reanudación, no otraarquitectura.
8. No es necesario acabarV3exhaustivo de todo el maestro para entrenar un subconjunto; sí exactamente contar, verificar y aprobar almenos5Mtargets independientes +dev. No se certifica contaminación global contra benchmarks ausentes.

Siguiente intervención única: **preparar un subconjunto suficiente de fuentes recuperadas cerrando sus derechos/atribución y splits**; después exactoV3 y regresión del lector final. MantenerF2, Hielo/TraposOFF, evaluación congelada. Entrenamiento posterior requiere autorización; no gastar ni ampliar modelo ahora. Histórico intacto, evaluaciones selladas cerradas.
''')
print('Wrote fifteen substantive reports + frozen evaluation')
