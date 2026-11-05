from common import *
import datetime
s=json.loads((ROOT/'results/summary.json').read_text());data=s['data'];perf=s['performance'];nll=s['nll_real_weighted']
def write(name,text):(ROOT/(name+'.md')).write_text(text.strip()+'\n')
table='| Brazo | Parámetros activos | NLL train real inicial → final | NLL dev real inicial → final | Targets/s | Tiempo 64 updates |\n|---|---:|---:|---:|---:|---:|\n'
for k,p in perf.items():
 n=nll[k];table+=f"| {k} | {p['trainable_parameters']:,} | {n['initial']['train']['nll']:.4f} → {n['final']['train']['nll']:.4f} | {n['initial']['dev']['nll']:.4f} → {n['final']['dev']['nll']:.4f} | {p['targets_per_second']:.1f} | {p['seconds']:.3f}s |\n"
write('README',f'''# CryoCCM — Language Bridge V1

Implementado y ejecutado en CPU FP32, rama `cryo-language-bridge-v1`, base `1841b99`; evidencia de Addressable estable `5f2a166`. Trapos aprendido OFF. Modelo pequeño, inicialización nueva: no se migraron pesos simbólicos ni históricos.

**Puente autoregresivo operativo; utilidad lingüística de Hielo no demostrada; pretraining significativo bloqueado.**

{table}

16 tests únicos PASS (`results/release-tests.log`), tres smoke tests de 64 updates/semilla17 y 12.537 targets expuestos por brazo. Sin GPU, Chinchilla, servicios pagos ni evaluaciones selladas. Generación técnica válida pero repetitiva: los seis prompts fijos producen 24 puntos. La pérdida no demuestra comprensión.

Leer LANGUAGE_ADAPTER.md: sustitución explícita del contrato de eventos DSL por escrituras deterministas de frontera, y consultas por token. No es un extractor semántico. MEMORY_EVALUATION.md registra 25% en cuatro opciones para todos, sin ventaja de Hielo.

## Ejecutar

Desde este worktree, verificación sin entrenar:
```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python language-bridge/extra_tests.py
sha256sum -c language-bridge/SHA256SUMS
```
Reproducción completa exclusivamente en salida nueva (otros ~17s de entrenamiento, más tests/evaluación):
```bash
bash language-bridge/reproduce.sh /PATH/TO/NEO_HOME/research/neo-architecture-recovery/language-bridge-reproduction-NEW
```
El script rechaza directorios existentes; los checkpoints originales nunca se sobrescriben. Reutiliza los entornos locales Python3.11/Torch y V3 tokenizers0.23.3/regex2026.9.29, sin instalar paquetes ni modificar V3. La identidad está en results/summary.json y SHA256SUMS. Texto local de fuentes en results/data.json, deliberadamente ignorado por git; se reconstruye desde fuentes D0.1 ya adquiridas y hashes, sin nueva descarga.

Artefactos: model.py; engine.py; build_data.py; evaluation.py; tests.py/extra_tests.py; results/*-final.pt (locales, carga weights_only); curvas.csv; generaciones con bytes exactos; manifests de fuentes/licencias/tokenizer y métricas por idioma/dominio. Resultados negativos conservados. No se autoriza automáticamente un siguiente entrenamiento.
''')
write('ARCHITECTURE_INVENTORY','''# Inventario real

Referencia inspeccionada: addressable/address_model.py y vendor/cryo_historical.py; estabilidad/README.md y DECISION.md; contract-v2/README.md y DECISION.md. Trapos V2 falló y permanece congelado.

| Componente | Estado anterior | Puente ejecutado |
|---|---|---|
| Foreground | Block histórico GQA/RoPE/RMSNorm/SwiGLU funcional | Una capa, width32, atención causal local16 |
| Refinamiento rápido | Dos iteraciones normalizadas | Mismas ecuaciones, sin profundidad nueva |
| Hielo | Matriz8×32 y Delta direccionable funcional en DSL | Misma representación y ecuación; nueva interfaz determinista |
| Extracción | Registros de4 IDs y `=`/`!`/`;` | Incompatible con texto libre; parser eliminado de esta ruta |
| Lectura | Dirección de entidad difundida dentro de registro | Dirección del token actual, sin entidad oracular |
| Cabeza LM | Proyección ligada a embedding, vocab8192 con IDs DSL | Vocab V3 real8192 y embeddings recién inicializados |
| Entrenador | Respuestas simbólicas y diagnósticos | Cross-entropy de siguiente token, padding/fronteras enmascarados |
| Generación | Evaluación simbólica | Session incremental acotada + continuación guardable |
| Tokenizer | V3 BPE8K real provisional | Integración comprobada, multiescala no usada como entrada |
| Corpus | D0/D0.1 con permisos/defectos distintos |8 documentos naturales locales +32 relatos controlados train |

No existía una ruta de escritura semántica validada para lenguaje libre. Este puente es un adaptador explícito, no una continuación automática del certificado simbólico. No se reutilizaron embeddings ASCII como si sus IDs fueran BPE. No hay parser de entidades, Trapos, RAG ni KV cache oculto. Los certificados de CUDA/BF16 anteriores no se transfieren.
''')
write('LANGUAGE_ADAPTER','''# Contrato del adaptador

`model.py`: embeddings E8192×32 compartidos con LM head; Block histórico causal (GQA/RoPE local); refinamiento rápido de dos pasos; matriz Hielo H8×32 inicialmente cero. Trapos OFF. Cada documento comienza en cero. EOS258, BOS257, PAD256. Una conversación fuente completa es un documento; sus roles se conservan en texto, sin máscara SFT.

Para cada chunk de hasta16 tokens:

1. x = Block(E(tokens), máscara causal). RoPE reinicia posiciones0…15; no embeddings absolutos nuevos.
2. q_t = normalize(address(E(token_t))). r_t = read(address_out(q_t H_previo)).
3. f = x; repetir dos veces f = RMSNorm(f + tanh(fast([f,x,r]))).
4. logits_t = Eᵀ RMSNorm(f_t + r_t).
5. Solo tras un chunk completo: k=q_último; v=tanh(event_value(f_último)); H_nuevo=H+k⊗(v−kᵀH).

La matriz, dimensiones, Delta, proyecciones y refinamiento se conservan. **Cambian el calendario de escritura y la construcción de consultas**: el original usa entidad y valor en posiciones sintácticas distintas, y difunde claves de entidad dentro de cada registro; el puente usa el token final y consultas por token. El contraste A/B prueba este adaptador, no demuestra equivalencia con el comportamiento aprendido por el DSL. Son cambios inevitables y declarados de interfaz, no pesos migrados ni extracción semántica.

H_nuevo jamás se utiliza para los logits de su propio chunk. No se escribe un fragmento parcial. No hay labels, entidades del oráculo, decoder auxiliar ni aceptación aprendida en el forward. Usar el último token puede producir direcciones de puntuación repetidas y sobrescritura; no está resuelto el direccionamiento lingüístico.

En entrenamiento, gradientes atraviesan H entre chunks de una ventana128; se truncan al reiniciar cada ventana. Documentos fuente se guardan completos, pero las ventanas128/stride127 son unidades de optimización con offsets, no documentos nuevos: un token solapado permite cubrir cada target una sola vez en el recorrido completo. No se mezcla texto de documentos diferentes. El packing admite segmentos y reinicia H en cada frontera.

Session guarda H, pending (0…15 IDs), session_id y chunks completados. Cada token recalcula el prefijo local pendiente: correcto pero no KV-cache eficiente. Al terminar el chunk, descarta sus tokens crudos y persiste únicamente H; un session_id distinto exige reset explícito. La generación incluye todos los tokens de texto y EOS, enmascara PAD/BOS/roles/reservados; bytes generados pueden ser UTF8 inválido y se guardan exactamente antes de una visualización con reemplazo. El decodificador estricto no se altera.
''')
write('TOKENIZER_COMPATIBILITY',f'''# NeoToken V3: compatibilidad medida

Artefacto real preexistente `../neotoken-v3/artifacts/bpe-8192.json`, fingerprint `{FP}`, {s['tokenizer']['artifact_bytes']} bytes. Carga JSON restringida y fingerprint esperado, sin pickle. Algoritmo byte BPE, vocab8192; bytes0…255, controles256…266, reserva267…511, merges512…8191. PAD256/BOS257/EOS258 explícitos. Sin UNK ni normalización Unicode destructiva. Los controles literales en texto no inyectan roles especiales.

Tests ejecutados: encode_reference Python = encode nativo sobre ES/EN, código, Unicode; roundtrip exacto acentos, emoji, combinaciones, NUL, espacios, Markdown/control literal y fórmulas; bytes0…255 por encode_bytes/decode_bytes; vacío; recarga con IDs iguales; rechazo de surrogates y controles en token_bytes; StreamingEncoder con trozos1/2/7bytes y StreamingDecoder incremental. PASS en release-tests.log.

Una tokenización BPE completa de un prefijo puede cambiar en su última pieza al añadir texto: no se promete que encode(prefijo) sea prefijo literal de encode(texto completo). El encoder streaming retiene piezas abiertas y emite IDs equivalentes al texto completo al terminar. La causalidad del modelo se prueba sobre los IDs fijos ya adquiridos; ninguna vista calculada con el futuro entra al forward.

Prueba local de216.000 bytes: encode {s['tokenizer']['encode_utf8_bytes_s']:.0f} bytes/s, decode {s['tokenizer']['decode_utf8_bytes_s']:.0f} bytes/s. Repetición corta, no benchmark exhaustivo de corpus. Estructuras multiescala existen como sidecars, incluidas rutas offline; no se consumen aquí ni se les atribuye causalidad sin contrato.

**Apto mecánicamente para este smoke test**, todavía candidato provisional: código, conversación, compresión óptima y selección de vocabulario final no certificados universalmente. V1/A4 intactos; ninguna migración de IDs o embeddings históricos.
''')
write('TRAINER_CONTRACTS','''# Contratos del entrenador

16 tests únicos ejecutados en extra_tests.py (incluye las8 pruebas de tests.py), todos PASS; no sumar ambas ejecuciones como24 pruebas distintas. Logs iniciales y final preservados.

- Causalidad train/eval: cambiar sufijo desde posición21 no cambia logits anteriores, tres brazos; dropout0, CPU FP32, tolerancia1e-6.
- Atención por documento, independencia entre filas, padding y packed/unpacked: salida de documentos juntos coincide con separada; logits en padding cero. Loss shifted se compara contra CE manual; excluye cruces de documentos y padding, incluye EOS legítimo.
- Gradientes finitos y no ausentes para todos los parámetros activos; cambian tras AdamW; identidad exacta de grupos sin duplicados ni huérfanos; estado AdamW para cada parámetro activo. Sin módulos reconstruidos después de crear optimizador.
- No-Hielo congela deliberadamente address/event_value/address_out/read. Transformer congela además fast y fast_norm. Estos parámetros siguen asignados para mantener inicialización compartida, pero no se contabilizan como activos.
- Gradiente de un logit posterior alcanza embeddings escritos en chunk anterior; actualización rank1 sin alterar logits del chunk actual; no-Hielo es invariante al prefijo que salió de ventana.
- Generación incremental vs forward completo: atol2e-6/rtol1e-5. Nuevo session_id sin reset rechazado. Sesión guardada después23tokens (H y prefijo pendiente) continúa exactamente hasta39tokens tras recarga segura.
- Reanudación completa:8 updates continuos vs3+save/restore+5, tres brazos. Igualdad exacta de parámetros y todos los tensores/contadores AdamW al final. Se guardan torch/Python RNG, cursor, updates/microsteps, orden, datasetSHA, tokenizerFP, config, acumulación1 y schedulerNone. No NumPy/AMP/DDP/worker RNG utilizado. Sin acumulación parcial pendiente.

Reanudación certificada exclusivamente CPU FP32 monoproceso, dropout0, un thread. No transferible automáticamente a CUDA, AMP, multiproceso ni generación con muestreo aleatorio. Checkpoints torch.load(weights_only=True), .pt locales ignorados por git y hasheados. Código histórico intacto; freeze protocol.json antes de entrenar.
''')
write('DATA_READINESS','''# Datos del smoke test

Se reutilizaron fuentes originales ya adquiridas D0.1; no nueva descarga ni Chinchilla. build_data.py verifica SHA de texto, licencia declarada, roundtrip, separación de grupos y splits.8 documentos naturales:4 conversaciones OASST train (2ES/2EN),2dev (1ES/1EN), documentación Click train EN y archivo Requests dev EN. Conversaciones completas con roles, párrafos/código originales; no SFT.32 relatos sintéticos train,16ES/16EN, autoría del script identificada, cada entidad con cuatro valores por idioma; no se presentan como literatura o lenguaje natural adquirido.

Datos y licencias están referenciados por documento en results/data-manifest.json. Aviso OASST Apache2, Click BSD3 y Requests Apache2 contrastados con archivos locales de licencia hasheados. La licencia de colección no prueba todos los derechos individuales ni calidad factual; uso local de ingeniería, sin publicar textos. No revisión humana independiente. Revisión de agente y búsqueda de emails no equivalen a certificación exhaustiva PII; errores originales no se corrigen silenciosamente. Material Gutenberg se excluye por condicionamiento jurisdiccional.

Sin hashes exactos ni familias compartidos train/dev; cero coincidencias normalizadas de12palabras. Esto no demuestra ausencia de toda paráfrasis/contaminación de fuentes. Se respetan splits previos y no se abre test sellado. Dev solo evalúa; no selecciona pasos, prompts o hiperparámetros.

Inventario exacto por split/idioma/dominio/bytes/IDs/targets: results/summary.json. Train contiene37 documentos, dev3. El train natural tiene5866 targets de recorrido; el sintético1884. Dev natural1705. Targets expuestos realmente por brazo12537, con repeticiones; NO son12537 tokens únicos nuevos. No hay dev sintético usado para ajustar entrenamiento; diagnóstico nuevo de memoria se evalúa después, separado y sin cambios posteriores.

Faltan narrativa natural independiente con derechos verificados, más código train, más familias y conversación/contexto con cobertura suficiente. Este panel habilita ingeniería, no una dieta de pretraining ni conclusiones poblacionales. Los originales completos permanecen en data.json local y fuentes D0.1; ventanas guardan IDs, documento y offset.
''')
write('SMOKE_TESTS',f'''# Smoke tests lingüísticos ejecutados

Protocolo fijado en protocol.json antes de entrenar: tres brazos, semilla17,64updates, batch2, ventanas128, chunk16, FP32CPU, un thread; AdamW .003, betas(.9,.95), decay.01, clipping1. Checkpoint final fijo, sin selección por dev. Cada brazo recibe idéntico orden y12.537 targets; pérdidas solo siguiente token, sin pérdida auxiliar.

{table}

El promedio real pondera targets y separa los relatos sintéticos; results/smoke-*.json conserva NLL/PPL por ES/EN/dominio y cada update/gradiente. ES dev conversación solo273 targets y EN código1251 dominan métricas distintas: el agregado no basta. Hielo obtiene NLL dev real7.1039 vs7.2575 sin Hielo, pero una semilla/panel mínimo no permite atribuir una ventaja general ni retención selectiva. Transformer no es B0 histórico certificado: bloque convencional del mismo origen, menos parámetros activos y mayor visibilidad; se etiqueta explícitamente.

Las seis generaciones fijadas (2prompts×3brazos) resultan en24puntos cada una. Se registran IDs, byteshex, SHA y validez UTF8; todas válidas en esta ejecución. La ruta de generación está operativa, la generación lingüística sigue siendo incoherente/repetitiva. Pérdida menor no acredita entendimiento ni utilidad de Hielo. No se extendieron updates ni se eligieron muestras favorables.
''')
write('MEMORY_EVALUATION','''# Evaluación distante: resultado negativo acotado

16 relatos nuevos controlados (ES/EN×retención/corrección×4colores), en results/memory-fixtures.json. Son textos authored experimentales, no hechos de fuente ni un benchmark de comprensión. Prefijo con hechos, otra entidad y distractores largos, consulta posterior. La respuesta válida viene de la construcción, nunca se pasa al forward. El prefijo se alinea a frontera16 con IDs byte-espacio explícitos y la consulta ocupa menos16tokens.

Antes de consultar se descartan tokens previos; Session solo guarda H8×32, pending vacío, session_id y contador. No-Hielo no tiene ninguna ruta al prefijo; test de invariancia confirma ausencia de acceso accidental. Transformer conserva todo el prefijo explícitamente como control con más información. Se reportan alternativas de continuación con logprob media por token para controlar longitudes, no exactitud de generación libre. Cada grupo tiene solo4casos; azar de referencia25% para cuatro etiquetas balanceadas.

Resultado: **todos los modelos25%**, tanto ES como EN, retención y corrección. Hielo normal/reset/intercambio compatible:25% en cada grupo. No existe ganancia funcional ni caída de exactitud al resetear/intercambiar. Las puntuaciones sí varían: diferencia máxima de logprob media0.02225 al reset y0.02682 al intercambio, sin decisiones correctas adicionales (final-checks.json). Esos resultados no prueban que los estados sean idénticos o que no tengan ninguna información; prueban que este lector/entrenamiento no aprovecha la información en la métrica ejecutada.

El intercambio usa misma entidad y layout con valor vigente distinto; no implica un efecto causal correcto observado. Correcciones obedecen el oráculo del panel. No se ejecutó una batería completa de contrafactuales sobre valor obsoleto y vigente con exactitud conjunta: no se sustituye por un éxito declarado. La compuerta exploratoria de ventaja≥10pp y caída por reset≥10pp NO se supera.

El smoke train contiene lenguaje y relatos de exposición, pero no supervisión específica para responder consultas distantes. Por tanto este negativo no identifica una incapacidad representacional de Hielo ni refuta su evidencia simbólica. El límite local16, direcciones de último token y ausencia de entrenamiento de recuperación son confusiones explícitas. No se ha implementado detección de acontecimientos lingüísticos ni filtrado aprendido. Siguiente contraste, solo con autorización: entrenamiento acotado de recuperación lingüística controlada y baseline local idéntico, antes de considerar escala.
''')
write('PERFORMANCE',f'''# Coste CPU medido

{table}

Hielo aumenta tiempo total de training {100*(perf['ice']['seconds']/perf['no_ice']['seconds']-1):.1f}% frente al mismo foreground sin Hielo, y reduce throughput {100*(1-perf['ice']['targets_per_second']/perf['no_ice']['targets_per_second']):.1f}%. Asignados284096 parámetros en todos; activos280736/284096/277600. Diferencia A/B3360 parámetros activos; embeddings ligados8192×32=262144 dominan el tamaño. No se afirma igualdad de FLOPs.

Promedios/stdev de update y tiempos completos en summary.json. Medición end-to-end incluye construcción local de batches fuera de la curva del update, con128 ventanas en64updates; no profiler. RSS pico del proceso secuencial713.8–715.3MiB es high-water acumulado, no asignación incremental por brazo. Hielo persistente256float32=1024bytes por sesión, además del prefijo local pendiente y activaciones para backward.

Estimación estructural: lectura H y proyecciones cuestan aproximadamente2L(8×32+32×32+32×32) operaciones multiply/add, más2L×32×8 para direcciones y coste de norma; una escritura cada16tokens añade proyección32×32 y Delta rank1. Excluye activaciones, backward, layout y overhead Python: no es medición de FLOPs completos. Atención C usa longitud hasta128 en train y contexto completo mayor en diagnóstico, frente bloques16 de A/B.

Proyección puramente mecánica de100k targets al throughput observado: sinHielo49.7s, Hielo54.4s, Transformer28.6s. No autoriza entrenar ni predice un modelo12M/50M/GPU. Repeticiones, dataset, longitud y evaluación cambian el coste. No hubo GPU, mixed precision ni benchmark CUDA; generación recalcula prefijo de chunk y aún no está optimizada.
''')
write('PRETRAINING_READINESS','''# Compuertas

| Compuerta | Estado demostrado |
|---|---|
| V3 real reversible, IDs explícitos | PASS local/provisional BPE8K |
| Procedencia/licencias | PARTIAL: avisos archivados, derechos individuales OASST no certificados |
| Separación train/dev | PASS exactos/grupos/12palabras en panel; no certificación universal |
| LM causal/máscaras/shift/padding | PASS CPU FP32 |
| AdamW, gradientes y updates | PASS tres brazos |
| Checkpoint/RNG/cursor/orden/reanudación | PASS CPU monoproceso,8updates, sin AMP |
| Generación incremental y sesión | PASS técnica; texto degenerado |
| Baseline local sin Hielo | PASS ejecutado con datos idénticos |
| Tokens/s/RAM | PASS medido; RSS pico acumulado |
| Política de escritura | Documentada/causal; semántica no validada |
| Ventaja funcional en texto distante | FAIL/NO DEMOSTRADA25% |
| Datos suficientes y diversos para pretraining | BLOCKED; sin usar Chinchilla |
| Trapos aprendido | OFF/congelado, no desbloqueado |
| Entrenamiento significativo | NO AUTORIZADO por esta fase; no preparado científicamente |

El puente permite seguir investigación lingüística con modelos pequeños y presupuestos nuevos. Antes de pretraining: cerrar corpus/licencias/dedup/tokenización exacta por su vía independiente, comprobar direccionamiento y recuperación de lenguaje con entrenamiento/evaluación emparejados y exposición suficiente, estimar presupuesto real del tamaño seleccionado, ampliar confirmación y cubrir precisión/hardware que se pretenda usar. No es necesario reabrir Trapos para ello. Ningún certificado de símbolo/CPU se transforma en certificado de lenguaje/GPU.
''')
write('DECISION','''# Decisión

1. **Sí**, CryoCCM-Addressable puede adaptarse y ejecutarse como LM causal: forward/backward, AdamW, shift, generación y reanudación comprobados. Es una instancia nueva pequeña, no un checkpoint simbólico convertido silenciosamente.
2. Faltaban contratos libres de DSL para escribir/consultar, entrenador next-token y generación de sesión. Se implementaron explícitamente. El extractor semántico sigue ausente.
3. NeoTokenV3 BPE8K real pasa encode/decode, referencia independiente, streaming y fixtures Unicode/bytes. Es apto provisionalmente para el smoke; no se modifica ni se declara definitivo/multiescala causal.
4. **No** se demuestra ventaja funcional de Hielo en dependencias largas:25% de cuatro opciones, sin caída al reset/swap. Una mejora pequeña de NLL dev no sustituye esa prueba.
5. Coste CPU observado:1838 targets/s con Hielo vs2014 sin él, aproximadamente9.6% más tiempo total. Una semilla y proceso compartido, no evidencia CUDA.
6. Escritura determinista sirve como interfaz técnica temporal y causal. No está validada como solución de memoria lingüística: clave del último token/puntuación, compresión y lectura por token siguen limitando el puente.
7. Limitan la transición la falta de recuperación entrenada en lenguaje, exposición mínima/diversidad, derechos condicionados y ausencia de un contrato semántico para claves; el diagnóstico no aísla cuál causa el negativo.
8. **No se justifica iniciar pretraining significativo todavía.** El siguiente paso razonable es un único contraste pequeño de recuperación lingüística con objetivo de respuesta comprobable, A/B local idéntico y conjunto independiente, con nueva autorización y presupuesto. No rediseñar Trapos automáticamente, no tocar Hielo/tokenizer simultáneamente ni escalar hasta demostrar utilidad.

Operativo: núcleo BPE, adaptador, LM causal, controles, checkpoint, generación y métricas. Experimental: escritura/lectura lingüística determinista, memoria de largo alcance. Pendiente: calidad de lenguaje, recuperación funcional generalizable y gates de datos/coste. Resultados originales, Trapos negativo y conjuntos sellados permanecen intactos.
''')
if __name__=='__main__':print('REPORTS WRITTEN')
