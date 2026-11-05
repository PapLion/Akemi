from pathlib import Path
import json,collections,hashlib
R=Path(__file__).resolve().parent
s=json.loads((R/'results/conditional-selection.json').read_text());a=json.loads((R/'results/approved-selection.json').read_text());summary=json.loads((R/'results/summary.json').read_text());docs=s['documents']
def put(name,text):(R/name).write_text(text.strip()+'\n')
comp=[]
for split in ['train','dev']:
 for lang in ['es','en']:
  ds=[d for d in docs if d['split']==split and d['lang']==lang]
  comp.append(dict(split=split,language=lang,documents=len(ds),text_ids=sum(d['text_ids'] for d in ds),effective_targets=sum(d['effective_targets'] for d in ds),bytes=sum(d['text_bytes'] for d in ds),characters=sum(d['characters'] for d in ds),text_ids_per_byte=sum(d['text_ids'] for d in ds)/sum(d['text_bytes'] for d in ds),text_ids_per_character=sum(d['text_ids'] for d in ds)/sum(d['characters'] for d in ds)))
(R/'results/composition.json').write_text(json.dumps(comp,indent=2)+'\n')
table='\n'.join('| '+ ' | '.join(str(r[k]) for k in ['split','language','documents','text_ids','effective_targets','bytes'])+' |' for r in comp)
put('README.md','''# F2 Corpus Release V1 — BLOCKED

Se ejecutaron clasificación, atribución, conteo exhaustivo de una selección candidata bilingüe y certificación del lector con documentos aprobados. No se entrenó F2.

- [Decisión](DECISION.md), [derechos](SOURCE_RIGHTS_MATRIX.md), [condiciones pendientes](REMAINING_BLOCKERS.md).
- [Selección y conteos exactos](NEOTOKEN_V3_EXACT_COUNTS.md), [lector](DATA_READER_CONTRACTS.md).
- Base ddbd348; rama neo-f2-corpus-release-v1. Ningún archivo histórico fue modificado.

Reproducir: `python f2-corpus-release/release.py` con el entorno V3/PyTorch existente; `python f2-corpus-release/reader.py`; `python -m unittest discover -s f2-corpus-release -p 'test_release.py' -v`. release.py reutiliza certificados por SHA; no entrena ni descarga corpus. Solo recupera cuatro documentos pequeños de evidencia oficial. SQLite/token arrays y checkpoint de integración permanecen locales, fuera de Git.

Los manifests condicionales NO habilitan el entrenamiento: Reader exige APPROVED. El entrenamiento significativo sigue desautorizado.''')
put('SOURCE_RIGHTS_MATRIX.md','''# Matriz de derechos para F2 BASE

| Familia | Documentos BASE retenidos | Estado | Decisión ejecutada |
|---|---:|---|---|
| Wikipedia EN | 15.691 | CONDITIONAL | Ledger individual, revisión HF fijada verificada, selección y atribución creadas; excepciones de contenido externo pendientes |
| Wikipedia ES | 15.756 | CONDITIONAL | Igual; no se declara todo el dominio aprobado |
| FineWeb2 ES | 335.316 | QUARANTINED | Sin prueba de derechos por documento/sitio subyacente |
| FineWebEdu EN | 147.986 | QUARANTINED | Licencia del dataset no despeja automáticamente contenido web incorporado |
| FineMath EN | 41.158 | QUARANTINED | Procedencia y derechos del contenido matemático subyacente sin cierre |
| CPython | 7 | EXCLUDED | Reserva histórica de evaluación, aunque exista licencia |
| OASST | 765 SFT separados | CONDITIONAL | Sin conversión a BASE: falta reconstrucción de árboles, revisión de texto de terceros, privacidad y contaminación |
| Click D0.1 | 3 train | APPROVED | BSD-3-Clause y hashes ya certificados; retenidos |
| Requests D0.1 | 2 dev | APPROVED | Apache-2.0 y hashes ya certificados; fuera de train |

results/source-decisions.json conserva decisiones agregadas para TODAS las decisiones históricas del índice. results/wiki-rights-ledger.jsonl clasifica individualmente 31.447 documentos retenidos. No se resucitan las 411 exclusiones posteriores ni se abre test. No se modificó ningún manifest original.''')
put('LICENSE_EVIDENCE.md','''# Evidencia recuperada y verificada

La card archivada wikimedia--wikipedia.md coincide SHA-256 **a0f2055ac612f924721e9981fa2a49a18adec1c67cc8026f6c97d12f17211b21** con la [revisión pública b04c8d1](https://huggingface.co/datasets/wikimedia/wikipedia/raw/b04c8d1ceb2f5cd4588862100d08de323dccfbaa/README.md). Así se resolvió la identidad documental de la declaración de licencia. El aviso sobre dumps 20231101 ausentes afecta bbc/dga/zgh; no señala EN/ES. No certifica por sí mismo la revisión exacta de cada artículo.

La card declara CC BY-SA 3.0/GFDL para texto original, no un permiso irrestricto para todo material incorporado. [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) permite copia y adaptación con condiciones de atribución y licencia. La [implementación Wikimedia](https://meta.wikimedia.org/wiki/Licensing_update/Implementation) admite atribución mediante URL del artículo y señala requisitos para contenido externo. No se impone GFDL adicional a todos los artículos: existen contenidos solo CC compatibles.

Se guardaron evidencia íntegra, URL, fecha UTC y SHA en evidence/ y results/evidence.json. Las versiones actuales no se presentan como términos exactos del snapshot de 2023. La card pública OASST actual declara Apache-2.0; la metadata local fija fdf72ae0827c1cda404aff25b6603abec9e3399b. Su comparación histórica exhaustiva no se ejecutó y no se aprueba una conversión BASE.

No se resolvió por suposición si los pesos entrenados constituyen adaptaciones ni obligaciones de una futura publicación de pesos. No es una conclusión jurídica de incompatibilidad: es una condición de revisión del uso previsto. La licencia general tampoco certifica derechos de privacidad, citas y materiales de terceros de cada documento.''')
put('APPROVAL_DECISIONS.md','''# Decisiones de aprobación

Se mantuvieron cinco documentos APPROVED con evidencia específica de licencia y hashes. No hubo nuevas aprobaciones.

Wikipedia pasa de una referencia genérica a un ledger individual reproducible: hash limpio, clave, idioma, familia, split histórico, componente de deduplicación y revisión de adquisición. En los candidatos además se verificaron URL, título, ID, shard y fila reales, y se creó atribución. Se cerró la condición técnica de identificación y confección de créditos. Quedan condiciones de alcance y material externo: el texto plano carece de historial detallado, avisos de atribución externos y revisión histórica individual. No se aplicó un detector regex como sustituto de esa revisión.

La clasificación CONDITIONAL no significa que Wikipedia sea ilícita ni que sea necesaria autorización individual de cada contribuidor. Significa que este release, bajo la regla solicitada de no inferir derechos para todos los textos, todavía no tiene evidencia suficiente para aprobar indiscriminadamente sus documentos. No se adjudica automáticamente un debate sobre entrenamiento y ShareAlike. QUARANTINED no equivale a incompatibilidad probada.

Los web/math quedan en cuarentena; CPython excluido por evaluación; OASST no se incorpora a BASE. Ningún documento se borró ni movió en el corpus original.''')
put('ATTRIBUTION_MANIFEST.md','''# Atribución materializada

results/attribution.jsonl contiene una entrada por artículo candidato: título, crédito a Wikipedia contributors, URL de artículo y de historial, licencia declarada y enlace, revisión HF, shard/fila, hash limpio y modificaciones conocidas. No contiene los textos.

El historial se enlaza para identificar contribuciones; no se afirma que el historial actual sea la revisión original extraída. La revisión HF fija los bytes del dataset. La modificación declarada incluye extracción mwparserfromhell y reparaciones históricas registradas. No se publica una lista ficticia de autores ni se elimina una atribución conocida.

Para Click/Requests se reutilizan los hashes y licencias de corpus-recovery-f2/results/f2-selection.json y los textos LICENSE locales. La atribución técnica generada no resuelve avisos adicionales perdidos durante extracción de contenido externo; external_attribution_review sigue PENDING.''')
put('F2_CORPUS_SELECTION.md','''# Selección reproducible

Hay dos manifiestos separados:

1. approved-selection.json: 3 documentos train Click y 2 dev Requests, 25.355/8.637 targets. Único permitido al lector.
2. conditional-selection.json: Wikipedia EN/ES de la vista 1B actual; no autorizado para entrenamiento.

Selección candidata por SHA256(clave), sin usar contenidos de test; artículos completos hasta 30.000 IDs de texto por artículo. Se conserva split histórico train/dev, se excluyen conflictos de componente y hashes duplicados antes de aceptar un documento. Las vistas 500M/1B no se suman. La elección no usa resultados de entrenamiento. Se retienen suficientes artículos para superar 2,5M targets train y 100k dev por idioma; el exceso es disponibilidad, no permiso de exceder el presupuesto futuro de 5M.

La fuente dominante sigue siendo Wikipedia: dos ediciones y muchos artículos no equivalen a muchas familias de fuentes independientes. Código/documentación aprobados son mínimos y solo EN. No se inventa una mezcla ideal. No hay repetición de exposiciones para rellenar el déficit. La reserva independiente de trabajos/código permanece fuera de train.

Si se resuelven derechos, el próximo manifest autorizado deberá fijar exactamente el corte de 5M targets y sus máscaras; esta selección condicional no es todavía un release entrenable.''')
put('NEOTOKEN_V3_EXACT_COUNTS.md',f'''# Conteo V3 exhaustivo de la selección candidata

| Split | Idioma | Documentos | IDs texto | Targets BOS-texto-EOS | Bytes texto |
|---|---|---:|---:|---:|---:|
{table}

Fingerprint V3: 813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b. Artefacto sin modificaciones. Cada documento se tokenizó, se comprobó round-trip Unicode y codificación repetida idéntica; la caché registra SHA del texto y fingerprint. Los tests verifican longitudes de arrays para todos los seleccionados.

Son **5.006.879 targets train candidatos** y **212.105 dev candidatos**, no aprobados. Tokens de texto = targets menos un EOS supervisado por documento. BOS es entrada, no target inicial. No se predicen transiciones entre documentos. Ventanas de T tokens con stride T-1 mantienen cada target una vez, incluido EOS; padding ignorado. Las cifras se refieren a posiciones tokenizadas en documentos distintos, no a vocablos únicos ni a exposiciones repetidas.

Conteo de la selección completo, corpus maestro completo NO contado. Certificados reanudables counts.sqlite y IDs uint16 locales; hash de certificados en LOCAL_SHA256SUMS.json. Tiempo de adquisición+preparación+conteo: {summary['seconds']:.2f}s; no es benchmark puro de tokenización. Aprobado sigue siendo 25.355 train / 8.637 dev.
''')
put('TRAIN_DEV_ISOLATION.md','''# Aislamiento train/dev

Siete tests adicionales PASS. Para candidatos, conjuntos de clave, SHA limpio, familia documental y componente de deduplicación son disjuntos. Ningún split test histórico se abrió. Se usa únicamente keep de 1B refinado, por lo que las 411 exclusiones posteriores no entran.

Se reutiliza el grafo de near-dedup histórico (Jaccard 0,85 y otros criterios de aquella ejecución), no se vuelve a auditar todo el corpus. Su recall no es exhaustivo: no certifica ausencia de traducciones, paráfrasis ni contaminación con todos los benchmarks públicos. EN/ES pueden compartir conceptos; no se afirma separación semántica total. Esta limitación mantiene deduplicación/splits en CONDITIONAL para el release candidato hasta revisión específica. Los cinco documentos aprobados conservan separación por repositorio y el chequeo previo de shingles sin coincidencias.

No se utilizaron conjuntos sellados para elegir documentos, modelos ni proporciones. Las claves de test se contabilizan como metadatos, sin leer sus textos.''')
put('DATA_READER_CONTRACTS.md','''# Contratos del lector adicional

reader.py solo acepta documentos APPROVED y verifica SHA, V3 y longitud. Una fila contiene una ventana de un documento; no existe atención ni target cruzado entre documentos. Orden barajado determinista semilla17; identidad del manifest y orden protegidos en estado. Un cambio de configuración o manifest falla al cargar cursor.

Se ejecutaron 4 updates técnicos continuos frente a 2+2 interrumpidos sobre documentos aprobados reales. Total computado: 6 updates al contar la repetición de comparación. Coincidieron exactamente parámetros, AdamW, RNG Python/Torch, cursor, pérdidas y claves/offsets de batches. Checkpoint local integration-resume.pt contiene estados completos e identidad del lector/tokenizer/código. La integración tiene dropout cero; aun así RNG se conserva. Se probaron causalidad real, aislamiento de filas, padding, shift, cobertura única de 25.355 targets y gradientes finitos.

Siete unittest PASS; results/reader-contracts.json y tests.log contienen evidencia. Se reutilizan sin repetir los nueve tests históricos F2/baseline. No es entrenamiento significativo ni experimento de calidad.

Límite: lector single-process, sin workers ni prefetch. Materializa tokens de los cinco documentos aprobados pequeños. El conteo candidato sí lee por streaming y guarda certificados por documento. El lector escalado de una futura selección aprobada bilingüe todavía no fue certificado: no se oculta como PASS. La config de entrenamiento permanece deshabilitada.''')
b=json.loads((R.parent/'corpus-recovery-f2/results/f2-benchmark-isolated.json').read_text())
budget={k:v['cases'][0] for k,v in b.items()}
put('CPU_BUDGET.md',f'''# Presupuesto reutilizado, sin repetir benchmark

Contexto128, batch2, CPU FP32. F2: {budget['F2']['targets_per_second']:.2f} targets/s; Transformer: {budget['Transformer']['targets_per_second']:.2f} targets/s. Fuentes: corpus-recovery-f2/results/f2-benchmark-isolated.json.

5M por modelo: F2 {budget['F2']['compute_only_5M_hours']:.3f} h de cómputo, Transformer {budget['Transformer']['compute_only_5M_hours']:.3f} h. Con reserva global del30%: F2 {budget['F2']['planning_5M_hours_with_30pct_allowance']:.3f} h, Transformer {budget['Transformer']['planning_5M_hours_with_30pct_allowance']:.3f} h. Reserva no medida específicamente para evaluación; no se disfraza como coste validado del pipeline completo. RAM histórica alrededor de814/825MiB por proceso; sin nueva medición de entrenamiento completo.

Checkpoint histórico F2: escritura {budget['F2']['checkpoint_seconds']:.4f}s, restauración {budget['F2']['restore_seconds']:.4f}s. Evaluación completa, frecuencia de checkpoints y lectura escalada: CONDITIONAL, necesitan parametrizarse con release aprobado. Conteo/preparación de esta selección se midieron aparte; no se añaden al throughput de entrenamiento. Lector pequeño: results/reader-contracts.json.

Alquiler efectuado: USD0. Electricidad/uso del equipo no tarifados. No hay presupuesto GPU ni autorización de entrenamiento. Estas mediciones del equipo son estimaciones de planificación, no SLA.''')
config=dict(training_authorized=False,ready=False,model='existing F2',parameters=2082176,baseline_parameters=2032768,context=128,batch=2,seed=17,lr=.003,betas=[.9,.95],weight_decay=.01,clip=1,precision='CPU FP32',Hielo=False,Trapos=False,maximum_planning_train_targets=5000000,approved_independent_train_targets=25355,repeat_to_fill=False,approved_manifest='results/approved-selection.json',conditional_manifest_not_trainable='results/conditional-selection.json',checkpoint_policy='fixed final; RNG AdamW reader manifest/order cursor; intermediate frequency pending approved full release',evaluation='NLL/PPL by language/domain; document-weighted and token-weighted; fixed prompts; repetition; no sealed evaluations')
(R/'F2_TRAINING_CONFIG.json').write_text(json.dumps(config,indent=2)+'\n')
put('F2_TRAINING_CONFIG.md','''# Configuración preparada, deshabilitada

F2_TRAINING_CONFIG.json mantiene F2=2.082.176 y baseline=2.032.768, contexto128, batch2, CPU FP32, semilla17, AdamW LR0,003 betas0,9/0,95 decay0,01 clip1. Hielo/TraposOFF. training_authorized=false, ready=false. No se genera un comando que entrene 5M repitiendo los 25.355 aprobados.

Evaluación: reutilizar protocolo anterior NLL/PPL por idioma y dominio, curvas por targets vistos, prompts fijos y repetición, comparación baseline. El dev candidato ES107.333/EN104.772 targets sirve para planificar, pero no puede usarse como aprobado hasta resolver derechos. El dev aprobado contiene dos archivos de código EN, insuficiente para conclusiones bilingües o prosa general. Frecuencia y coste total de evaluación aún pendientes de release aprobado. No seleccionar checkpoints por ejemplos anecdóticos.''')
gates={
'provenance':'CONDITIONAL','rights':'BLOCKED','attribution':'CONDITIONAL','integrity':'PASS','diversity_ES_EN':'CONDITIONAL','sufficient_approved_volume':'BLOCKED','deduplication':'CONDITIONAL','splits':'CONDITIONAL','V3_selection_count':'PASS','effective_targets':'PASS','approved_small_reader':'PASS','approved_small_exact_resume':'PASS','full_release_reader':'BLOCKED','evaluation':'CONDITIONAL','budget':'CONDITIONAL'}
(R/'results/gates.json').write_text(json.dumps(gates,indent=2)+'\n')
put('REMAINING_BLOCKERS.md','''# Requisitos concretos restantes

1. Resolver para Wikipedia el alcance de uso/licencia previsto y las excepciones/atribuciones externas de los artículos candidatos. Se dispone de URL, título, ID, shard/fila, hash y revisión HF; falta evidencia histórica por artículo o una revisión documentada suficiente que determine qué avisos externos se requieren. No basta marcar una casilla genérica por dominio. Si no puede recuperarse esa evidencia, excluir el documento afectado y reemplazarlo por otro ya existente y revisable. La decisión sobre obligaciones de modelos/redistribución no la inventa el agente.
2. Tras ello, registrar aprobación individual y conservar créditos/licencia/modificaciones. El déficit aprobado actual es4.974.645targets; el volumen candidato supera ese déficit. No hace falta descargar otro corpus ni terminar el conteo maestro V3 para evaluar este subconjunto.
3. Revisar near-duplicates/contaminación de la selección ya identificada sin abrir conjuntos sellados y congelar splits admitiendo las limitaciones de EN/ES relacionadas. No repetir la auditoría de integridad original.
4. Con el manifest aprobado, certificar streaming del lector a esa escala y corte exacto máximo5M, fijar frecuencia de evaluación/checkpoints y presupuesto global. El lector aprobado pequeño ya tiene reanudación exacta certificada; no atribuir esa prueba automáticamente a millones de tokens candidatos.

Web/FineMath exigen evidencia por fuente subyacente y OASST exige trabajo de transformación/privacidad; no son el camino mínimo para cerrar el déficit. No iniciar otro ciclo de recopilación.''')
put('DECISION.md','''# F2 BLOQUEADO — no listo para autorización de entrenamiento

Se avanzó materialmente: clasificación individual de31.447artículos Wikipedia, identidad de card HF cerrada byte a byte, atribución por artículo candidato, conteo exacto bilingüe y lector aprobado con reanudación exacta. Los candidatos suman5.006.879targets train +212.105dev. No son datos aprobados. La selección aprobada permanece en25.355train +8.637dev; faltan4.974.645targets independientes aprobados.

No se convirtió una licencia genérica en aprobación por documento, ni se resolvió por suposición una cuestión jurídica sobre modelos. Wikipedia sigueCONDITIONAL por excepciones/atribución externa y alcance del uso; otras familias web/math siguenQUARANTINED; CPythonEXCLUDED por reserva; SFT separado. Se preservaron todos los originales y no se entrenó F2.

La barrera principal ahora es documental/de derechos, seguida de congelar la selección aprobada y certificar su lector escalado. No faltan5Mtokens candidatos, otro tokenizer, otro modelo ni una auditoría integral repetida. El conteo exhaustivo del maestro no es necesario para este piloto si se cierra el release seleccionado. No se afirma READY ni comprensión lingüística.

El siguiente trabajo mínimo es resolver condiciones para estos artículos concretos, no descargar más datos. Tras resolverlas, aplicar el corte presupuestario y completar lector/evaluación; después solicitar autorización para entrenar. Ver REMAINING_BLOCKERS.md y results/gates.json para cada compuerta.''')
# Local artifacts excluded from Git still receive verifiable hashes.
local={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.suffix in ['.sqlite','.pt']}
(R/'LOCAL_SHA256SUMS.json').write_text(json.dumps(local,indent=2)+'\n')
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in str(p) and p.suffix not in ['.sqlite','.pt','.pyc']}
(R/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps(comp,indent=2))
