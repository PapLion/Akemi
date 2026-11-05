from run import *
r=read('short-comparison');pre=read('attention-before');post=read('attention-after');diag=read('diagnostics')
def write(n,s):(ROOT/n).write_text(s.strip()+'\n')
write('README.md','''# CryoCCM — Query Conditioning V1

Contraste ejecutado en CPU FP32, dos brazos de200updates, semilla17. Único cambio: mover los dos IDs de la entidad desde el medio al final de la consulta. Misma historia, multiconjunto de tokens, longitud, posición de predicción, target, inicialización, receta y orden. Sin Hielo ni Trapos; foreground y V3 intactos.

| Formato | Train respuesta/conjunta | Dev pares nuevos | Dev layout nuevo | Swaps estrictos dev |
|---|---|---|---|---|
| A: token final común |25% /0%|25% /0%|25% /0%|0/12|
| B: entidad final |25% /0%|12,5% /0%|25% /0%|0/12|

**La intervención cambia Q y atención, pero no enseña binding funcional. Compuerta FAIL; distancia larga NO EJECUTADA.** No semillas adicionales, no aumentos de capacidad ni updates. Se cierra esta familia de microfits y se detiene la investigación de Hielo lingüístico hasta disponer de un foreground con recuperación certificada.

Ver DECISION.md, QUERY_DIAGNOSTICS.md y COMPARISON.md. Datos, curvas, logits/Q/K reales, predicciones y checkpoints guardados en results/. Archivos .pt locales (no versionados) identificados en SHA256SUMS/ARTIFACT_MANIFEST.json. Código y pruebas reproducibles, no publicaciones ni merge automático.

Pruebas sin nuevos entrenamientos principales: usar el Python local de reproducibilidad para ejecutar query-conditioning/tests.py. Reproducción completa: bash query-conditioning/reproduce.sh en worktree nuevo con results vacío; se rechaza sobrescribir. El procedimiento respeta el gate y no ejecuta largo si B falla. No abrir el confirmatorio V2.
''')
write('DATA_CONTRACT.md','''# Contrato de datos

Reutilizamos las historias de binding-diagnostic/experiment.py sin modificarlo. Train: Nora/Iris, dos valores distintos entre cuatro colores, ambos órdenes, ambas preguntas:48respuestas/24historias. Dev pares: Nora/Mira; dev layout: Nora/Iris con holds/holding en vez de has/have.48respuestas por panel. Son plantillas experimentales EN, no lenguaje abierto ni evaluación ES. Luna se comprueba en tests de tokenización, no se añade al entrenamiento. Los dev son nuevos pares o reformulaciones, no nuevos valores (los cuatro se entrenan).

A conserva literalmente “What does Nora have? Answer:”. B permuta sus IDs y produce “What does have? Answer: Nora”. En layouts alternativos se aplica la MISMA permutación al nombre. No se corrige la gramática de B: es una intervención de orden, no una comparación de naturalidad. Los textos B vuelven a codificar exactamente los IDs permutados, sin byte injection ni modificación del tokenizer. Conservan11 tokens por consulta del panel principal, predicción en posición118, prefijo108 con11tokens de hechos al final, tras96tokens neutrales y BOS. El hecho queda cerca de la pregunta, no todos sus tokens quedan dentro de los últimos16 respecto a la respuesta.

A termina en ID58(:); B en1318(Nora),1544(Iris),2141(Mira),2184(Luna), todos distintos y verificados con V3 real. Las entidades son multitoken: se mueven las dos piezas, no solo el ID final. Se conservan los tokens de ambos nombres; los targets de color jamás aparecen en la pregunta. Los valores están únicamente en las historias.

Balance dataset:6ejemplos por entidad–valor,48targets. Cada paso usa batch8, mismo sampler V2. Exposición1600targets/brazo:800por entidad; valores402/400/399/399 (ciclo parcial, no balance exacto de valores consumidos). Exactamente iguales en A/B, explícitos en diagnostics.json. La primera/última escritura global resuelve50%; presencia sin valores25%. Ambos modelos terminan siguiendo un color constante en train (25%), no una asociación.

Cambios inevitables: posiciones internas de la entidad y sufijo, token desde el que se predice, sintaxis/orden de pregunta y relación posicional con hechos. La longitud total y posición del target no cambian. No se atribuye causalidad exclusiva a Q frente a toda la intervención de formato.
''')
write('QUERY_DIAGNOSTICS.md',f'''# Atención real: embeddings, Q, K y logits

Se extraen tensores del modelo real, no estados simulados. inspect_attention reconstruye Q/K con RoPE desde los pesos y comprueba el resultado de la atención manual frente al input real de o en scaled_dot_product_attention (atol2e-6,rtol1e-5, fijadas antes de ejecutar). Se guardan embedding final, Q final, K de hechos, atención normalizada, masa por hecho/cabeza y logits en attention-before.pt/attention-after.pt. JSON de todos los paneles conserva diagnósticos por historia, no solo ejemplo favorable.

| Medida pareja Nora/Iris misma historia |A inicial|B inicial|A final|B final|
|---|---:|---:|---:|---:|
| Delta máximo Q |{pre['A']['q_max_delta']:.6g}|{pre['B']['q_max_delta']:.6g}|{post['A']['q_max_delta']:.6g}|{post['B']['q_max_delta']:.6g}|
| Delta K hechos |0|0|0|0|
| Delta atención factual relativa |{pre['A']['relative_fact_attention_max_delta']:.6g}|{pre['B']['relative_fact_attention_max_delta']:.6g}|{post['A']['relative_fact_attention_max_delta']:.6g}|{post['B']['relative_fact_attention_max_delta']:.6g}|
| Delta logits |{pre['A']['logit_max_delta']:.6g}|{pre['B']['logit_max_delta']:.6g}|{post['A']['logit_max_delta']:.6g}|{post['B']['logit_max_delta']:.6g}|

Q distinta y atención distinta NO equivalen a recuperar correctamente un valor. B responde igual a ambas entidades entrenadas en24/24historias. En Nora/Mira da tokens diferentes según entidad pero0%conjunta: no demuestra binding, y CE sube9,53939. Es sensibilidad a identidad sin la relación correcta.

Orden real de operaciones: embedding → RMSNorm → Q/K/V por token → RoPE → atención causal → residual → MLP por token → dos refinamientos rápidos normalizados por token → slow_norm → LM head compartido con embedding. Hay UN bloque de atención; las operaciones posteriores no hacen otra atención entre posiciones. Al final B tiene identidad en Q, pero las K/V de un token de valor todavía no incorporan la entidad que lo precede. El Jacobiano de la K de un color respecto a embeddings de otros tokens es exactamente0 en ambos checkpoints (diagnóstico ejecutado). Esto caracteriza una restricción del mecanismo; no es prueba de incapacidad absoluta de mezclar información vía capas no lineales ni identifica una causa única del fallo.

Las consultas y hechos están causalmente antes del target. Las etiquetas no participan en el forward. La igualdad Q de A no impedía toda influencia de la consulta: había gradientes y pequeñas diferencias de logits. El experimento refuta que cambiar solo el token final sea suficiente bajo esta receta, no que el modelo nunca pueda aprender.
''')
rows=[]
for fmt in ['A','B']:
 for split,m in r[fmt].items():rows.append(f"|{fmt}|{split}|{m['entity_sides']['0']*100:.2f}%|{m['entity_sides']['1']*100:.2f}%|{m['joint']['accuracy']*100:.2f}%|{m['all']['nll_answer']:.6f}|{m['same_answer_stories']}/24|")
write('COMPARISON.md','''# A/B: respuesta normal sin decoder auxiliar

|Formato|Panel|Entidad A|Entidad B|Conjunta|CE respuesta|Respuesta idéntica|
|---|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

Argmax sobre8192IDs, no selección forzada entre colores. Una respuesta supervisada por secuencia; no teacher forcing de la respuesta. Checkpoint final200 fijado, sin selección por dev. En train ambos predicen exclusivamente5927(white). En dev pares B predice5927 para Nora y6101para Mira, sin resolver ambas asociaciones; cambiar predicción no basta. Exactitud de primer/último valor seguido25%train,12,5%dev pares B. Ambas órdenes factuales dan las mismas tasas; no hay éxito oculto en un solo orden.

A reproduce exactamente todos los pesos finales del control corto anterior40848ae, ver diagnostics.json. La identidad inicial A/B se certifica con hash real de pesos. Esto no garantiza resultados universales: una semilla y doscientas actualizaciones limitan el alcance.
''')
write('COUNTERFACTUALS.md','''# Intercambios de valores y consulta

Para cada combinación de dos colores diferentes hay historia A=x,B=y y su intercambio A=y,B=x, ambas órdenes.12pruebas estrictas por panel; cada una exige cuatro consultas correctas. Ambos formatos obtienen0/12 en train y en ambos dev. Las predicciones de las cuatro consultas están preservadas e identificadas por program_id/valores en datasets.json.

Cambio exclusivo de consulta:0/24historias con ambas respuestas correctas en todos los paneles. A produce respuesta idéntica en24/24; B también en train/layouts. En pares nuevos B produce respuestas distintas, pero ambas correctas en0/24. Esa diferencia de identidad es compatible con sobreajuste del último token y no prueba recuperación.

Los tests del oráculo comprueban que los valores son distintos, que el intercambio cambia necesariamente el target y que la pregunta no introduce la respuesta. No se utilizaron etiquetas para indexar memoria o seleccionar atención.
''')
write('ENGINEERING.md','''# Contratos y preservación

Antes de entrenar: tests de pares/multiconjuntos y balance, causalidad train/eval, independencia batch, alineación siguiente-token, gradientes de consulta/prefijo, parámetros/AdamW, etiqueta fuera del forward, checkpoint y reanudación exacta continua8updates contra3+5 en ambos formatos. Se compararon pesos, AdamW, RNG Torch/Python y cursor/orden. Ingeniería con fixtures de8updates, separada de los200updates por brazo.

Siete tests reproducibles adicionales PASS: tokenización de cuatro nombres, datos emparejados, atención real, checkpoint/optimizador, causalidad/labels, reanudación exacta y swaps oraculares. Las tolerancias se fijaron en código antes de ejecutar. No se trasladó certificado CUDA/BF16: soloCPUFP32 monoproceso.

Modelo/Block/tokenizer importados sin editar.13tensores activos; AdamW completa cobertura, gradientes finitos y parámetros cambian. Checkpoints guardan modelo, AdamW, RNG, dataset/cursor/orden, tokenizer y hash fuente, acumulación1 y schedulerNone. Su campo protocol es el heredado V2 del runner e incluye metadatos históricos; PROTOCOL.json de esta carpeta y cursor200 son la configuración efectiva del contraste, vinculados por manifest. No se confunden los campos400updates heredados con el entrenamiento ejecutado.

Una primera instrumentación de masa por hecho detectó una diferencia de segmentación BPE al tokenizar cada frase por separado (espacio fusionado con entidad siguiente). Ocurrió ANTES de todo entrenamiento principal. Se conservó el fallo en results/diagnostic-attempt-0/, se corrigió únicamente el corte de spans del diagnóstico sobre los IDs reales y se comprobó la reconstrucción contra atención real. No se cambiaron datos, modelo, umbrales ni entrenamiento para ocultar un resultado. El preflight de ingeniería se repitió; no se repitieron entrenamientos principales.

Sin Hielo entrenado, sin Trapos, GPU, servicios pagados, Chinchilla ni acceso al confirmatorio sellado. Los resultados anteriores y fuentes permanecen intactos. SHA256SUMS cubre código, configuración, resultados y checkpoints locales; no se lee ningún cuerpo sellado.
''')
a=read('short-A-17');b=read('short-B-17')
write('PERFORMANCE.md',f'''# Coste CPU del contraste

|Formato|Tiempo200updates|Respuestas/s|IDs entrada/s|RSS pico proceso MiB|
|---|---:|---:|---:|---:|
|A|{a['seconds_train']:.4f}|{a['responses_s']:.2f}|{a['input_ids_s']:.2f}|{a['peak_process_rss_mib']:.2f}|
|B|{b['seconds_train']:.4f}|{b['responses_s']:.2f}|{b['input_ids_s']:.2f}|{b['peak_process_rss_mib']:.2f}|

284096parámetros asignados,280736entrenables; idénticos en A/B.1600respuestas/brazo,48ejemplos únicos (33ciclos completos y fracción). RAM es máximo acumulado de proceso, no asignación aislada. Medidas sin profiler, sin CUDA; no extrapolación GPU ni FLOPs medidos. Los snapshots de atención se toman fuera de entrenamiento. No hay evidencia de mejora de eficiencia, y no es el objetivo del contraste.
''')
write('DECISION.md','''# Decisión cerrada: no se certifica Query Conditioning V1

1. Sí: entidad al final modifica embeddings/Q.2. Sí: modifica preferencia relativa de atención hacia hechos.3. No aprende a distinguir asociaciones: ambas entidades entrenadas reciben el mismo color,25%respuesta y0%conjunta.4. No se observan bindings correctos:0/12swaps, comportamiento constante en train.5. No generaliza: nuevo par12,5%,conjunta0%; layoutnuevo25%,conjunta0%.6. Distancia larga NO EJECUTADA: la compuerta corta falló; su dificultad independiente sigue sin aislarse.7. No está justificado reanudar Hielo lingüístico.

La hipótesis de que bastaba dar identidad al token final queda refutada como solución suficiente bajo esta receta. No se refuta una contribución parcial de ese formato: Q/atención sí cambian, pero no hay beneficio funcional. No se demuestra incapacidad absoluta del modelo. Las condiciones son un foreground diminuto de un bloque, doscientos updates, una semilla y plantillas EN.

Cerramos explícitamente esta familia de microfits: no más permutaciones, seeds, updates o cambios de tokenizer en respuesta al fallo. No se rediseña memoria, Trapos o atención en esta fase. El problema se traslada a capacidad y aprendizaje del foreground lingüístico. La siguiente línea, si se autoriza, debe verificar representaciones contextuales que vinculen entidad con valor ANTES de la lectura y una receta de aprendizaje básica estable; el panel y controles negativos quedan congelados como regresión. La observación concreta que lo motiva es que las K/V del color en la única atención dependen del token y posición, sin codificar todavía su entidad vecina; dar identidad a Q no resuelve por sí mismo esa asociación. Eso no elige automáticamente más capas ni una nueva arquitectura ni demuestra una causa exclusiva frente a optimización.

No se inicia otro entrenamiento ni se promueve un formato como Language Bridge certificado. Hielo direccionable simbólico y todo su histórico se conservan. La memoria lingüística permanece bloqueada por ausencia de control neuronal positivo.
''')
print('Reports written from executed results')
