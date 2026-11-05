import json,hashlib,platform,subprocess
from pathlib import Path
import run_addressable as R
O=R.O;D=O.parent
load=lambda n:json.loads((O/(n+'.json')).read_text())
a=load('analysis');g=load('generalization');cost=load('main-cost');mc=load('microfit-cost');lat=load('latent-update-check')
def write(n,s):(D/n).write_text(s.strip()+'\n')
write('README.md','''# CryoCCM-Addressable V1

Implementación y experimento CPU FP32 ejecutados. Asociación inicial y respuesta normal 100% en train/layout; corrección incompleta. **Éxito parcial de asociación; no certificado de filtrado ni de lenguaje.**

Origen: cryo-multiwrite-v1, 3950afc. Rama aislada cryo-addressable-memory-v1. Sin GPU, gastos, corpus, tokenizer ni evaluaciones selladas.

Artefactos: `results/`; datos, curvas de 300 updates, predicciones completas, estados reales, checkpoints, AdamW/RNG/cursor, controles, tests y hashes. `.pt` se conserva localmente y está ignorado por Git. No publicar solo el código y asumir que los checkpoints viajan con Git.

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/test_contracts.py
# Entrenamiento: requiere results/ nuevo; rehúsa sobrescribir microfit.pt.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/run_addressable.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/analyze_addressable.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/generalization.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" addressable/latent_update_check.py
```

Para repetir entrenamientos, usar otro worktree con esta versión y carpeta results vacía. El checkpoint histórico fuente se encuentra en el worktree selective-memory original; no se descarga ni altera. Consultar REPRODUCIBILITY.md y DECISION.md.
''')
write('THEORY.md',r'''# Ecuaciones y procedencia

Hielo: M en R^(8×32), cero por documento. Foreground causal histórico y refinamiento rápido normalizado de dos pasos conservados. No KV cache ni contexto completo oculto.

Para un registro observado de cuatro IDs `op entidad valor ;`, se extrae la clave de la representación de embedding de la entidad: k=normalize(Wk E[token_entidad]). Es una rama causal del input del foreground, deliberadamente independiente de contexto. No se usa la entidad como índice de fila de M ni se suministran valores del oráculo. Los cinco caracteres tienen embeddings aprendidos ordinarios, igual que cualquier token. La clave de consulta comparte exactamente E y Wk.

El valor v=tanh(Wv f_pos_valor+bv) procede del foreground refinado real, causal. Tras emitir los logits del chunk, cada acontecimiento observado `=` o `!` completo aplica, en orden textual:

M' = M + k (v - k^T M)^T.

Con ||k||=1, k^T M'=v^T salvo redondeo. Para otra clave q, la interferencia es proporcional a q^T k; no se garantiza conservación de asociaciones arbitrarias. No se han aumentado dimensiones ni usado slots de entidad del oráculo. Es Delta de beta=1, retención global=1; no equivale a los gates aprendidos anteriores.

La lectura r=q^T M entra por Wout, el módulo read histórico y la misma actualización fast, normalización final y head atado. En una consulta, desde la posición de entidad se reutiliza su clave hasta el final del registro; antes de verla solo se usa el token actual. El estado escrito al final de chunk nunca alimenta sus propios logits.

**Intervención de sistema completo:** direccionamiento compartido, valores por acontecimiento, gramática explícita, escritura determinista y nuevo readout. No permite atribuir causalmente la diferencia solo a escritura, solo a claves ni a parámetros adicionales. La regla anterior escribía incluso chunks de ruido; aquí el rechazo `~` no escribe. Esta ventaja de estructura está declarada y no es selección aprendida.

Referencias primarias: [Miller et al., Key-Value Memory Networks (2016)](https://arxiv.org/abs/1606.03126), distinción clave/valor; [Yang et al., DeltaNet (2024)](https://arxiv.org/abs/2406.06484), memoria matricial editable. Implementación propia de las ecuaciones, sin copiar kernels. [FLASH-LINEAR-ATTENTION LICENSE](https://github.com/fla-org/flash-linear-attention/blob/main/LICENSE) verificada MIT el 31-10-2026; no se importa esa biblioteca. No se presenta este módulo como reproducción de Gated DeltaNet ni se heredan sus garantías/benchmarks. El repositorio local no contiene LICENSE raíz: no se declara resuelta su redistribución.
''')
write('IMPLEMENTATION.md','''# Implementación

`address_model.py`: nueva clase, fábrica y carga estricta weights_only. Foreground, embeddings, fast, fast_norm, read, slow_norm y LM head conservan pesos iniciales bit a bit. Nuevos Wk 32×8 sin bias, Wv 32×32+bias y Wout 32×32 sin bias: 2.336 parámetros adicionales. Se inicializan con seed707 después del decoder seed101.

El antiguo memory_head se retiene físicamente para planificación y trazabilidad, con todos sus parámetros congelados porque sus proyecciones ya no participan. No hay parámetros entrenables huérfanos. AdamW se construye después de crear módulos. Decoder auxiliar idéntico al baseline, solo supervisión inicial con etiquetas de prefijo; no se usa durante inferencia normal.

Formato acotado: registros simbólicos de cuatro IDs alineados dentro de chunks de ocho, documentos de 64 IDs en el experimento. El calendario acepta sintácticamente `=`/`!` terminados en `;`. No resuelve borrado, lenguaje natural o detección libre de acontecimientos. No equivale a filtrar relevancia aprendida. No se modifica NeoToken; estos son fixtures simbólicos ASCII del protocolo anterior.

Estado persistente entre chunks de un forward; reset documental y nuevo estado cero en cada llamada. No se certifica API de streaming entre llamadas con caché del foreground. `intervention=reset/swap` actúa únicamente antes de leer el último chunk.
''')
write('CONTROLS.md','''# Controles de realizabilidad

Ejecutados antes de la variante: diccionario explícito de dos asociaciones, 16 pares de valores y consultas a ambas entidades: 100%. Representaciones explícitas de ocho coordenadas y lector entrenable condicionado por entidad: 100%, CE0,07675 tras100 updates LR0,03. Control de claves intercambiadas:25%; valor cambiado al siguiente de cuatro:0%. `explicit-controls.json` contiene curvas.

Son controles diagnósticos con asociaciones del oráculo, no aprendizaje autónomo de Cryo. El lector explícito se ajusta sobre todas las combinaciones: certifica realizabilidad, no generalización. Test algebraico independiente: dos claves ortogonales, corregir una preserva exactamente la otra. No demuestra que el modelo aprenda claves ortogonales.
''')
write('ENGINEERING.md','''# Contratos ejecutados

`certification.json`: causalidad train/eval por perturbación futura en cortes4,8,12,16,24,32,48; máscaras de padding; permutación de batch; dos documentos concatenados frente a independientes; memoria de prefijo equivalente; gradientes auxiliares finitos no nulos hacia address y event_value; AdamW sin omisiones/duplicados; reanudación exacta3+3 frente a6updates, modelo, decoder, AdamW, sampler, torch/Python RNG, cursor, losses y orden de muestras. FP32 CPU un hilo, dropout0.

`additional-tests.log`: ocho tests PASS, incluyendo pesos iniciales del foreground intactos; máscara del último token sin acceso al prefijo escrito; decoder auxiliar ajeno al forward; exactamente dos eventos escritos por fixture; realizabilidad Delta; todos los parámetros entrenables con gradientes finitos y cambio tras update; ausencia de dependencia de corrección futura en el estado inicial. No se certifica CUDA, AMP o multiproceso.

Los primeros checkpoints conservaron el campo heredado config.updates=150, aunque step=300 y curvas completas registran300. Se preservaron. `checkpoint_metadata.py` genera copias `.certified.pt` con receta real y hash del original, sin modificar pesos, AdamW ni RNG. Es una corrección de metadatos, no otro entrenamiento. El reanudador original verifica identidad del dataset y cursor; sus configuraciones base son fijas en código. No se certifica migración automática de configuraciones arbitrarias.
''')
train=load('main-train')['metrics']['all'];dev=load('main-dev')['metrics']['all']
write('LEARNING_RESULTS.md',f'''# Aprendizaje ejecutado

Microfit:32registros, entidades A/B, cuatro valores cada una,16combinaciones×2órdenes. 300updates, semilla17,batch8,AdamW LR0,003 betas0,9/0,95 decay0,01 clip1. L=CE_respuesta+0,1 CE_inicial; mismo decoder auxiliar anterior. Compuerta fijada antes de entrenar: ambas marginales y conjunta≥90%, CEmedia<0,5. Resultado100% conjunto y lector normal100%; CE_A={load('microfit-gate')['metrics']['ce_A']:.7f}, CE_B={load('microfit-gate')['metrics']['ce_B']:.7f}. Gate PASS.

Contraste principal:160registros, cinco pares cíclicos de entidades,16pares de valores×2órdenes;300updates con idéntica receta. Ambas asociaciones se supervisan solo después de formarse. No se enseñan correcciones en este entrenamiento. Mismos índices de batch que rango1 original, comprobados los300updates. Se reutiliza su ejecución previa inmutable; no se afirma haberla reentrenado.

|Sistema|Conjunta inicial train|Conjunta nuevo layout|Respuesta normal layout|
|---|---:|---:|---:|
|DeltaFast rango1 original|8,125%|6,875%|25%|
|Addressable|100%|100%|100%|
|Explícito diagnóstico|100%|No equivalente|No modelo Cryo|

En Addressable, consultar separadamente ambas entidades y exigir ambas respuestas normales correctas:100% en train y layouts. No es solo un probe. Marginales A/B100%, matrices completas en JSON. CE inicial dev A={dev['initial']['ce_A']:.7f}, B={dev['initial']['ce_B']:.7f}.

Generalización adicional:480casos de pares de entidades no usados juntos en train, mismos cinco tokens de entidad/cuatro valores y layouts desplazados:90% conjunta auxiliar y95% respuesta normal. No vocabulario nuevo. No independencia estadística entre todos los contrafactuales ni confirmación multisemilla.
''')
write('MEMORY_BINDING.md',f'''# Asociación, conservación y actualización

Misma capacidad de Hielo:256floats,1KiB FP32 por secuencia, sin crecimiento con longitud. Es una memoria asociativa distribuida, no256slots discretos.

Formación:100% de ambas asociaciones en train y layouts. Retención tras chunks rechazados:100%; la escritura se omite determinísticamente, no hay selección aprendida.

Panel de correcciones controlado:640casos (preservar/corregir y afectar cada entidad), generados después del entrenamiento como diagnóstico no usado para ajustar. Tras corrección:75% conjunta; cada rol87,5%; entidad efectivamente modificada75%, no modificada100%. Respuesta normal87,5%. Por tanto no está resuelta la actualización semántica fiable.

Diagnóstico de mecanismo: en640eventos, la clave vuelve a leer el vector latente recién escrito con error máximo {lat['max_latent_value_reread_error']:.9g}. Es evidencia de reemplazo algebraico del vector, no de que v codifique correctamente el valor simbólico. Cambiar el operador de corrección `!` por `=` equivalente conserva75%/100%; la novedad de `!` por sí sola no explica el fallo. Permanecen extracción/representación de valor en nuevos contextos y lectura/generalización como explicaciones no aisladas.

El otro panel heredado con escritura inicial desplazada y evento en posición distinta alcanza56,25% conjunta inicial y75% posterior: ver main-corrections.json. No ocultarlo detrás del layout dev perfecto. Las estructuras nuevas afectan el resultado.
''')
write('COUNTERFACTUALS.md','''# Contrafactuales y ablaciones mínimas

Intercambio de los dos valores distintos:120parejas train y120layout,100% en criterio estricto (ambos bindings correctos antes y después); también100% pareja de respuestas normales.

Correcciones:320pares. Cambiar el obsoleto conserva predicción normal100%, pero ambas respuestas correctas87,5%; criterio conjunto de ambos bindings75%. Cambiar el vigente cambia la predicción100%, pero solo75% de parejas responden correctamente ambas veces; criterio conjunto de bindings62,5%. Sensibilidad no equivale a corrección.

Resetear Hielo antes de consulta: respuesta100→25%, cambia75% predicciones. Intercambio dentro del batch16:87,5% respuesta, cambia12,5%. Este intercambio no garantiza valores diferentes en cada pareja; no extrapolar el pequeño efecto como independencia de memoria. La ablación reset es más informativa aquí. Ninguna prueba desactiva memoria durante entrenamiento.

No se han añadido nuevas pérdidas ni realizado nuevas trayectorias de ablación. Controles explícitos con clave errónea y valor erróneo están separados del modelo aprendido.
''')
write('PERFORMANCE.md',f'''# Coste CPU medido

Microfit300updates:{mc['seconds']:.3f}s. Principal300updates:{cost['seconds']:.3f}s. RSS máximo acumulado:{cost['rss_kib']}KiB; no memoria aislada por brazo.

Modelo292.067parámetros frente289.731del baseline; +2.336(0,81%). Entrenables284.096 frente285.539 porque proyecciones antiguas no usadas están congeladas. Decoder auxiliar5.140igual. La menor cantidad entrenable no implica menor capacidad equivalente. Estado256floats igual.

Medición acotada sin profiler,5updates tras2warmups: Addressable{a['timing']['addressable']['update_ms']:.2f}ms/update, rango1{a['timing']['rank1']['update_ms']:.2f}ms. Son87,21/85,25targets de respuesta/s, con16targets auxiliares adicionales/update. La diferencia pequeña de esta muestra no demuestra aceleración estable. Incluye generación de logs y extracción de ambas etapas en pérdidas comunes.

Proxy aritmético nuevo: clave32→8 y lectura8×32 (~1.024FLOPs/token juntos), nueva proyección32→32 (~2.048/token), más valor32→32(~2.048/evento) y transición Delta O(8×32/evento); se excluyen normas,tanh,elementwise,foreground y backward. No es conteo FLOPs medido ni comparación iso-FLOPs. Escrituras reales2/fixture; rango1 actualizaba cada uno de8chunks. Comparación causal de mecanismos individuales pendiente. Sin medición GPU ni extrapolación CUDA.
''')
write('DECISION.md','''# Decisión científica

**Continuar como prototipo de asociación funcional parcial; no promover arquitectura ni afirmar aislamiento térmico completo.**

Sí: Hielo direccionado por claves aprendidas compartidas aprende dos bindings, los recupera por la ruta normal fuera de la ventana local y sigue intercambios de valores en el panel de formación. Es un cambio material respecto a rango1/MultiWrite, no solo un decoder auxiliar mejor.

Límites: escritura determinista con estructura de registros suministrada; no selección Trapos aprendida. Corrección semántica75% en entidad afectada; pares de entidades nuevos90% conjunta y95% lector; otro layout de eventos56,25% inicial. Una sola semilla. No lenguaje natural. No atribuir causalidad única a claves: también cambian extracción por evento, lectura y calendario/retención de escritura. No hay control capacidad/computación igualada.

No se ejecutan semillas adicionales: no se demostró actualización fiable. El umbral conservador de triaje de confirmation-gate.json (≥90% en tres criterios) se documenta como decisión posterior al resultado, no como preregistro. No se seleccionaron semillas ni pesos según dev; checkpoint final300 fijo.

Siguiente cambio mínimo recomendado: **ningún cambio arquitectónico aún**. Confirmar en un contraste de datos prefijado si supervisar acontecimientos de corrección y posiciones variadas con este mismo sistema elimina el error específico de valores corregidos. Incluir control emparejado con la receta actual y posterior confirmación de semillas. No ejecutado aquí. Antes de aislar el beneficio del direccionamiento, añadir control con escritura por evento y calendario idénticos al nuevo sistema, manteniendo lector anterior, en experimento independiente autorizado.

La ruta merece seguir investigándose por su uso funcional de dos asociaciones. No se autoriza pretraining ni CUDA automáticamente.
''')
write('REPRODUCIBILITY.md','''# Reproducibilidad

Origen Git3950afc. Código nuevo solo addressable/. Intérprete y comandos en README. Dependencias importadas desde las carpetas históricas versionadas de este worktree; fuente aprendida DeltaFast seed17 cargada estrictamente con weights_only desde worktree selective-memory original.

Datos train/dev completos y frecuencias en results. Orden de300batches igual al baseline documentado. Semillas modelo fuente17,decoder101,nuevos módulos707; un hilo,CPU FP32,dropout0. Checkpoints incluyen AdamW completo,sampler RNG,Python RNG,torch RNG,cursor,step,microsteps y acumulación. Sin scheduler. Restauración exacta probada después de updates reales.

No se retocó el baseline ni el checkpoint histórico. historical-integrity.json valida SHA256SUMS de MultiWrite; source-manifest.json identifica checkpoint fuente y código padre. `.certified.pt` corrige solo metadatos de receta de las primeras copias preservadas; usar esos archivos para inspección inequívoca. Reanudador del piloto admite ambas copias porque los pesos y estados no cambian; no certifica otras configuraciones.

Las pruebas generales no son un certificado de calidad lingüística ni de selección, y los diagnósticos postentrenamiento no se usaron para nuevas actualizaciones. No se abrió ninguna evaluación sellada. Artefactos enumerados en SHA256SUMS (excluye propio manifiesto y pycache).
''')
# Verify immutable previous experiment against its manifest.
old=D.parent.parent/'cryo-multiwrite-v1/multiwrite';checked=0
for line in (old/'SHA256SUMS').read_text().splitlines():
 h,name=line.split('  ',1);assert hashlib.sha256((old/name).read_bytes()).hexdigest()==h,name;checked+=1
R.dump('historical-integrity.json',dict(previous_manifest=str(old/'SHA256SUMS'),files_verified=checked,all_match=True))
source=D.parent.parent/'cryo-selective-memory-study/selective-memory/results/extend/delta_fast-normal-w16-17.pt'
R.dump('source-manifest.json',dict(parent_commit='3950afc',checkpoint=str(source),checkpoint_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),torch=str(R.torch.__version__),platform=platform.platform()))
