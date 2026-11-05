from experiment import *
a=read('post-audit');r=read('comparison');short=read('short-17');long=read('long-17')
def write(n,s):(ROOT/n).write_text(s.strip()+'\n')
write('README.md','''# Language Binding Diagnostic V1

Contraste CPU ejecutado: dos brazos de 200 updates, semilla 17, batch 8. Resultado negativo de aprendizaje básico bajo la receta fijada; no es un resultado de Hielo.

| Condición | Train respuesta / conjunta | Dev pares nuevos | Dev layouts | Intercambios estrictos dev |
|---|---|---|---|---|
| Hechos cercanos | 25% / 0% | 25% / 0% | 25% / 0% | 0/12 |
| Hechos lejanos | 25% / 0% | 25% / 0% | 25% / 0% | 0/12 |

Ambos producen el mismo token de respuesta para las dos entidades en 24/24 historias de cada panel. No certifican el control corto (conjunta e intercambios >=90%). Se cierra esta línea de memoria lingüística y no se entrena Hielo.

Se conserva el modelo V2 sin cambios. Código en experiment.py/audit.py/tests.py; PROTOCOL.json preregistrado; resultados, curvas, predicciones y checkpoints locales en results/. Artefactos .pt fuera de git, identificados por SHA256SUMS. No GPU, corpus externo, servicios pagados ni evaluaciones selladas.

Ver DECISION.md para el mecanismo observado y sus límites. Reproducción: bash binding-diagnostic/reproduce.sh en un worktree nuevo con results vacío (se niega a sobrescribir evidencias). Los tests sin entrenamiento adicional: Python del entorno local ejecutando binding-diagnostic/tests.py. Se reutilizan sin editar memory-bridge/runner.py y language-bridge/model.py.
''')
write('DATA_PROTOCOL.md','''# Datos y comparación

Train: Nora/Iris, 12 pares ordenados de valores distintos × 2 órdenes × 2 consultas =48 respuestas/24 historias. Dev combinaciones: Nora/Mira, misma gramática; cambia el par de entidades, todos los valores ya son conocidos. Dev layouts: Nora/Iris, “holds”/“holding” en lugar de “has”/“have”, 48 respuestas/24 historias. No es lenguaje abierto: son plantillas controladas originales en inglés. No se ha medido transferencia a español. No se reutilizó ni abrió el confirmatorio V2.

Cada entidad recibe los cuatro valores seis veces por panel. Valores siempre diferentes dentro de una historia; cambiar solo la entidad preguntada exige cambiar la respuesta. Ambas órdenes equilibradas. El oráculo es el valor de la entidad, no la última escritura global. Primera/última escritura global:50%; presencia/pregunta sin hechos:25%; lookup exacto:100%. Este último es control diagnóstico no neuronal.

Los mismos 96 tokens neutrales se colocan antes de los hechos (corto) o después (largo). Se reutiliza exactamente el multiconjunto de tokens: no se vuelve a tokenizar al concatenar segmentos. Train tiene 11 tokens de hechos, prefijo108 y consulta11; hechos cercanos terminan inmediatamente antes de la pregunta. En largo hay96 tokens neutrales entre hechos y consulta. “Últimos16” describe el bloque factual antes de empezar la pregunta, no garantiza ambos hechos dentro de16 tokens del punto de respuesta. Padding de batch solo posterior al último token válido. Las secuencias emparejadas tienen idéntica longitud total, consulta, respuesta y parámetros. Cambian posiciones absolutas/relativas y orden del texto neutral; no se aísla exclusivamente distancia.

Se mantiene el sampler V2: misma permutación semilla17 y1600 respuestas por brazo. Exposición efectiva:800 consultas por entidad; valores402/400/399/399, y199–201 por celda entidad–valor, por el ciclo parcial final. Balance exacto del dataset y de consultas; balance aproximado de valores consumidos, diferencia máxima3. No se oculta esta limitación ni se reentrena para corregirla después de ver resultados. Ver post-audit.json y datasets.json para frecuencias/identidad.
''')
write('QUERY_CONDITIONING.md',f'''# Consulta: ruta real y limitación observada

Los prefijos factuales son idénticos al consultar Nora/Iris. Las consultas difieren en posiciones111/112 del input; posición de respuesta118 (índices cero). Se usa el logit del último token de consulta para predecir un token siguiente ausente del input. Ambas entidades están tokenizadas en varios IDs distintos; no hay colisión de identidad ni unknown.

Antes de entrenar, delta máximo de logits al cambiar solo consulta: {read('initial-query-conditioning')['short']['max_logit_delta']:.8f}. Después, corto: {read('short-query-conditioning')['max_logit_delta']:.8g}; largo: {read('long-query-conditioning')['max_logit_delta']:.8g}. Gradiente a embeddings de consulta corto:{read('short-query-conditioning')['query_embedding_gradient_norm']:.8g}; a prefijo:{read('short-query-conditioning')['fact_embedding_gradient_norm']:.8g}. Acceso y gradientes no implican binding aprendido.

El foreground tiene UN bloque de atención y después operaciones por posición (MLP y refinamiento rápido). En esa única atención Q_t=Wq RMSNorm(embedding(token_t)), con RoPE de t. Para el token final “:” idéntico y misma posición, Q_t es idéntica entre preguntas: delta medido0. Las K/V de los hechos dependen de embeddings locales, no incorporan todavía la pregunta. Por tanto los scores de hechos son idénticos entre consultas. Cambiar tokens de la pregunta afecta el denominador softmax, pero no los cocientes de atención entre tokens factuales. Tras entrenamiento, delta de atención factual relativa:{a['short']['post_attention']['fact_relative_attention_max_delta']:.3g} (ruido FP32), ver audit.py para reconstrucción desde pesos reales.

Esto restringe un mecanismo directo de direccionamiento contextual en esa única capa: el token de respuesta aún no ha integrado la entidad antes de seleccionar hechos. NO prueba incapacidad representacional absoluta: el MLP/normalización final podrían combinar una mezcla de hechos y señal de pregunta. El modelo no aprendió esa combinación bajo esta receta. No se ha demostrado que sea la causa única frente a optimización, ancho32, distribución e inicialización. No se cambió el backbone.
''')
write('SHORT_VS_LONG.md',f'''# Resultado emparejado

200 updates × batch8 =1600 respuestas por brazo, mismo orden e inicialización SHA {a['short']['initial_weights_sha']}.

Corto: CE train {r['short']['train']['all']['nll_answer']:.8f}; largo:{r['long']['train']['all']['nll_answer']:.8f}. En todos los paneles y ambos brazos, entidad A25%, B25%, conjunta0%. Primera/última asociación seguida25%; misma respuesta en24/24 relatos. No hay evidencia de que acercar los hechos rescate el aprendizaje con estas condiciones. No significa que distancia nunca importe.

Corto tiempo entrenamiento:{short['seconds_train']:.4f}s; {short['responses_s']:.2f} respuestas/s; {short['input_ids_s']:.2f} IDs/s. Largo:{long['seconds_train']:.4f}s; {long['responses_s']:.2f} respuestas/s; {long['input_ids_s']:.2f} IDs/s. Pico RSS proceso:{long['peak_process_rss_mib']:.2f}MiB (acumulado del proceso, no asignación aislada de cada modelo). Parámetros asignados284096; entrenables280736,13 tensores. Sin afirmaciones FLOPs medidos ni extrapolación GPU.

La pérdida converge cerca de ln(4), no a recuperación correcta. Una CE finita/reducida no sustituye exactitud. Curvas y gradientes por update en short-17.json/long-17.json; predicciones completas separadas por panel. No selección de checkpoints por dev: únicamente final200.
''')
write('COUNTERFACTUALS.md','''# Intercambios y cambios de consulta

Cada panel tiene24 historias (valores diferentes, dos órdenes). Para cada par no ordenado de colores y orden hay una historia y su intercambio:12 pruebas estrictas, cuatro respuestas obligatoriamente correctas por prueba. Ambos brazos:0/12 en train y en ambos dev.

Cambiar solo consulta manteniendo hechos exige responder el otro color. Ambos brazos:0/24 historias con las dos respuestas correctas,24/24 con respuesta idéntica. La red predice siempre ID5927 en train (un color admisible), no una secuencia desconocida o token especial. No se restringió argmax a cuatro colores: se evalúan8192 IDs. No hay evidencia funcional de consulta condicionada.
''')
write('TRAINER_CONTRACTS.md','''# Contratos ejecutados

Antes de los entrenamientos principales: datasets emparejados, balance y valores diferentes; causalidad train/eval por perturbación futura; aislamiento batch; target en siguiente posición causal; gradiente a consulta y prefijo; reanudación end-to-end continua8updates frente a3+5 en ambos datasets, con igualdad exacta de pesos, estado AdamW, RNG y cursor/orden verificados. Artefactos de ingeniería separados del entrenamiento principal.

Después: siete tests heredados V2 PASS, cinco tests nuevos PASS; checkpoints finales200updates/1600muestras,13 estados AdamW para13 tensores entrenables y parámetros finitos. El decoder es F.linear con embeddings compartidos; no hay cabeza nueva ni pérdida auxiliar. Modelo no_ice con fast intacto; rutas Hielo congeladas/no utilizadas. Mismo peso inicial certificado por hash real de state_dict, no solo hash del archivo fuente.

Checkpoints conservan configuración V2 del runner reutilizado, que incluye campos históricos no aplicables (p.ej.400updates primarios). El presupuesto REAL de este contraste está en PROTOCOL.json y cursor_updates=200; esta distinción es explícita, no se edita retroactivamente el checkpoint. Dataset/order/tokenizer/model_source se verifican al restaurar. PROTOCOL.json y todos los archivos se enlazan al checkpoint mediante manifest SHA de esta entrega. Ningún archivo previo se modifica. La primera ejecución heredada carecía de fixtures JSON ignorados por git; se conserva el log y se copiaron los fixtures V2 sin modificarlos antes de repetir con7/7PASS.

Las pruebas nuevas pueden repetirse sin sobreescribir checkpoints: python binding-diagnostic/tests.py. El ejecutor principal rechaza resultados existentes, y reproduce.sh impide iniciar un segundo entrenamiento sobre ellos. No se abrieron confirmatorios sellados ni se realizaron entrenamientos adicionales de búsqueda.
''')
write('DECISION.md','''# Decisión: detener la línea de memoria lingüística

Ambos brazos fallan incluso en train:25% respuesta,0% conjunta,0/12 intercambios, tras200updates fijados. El control corto no alcanza las compuertas prospectivas. No se entrena Hielo ni se añaden semillas, updates o variantes arquitectónicas aquí.

No se aisló un problema exclusivo de distancia. La consulta llega al modelo y recibe gradientes; las máscaras permiten ambos hechos, hay identidad de inputs/targets correcta y AdamW/reanudación certificados. La red colapsa a una respuesta constante. No se demuestra incapacidad absoluta del foreground ni del tokenizer ni de Hielo.

Observación técnica concreta: una sola capa de atención lee hechos desde la Q del token final idéntico. La entidad consultada no puede condicionar los scores relativos hacia los hechos en esa misma atención; las operaciones posteriores son por posición. Esa limitación se deduce de las ecuaciones y está comprobada con pesos reales antes/después del entrenamiento. Podría todavía aprenderse binding vía mezclas y no linealidades; el fallo actual no demuestra que esa vía sea imposible. Optimización, inicialización, capacidad y composición siguen sin separarse causalmente.

Próxima intervención mínima recomendada, NO EJECUTADA: mantener arquitectura/tokenizer/receta y cambiar únicamente el punto de lectura en un nuevo contraste preregistrado, formulando la pregunta para que el nombre consultado termine justo antes de la respuesta y usando ese último token para el siguiente-token. Así Q sí depende de la entidad desde la única capa. Compararlo con el sufijo común actual, mismos ejemplos/budget, para probar el cuello de condicionamiento sin añadir capas ni memoria. Los nombres son multitoken; preregistrar exactamente el token final y evaluar más de un nombre/pares para evitar un resultado accidental. Cambia el formato/posición de supervisión, no la memoria: exige una autorización/experimento posterior, no una búsqueda automática.

No se reclama superioridad ni capacidad lingüística. La conclusión firme es negativa bajo estas dos distribuciones y presupuesto. Se conserva todo el histórico V1/V2 y este negativo. La investigación de Hielo lingüístico queda detenida hasta certificar un control neuronal de binding válido.
''')
if __name__=='__main__':print('Reports written from measured artifacts')
