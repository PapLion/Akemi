from setup import *
r=read('micro-full-17');d=read('diagnosis');pc=read('positive-controls');fm=read('final-metrics');manifest=read('data-manifest');seal=read('confirmatory-artifact')
def write(name,text):(OUT/(name+'.md')).write_text(text.strip()+'\n')
write('README',f'''# Language Memory Bridge V2 — ejecución cerrada por compuerta

Rama `cryo-language-memory-v2`, origen `485f552`. Trapos OFF. Hielo, Delta, reader, foreground y NeoTokenV3 sin cambios. Implementación importada directamente desde language-bridge/model.py, sin copia modificada.

**No se demuestra ni se refuta recuperación lingüística de Hielo. Falló antes el control positivo de contexto completo.**

| Ejecución | Estado | Resultado |
|---|---|---|
| Contratos del entrenador | PASS |7 pruebas CPU |
| Contratos de estados/intervenciones | PASS |5 pruebas CPU |
| Memoria exacta oracular | PASS diagnóstico |100% en los paneles generados |
| Reader lineal sobre valor explícito | PASS diagnóstico |100%,100updates,20parámetros |
| Microfit de foreground con contexto completo | FAIL |200updates;16/32 respuestas,3/16 relatos con ambas correctas; CE1.04552 |
| Contraste principal A/B/C400updates | NO EJECUTADO |Bloqueado por el microfit preregistrado |
| Semillas29/43 | NO EJECUTADAS |No se habilitaron |
| Confirmatorio nuevo | SELLADO |{seal['examples']} ejemplos, nunca evaluados |

Datos controlados:2048 ejemplos train,1024 dev combinaciones y2048 dev estructuras; dos consultas por programa, todos sintéticos de código, no lenguaje natural abierto. Una respuesta = un token real V3; la exactitud usa argmax de8192 IDs, no selección forzada entre colores. La pérdida es exclusivamente de respuesta, no pretraining ni SFT general.

Guardar el negativo es parte del protocolo. No aumentar automáticamente updates, dimensiones ni modificar Hielo/Trapos/tokenizer. Ver DECISION.md. No GPU, Vast.ai, Chinchilla ni evaluaciones selladas históricas. Código, curvas, predicciones y controles en esta carpeta; .pt locales y datos grandes se conservan fuera de git, con hashes.

## Reproducir

Solo contratos (sin entrenamiento principal; los tests incluyen updates diminutos de ingeniería):
```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python memory-bridge/intervention_tests.py
```
Las7 pruebas conservan engineering.json y verifican su identidad al repetir; para reproducir todo, usar salida NUEVA:
```bash
bash memory-bridge/reproduce.sh /PATH/TO/NEO_HOME/research/neo-architecture-recovery/language-memory-reproduction-NEW
```
Rechaza directorios existentes. Reutiliza Python3.11/Torch y el backend V3 local; sin instalaciones ni descargas. El código respeta la compuerta del microfit, nunca fuerza el contraste principal. La auditoría V1 requiere el checkpoint local `../cryo-language-bridge-v1/language-bridge/results/ice-final.pt`; no se modifica.

SHA256SUMS verifica resultados/código/datos locales excepto el cuerpo sellado; su hash se produjo durante la escritura sin releer contenido. ARTIFACT_MANIFEST.json registra identidad y localización. La receta/cuerpo confirmatorio no deben utilizarse para ajustar la siguiente intervención.
''')
write('DATA_PROTOCOL','''# Datos y objetivo congelados

protocol.json se fijó antes del microfit: CPU FP32, semilla17, batch8, AdamW(.003, betas .9/.95, weight_decay .01), clipping1, modelo width32/chunk16.400updates por brazo principal como máximo;200updates de microfit independiente, sin reutilizar sus pesos en brazos principales. Selección de checkpoint: último paso fijo, sin elección por dev.

Los programas se generan por producto cartesiano de dos entidades, cuatro valores independientes, dos idiomas, ambos órdenes, condición inicial/corrección y tres transiciones no idénticas. Se consulta a ambas entidades; la corrección afecta una y la otra debe conservarse. Ninguna etiqueta, nombre de entidad oracular o valor esperado se pasa como índice al modelo: recibe exclusivamente tokens de hechos, distractores y pregunta. Los nombres son texto normal tokenizado por V3.

- Train: pares Nora–Iris y Mira–Luna, redacción0, distancias96/128;2048respuestas/1024programas.
- Dev combinaciones: Nora–Mira e Iris–Luna, redacción0, distancia96;1024respuestas/512programas.
- Dev estructuras: pares de train, redacciones1/2 y distancia160;2048respuestas/1024programas. Aquí cambian conjuntamente redacción y distancia: no atribuir un efecto exclusivamente a una.
- Microfit separado: Nora–Iris, EN,16pares de valores y ambas consultas, sin corrección,32respuestas. Su cometido es memorizar la tarea antes de estudiar generalización. No es un dev independiente.
- Confirmatorio: pares reservados Nora–Luna e Iris–Mira, redacciones1/2, distancia192,1024ejemplos. Cuerpo escrito en sealed/CONFIRMATORY.jsonl con permisos0400 y hash calculado al escribir; no se cargó ni evaluó. La receta usa enumeración cartesiana, sin muestreo RNG; el número de semilla reservado en metadatos no se utilizó para generación.

Cada respuesta es una palabra de un token: EN red/white/black/gold; ES rojo/azul/verde/negro. Son etiquetas lingüísticas distintas por idioma, no traducción uno a uno. Igual presupuesto de respuestas y targets elimina confusión de longitud de respuesta. Se conserva la palabra completa, sin recodificar a IDs DSL ni limitar el vocabulario de salida.

Se comprueba balance exacto de cuatro respuestas condicionado por pregunta/entidad/idioma; tablas desde los targets reales en data-manifest.json. Todos los pares valor–valor están presentes; queries de train/dev son disjuntas por programa/pares/layout. Los hechos completos preceden al menos16tokens neutrales; se añaden frases neutrales completas y padding byte-espacio hasta frontera96/128/160, nunca se recorta un hecho ni un documento externo. Es una conveniencia de ingeniería declarada, no extracción de acontecimientos semánticos.

El distractor es contenido neutro más la asociación de otra entidad; no se cubre todavía una tercera entidad adversarial ni lenguaje libre. Textos sintéticos compuestos durante esta sesión por el generador, procedencia en código/hashes. Ninguna fuente externa, documento privado, Chinchilla ni evaluación histórica. Datos de borrador previos al freeze de entrenamiento quedan preservados en results/draft-v0, excluidos de los resultados y de git. No se ajustó ningún dato después de observar el microfit.
''')
write('POSITIVE_CONTROLS',f'''# Realizabilidad y precondición fallida

Oráculo exacto de memoria por entidad:100% en train/dev/micro. Se verifican etiquetas mediante recorrido causal del diccionario y una segunda implementación de búsqueda inversa por entidad. Es selección asistida por el oráculo, no un logro de CryoCCM.

Reader lineal20parámetros sobre el valor explícito one-hot:100% tras100updates, CE {pc['results']['explicit_linear_reader']['ce_initial']:.4f}→{pc['results']['explicit_linear_reader']['ce_final']:.4f}. Diagnóstico de realizabilidad, no usa Hielo aprendido ni se incluye entre parámetros de los brazos.

Control sin valores: el mejor prior de clase condicionado por consulta/entidad/idioma llega exactamente25% tanto en train como micro. Heurística primer valor global:43.75%train/62.5%micro; último valor global62.5%. Recuperación por última escritura DE LA ENTIDAD logra100% porque implementa el oráculo. El panel exige binding, no mera recencia global. Un porcentaje superior a25% no basta para demostrarlo.

Control con contexto completo: mismo foreground/refinamiento rápido del brazo local sin Hielo; se llama al chunk_hidden original sobre toda la secuencia causal. La única diferencia respecto a A es visibilidad/posiciones de atención; no se usa la variante Transformer sin refinamiento de V1. Modelo pequeño nuevo desde semilla17, no warmstart lingüístico. Los tests comprueban que la pérdida tiene gradiente hasta el hecho visible.

Compuerta microfit congelada: exactitud≥95% y CE<.3 tras200updates sobre32ejemplos. Resultado50%, CE1.04552; ambas consultas correctas18.75%. La curva baja desde una CE cercana a9 y aprende los cuatro tokens de respuesta, pero no la recuperación por entidad. Fallan ambos requisitos sin cambiar umbrales ni extender presupuesto.

El fallo es de esta configuración/receta, no prueba de incapacidad del Transformer ni de Hielo. El oráculo resuelve los datos, pero no sustituye la precondición de aprendizaje del control neuronal. Por esa razón no se entrenaron A/B/C ni semillas adicionales.
''')
write('TRAINER_CONTRACTS','''# Contratos ejecutados

7 tests CPU en release-tests.log: oráculo/balance/separación; paridad de head selectiva con forward V1; ausencia de acceso al prefijo en no-Hielo; causalidad train/eval y sesiones; gradientes hasta H real y proyecciones; etiquetas no entran al forward; AdamW y reanudación.

5 tests CPU en intervention-tests.log: estado previo a consulta equivale al forward directo; sin escritura conserva cero; lectura desactivada en consulta elimina dependencia de H; reset en el microfixture de consulta≤16tokens; donantes compatibles y acceso al prefijo del control completo. No se ajustaron tolerancias: paridad atol2e-6/rtol1e-5, causalidad atol1e-6.

La entrada siempre es prefijo+pregunta. Se toma el hidden del ÚLTIMO token observado y se proyecta al vocabulario ligado; CE se calcula contra el token siguiente de respuesta. El answer nunca se concatena al input de entrenamiento. Cambiar targets sin cambiar input no altera logits. No hay teacher forcing de respuestas anteriores, decoder auxiliar ni máscara de cuatro candidatos; todos8192 IDs compiten.

Head selectiva evita crear logits de texto no supervisado, pero sus valores coinciden con el forward original. Se agrupan ejemplos en batch y se ejecuta el chunk_hidden original, sin editar módulos/ecuaciones. Padding al final no afecta consultas anteriores por máscara causal; se selecciona la posición válida de cada ejemplo. Cada fila empieza con H cero; memoria se mantiene con gradientes a través de todos los chunks del mismo ejemplo, sin truncar el hecho de la pregunta. No mezcla de sesiones.

AdamW incluye exactamente los parámetros requires_grad sin duplicados; todos reciben gradientes finitos y cambian en ingeniería. Sin Hielo/con contexto completo se congelan deliberadamente las proyecciones de memoria; reader/backbone/Delta originales no se reconstruyen después de AdamW.

Reanudación:8updates continuos vs3+guardar/restaurar+5 para tres rutas, igualdad exacta de pesos, estados/contadores AdamW y RNG Torch/Python. Guarda cursor_updates/cursor_samples, orden, seed, datasetSHA, tokenizerFP, config/protocolo, SHA del modelo, microsteps, acumulación1 y schedulerNone. Carga torch.load(weights_only=True). Sin AMP, multiprocessing, acumulación parcial o CUDA.

El protocolo400updates permanece implementado pero bloqueado. El checkpoint real conservado es micro-full-17.pt,200updates y1600respuestas. Se conserva engineering.json anterior al entrenamiento y logs de verificación adicionales; no se reetiquetan intervenciones sobre V1 como certificación de un B V2 entrenado.
''')
write('MEMORY_RESULTS',f'''# Resultados y alcance

| Modelo/condición | Respuesta exacta | Ambas asociaciones | Estado |
|---|---:|---:|---|
| Control oracular explícito |100%|100%|Diagnóstico asistido |
| Foreground completo, microfit train |50% (16/32)|18.75% (3/16)|200updates, FAIL |
| Foreground local A, principal |—|—|NO EJECUTADO |
| Hielo B, principal |—|—|NO EJECUTADO |
| Foreground completo C, principal |—|—|NO EJECUTADO |
| Semillas29/43 |—|—|NO EJECUTADAS |

No existen resultados V2 sobre dev de combinaciones, reformulaciones, corrección o conservación porque la precondición falló. Los datos se generaron y sus oráculos se verificaron, pero no se midieron esos resultados con nuevos modelos entrenados. No presentar el techo analítico25% de A como una exactitud medida.

En el microfit,16/16historias reciben la misma predicción para ambas entidades, incluso cuando sus valores difieren. Los cuatro tokens de respuesta son válidos, pero no se siguen relaciones consulta–entidad–valor. Confusión por clase y predicciones completas en final-metrics.json y micro-full-17-train-predictions.json. Los32ejemplos no son32unidades independientes: hay16programas y una semilla.

Inferencia sin reentrenar, quitando distractores del mismo checkpoint:25% respuesta,6.25% conjunta. Cambian conjuntamente posiciones/distancia, de modo que no aísla causalmente la longitud y no prueba un fallo de capacidad representacional. No se usa para modificar receta.

NLL sobre prefijo+pregunta+respuesta del microfixture: {fm['text_nll_micro']['nll']:.5f}, PPL {fm['text_nll_micro']['ppl']:.1f} sobre{fm['text_nll_micro']['targets']}targets. El entrenamiento optimizó solo respuesta, cuya CEfinal1.04552 es una métrica distinta. No hay medición de lenguaje real externo en esta fase ni una afirmación de mejor capacidad lingüística.

La prueba central sobre Hielo sigue SIN RESOLVER. El cuello de botella observado primero está en aprender recuperación condicionada por consulta bajo esta configuración, incluso cuando el control ve los hechos. No se puede adjudicar el fracaso a escritura/retención/reader de Hielo porque el brazo B no se habilitó.
''')
write('COUNTERFACTUALS','''# Contrafactuales y conservación

El microfit contiene todas16combinaciones de valores para dos entidades; el swap de valores conserva entidades, pregunta y formato. Evaluación estricta del checkpoint de contexto completo sobre seis pares no ordenados de valores distintos: **0/6** exige que sean correctas ambas consultas antes y después del intercambio. Son seis comparaciones relacionadas de un fixture de entrenamiento, no evidencia estadística independiente.

Predicciones y respuestas por consulta en final-metrics.json. El modelo da la misma respuesta a ambas preguntas de cada relato y no supera la prueba fuerte. Variar un valor puede cambiar logits/predicción, pero eso no basta para demostrar que sigue el binding correcto.

Correcciones, invariancia al valor obsoleto, conservación de la otra entidad y contrafactuales V2 de Hielo: NO EJECUTADOS como evaluación de un modelo entrenado V2, por fallo del control previo. Los programas y etiquetas sí están preparados y certificados, sin enseñar eventos futuros. No se abrieron confirmatorios.

La auditoría mecánica sobre el checkpoint V1 usa estados donantes de secuencias reales con el mismo par/consulta/layout/distancia y valor vigente distinto. Se mide explícitamente seguimiento del valor donante; en ocho casos mecánicos la respuesta correcta y seguimiento son0%, predicción newline. Esto no es un resultado de entrenamiento V2 ni una estimación general del checkpoint. Se conserva como evidencia de que intervenciones sobre estados reales están conectadas, no como prueba de memoria útil.
''')
write('CAUSAL_ABLATIONS',f'''# Auditoría de rutas y estados

Diagnóstico previo: V1 no entrenó preguntas/respuestas de recuperación distante; sus historias de exposición no constituían señal para contestarlas. Las evaluaciones eran posteriores. V2 implementa esa señal, pero queda detenido antes de B por la compuerta positiva.

La ruta conserva estados reales H8×32 entre chunks. Un checkpoint V1 inmutable se cargó y se extrajeron estados al terminar cada chunk; volver a consultar desde el estado previo coincide con el forward completo. Los snapshots están en v1-state-audit.pt, con SHA del checkpoint fuente, tokens de ejemplo y fingerprint V3.

Gradiente real de CE de respuesta sobre ese checkpoint: primer H={d['v1_answer_gradients']['first_memory_norm']:.6g}; event_value={d['v1_answer_gradients']['write_value_norm']:.6g}; address={d['v1_answer_gradients']['address_norm']:.6g}; read={d['v1_answer_gradients']['reader_norm']:.6g}. Llegar con gradiente no demuestra una política aprendida ni buen horizonte de aprendizaje.

Intervenciones implementadas fuera del módulo original:
- Normal: H obtenido causalmente del prefijo.
- Reset: cero justo ANTES de procesar la pregunta, no después de producir la respuesta.
- Swap: H de un prefijo donante real y compatible; se comprueba si la salida sigue su valor.
- Sin escritura: H empieza en cero y no se actualiza en prefijo ni pregunta.
- Sin lectura: mantiene H del prefijo pero anula la salida de read durante la consulta; se etiqueta como ablación de lectura en consulta, no intervención global de entrenamiento.

En los ocho fixtures mecánicos V1, reset/sin escritura/sin lectura alteran logits hasta0.01076; swap hasta2.86e-6. Todos mantienen el token newline,0% de respuesta y de seguimiento del donante. No es una ventaja funcional y no sirve para inferir aprendizaje de B.

Las claves siguen siendo de token, no de entidad semántica. La pregunta termina en el mismo token, y las fronteras suelen terminar en espacio: compartir un token de dirección puede limitar el direccionamiento, pero los estados y el foreground contienen otras dependencias; este diagnóstico no prueba una incapacidad ni una causa única. No se cambia el reader para corregirlo sin un contraste posterior.

Ausencia de atajos: hechos fuera de ventana16 al consultar, estado local sin-Hielo independiente del prefijo, clases balanceadas por pregunta; el control completo conserva explícitamente más información y no cuenta como igualdad computacional. No hay KV cache, labels oraculares ni historial oculto.
''')
write('PERFORMANCE',f'''# Rendimiento observado CPU

Única trayectoria neuronal lingüística entrenada: microfit de contexto completo, semilla17,200updates×batch8=1600respuestas supervisadas. Parámetros activos {r['parameters_active']:,}, asignados {r['parameters_allocated']:,}. Inicialización nueva y emparejable; los pesos del microfit se descartan para cualquier contraste principal.

Entrenamiento: {r['seconds_train']:.4f}s, {r['responses_s']:.2f}respuestas-target/s y {r['input_ids_s']:.2f}IDs de entrada/s. Medición de CPU de un hilo, head solo en posiciones supervisadas. Los32ejemplos del microfit se exponen50veces cada uno;1600targets consumidos no son1600ejemplos distintos. No confundir IDs de entrada con targets de pérdida. Cold start, construcción de datos, diagnósticos, evaluación y escritura de checkpoint quedan fuera de ese tiempo; tiempos por update/gradiente en micro-full-17.json. RSS high-water del proceso {r['peak_process_rss_mib']:.2f}MiB, no memoria exclusiva del modelo.

Reader explícito diagnóstico:20parámetros/100updates, independiente y no sumado a throughput del LM. Pruebas de ingeniería incluyen8updates para tres rutas, no aprendizajes comparativos. No se midió throughput de B V2 ni speedup de Hielo; los valores de V1 no se transfieren a esta receta answer-only.

Atención completa cuesta O(L²) frente a chunks16 de A/B, además de permitir acceso a más información. Todos los módulos provienen del mismo modelo; A/C tienen280736parámetros activos y B284096, con3360parámetros adicionales de memoria. No se midieron FLOPs completos y no se afirma igualdad de cómputo. No GPU, AMP, servicios pagos ni proyecciones de entrenamiento grande.
''')
write('DECISION','''# Decisión cerrada

**Resultado: inconcluso sobre memoria lingüística de Hielo; fallo de la precondición neuronal de recuperación.** Clasificación A del protocolo: el foreground de contexto completo no aprende suficientemente la tarea elemental bajo el presupuesto fijado. No es un resultado negativo de Hielo entrenado: ese entrenamiento no llegó a ejecutarse.

Hechos demostrados:
1. Los datos y el control explícito permiten recuperar exactamente los valores; priors de pregunta/presencia solo25%.
2. La pérdida siguiente-token recibe el prefijo correcto, sin answer en el forward, con gradientes finitos y parámetros actualizados. Full-context tiene acceso efectivo al hecho; no está ejecutándose accidentalmente con ventana16.
3. El microfit completo llega a50% respuesta y18.75% conjunta, CE1.04552; responde igual a ambas entidades en16/16historias y falla0/6 swaps estrictos. No certifica recuperación por entidad.
4. Los estados de Hielo V1 persisten, la lectura está conectada y las intervenciones afectan logits, pero eso no demuestra utilidad funcional ni entrenamiento V2.
5. Se respeta el fallo prospectivo: sin brazos400, sin confirmaciones29/43, sin retocar umbrales, LR, capacidad, tokenizer o arquitectura.

No hay base para concluir «Hielo no puede guardar lenguaje» ni «el único fallo está en Delta/Trapos/reader». El bloqueo observable actual es la adquisición de la asociación pregunta–entidad–valor en la receta de entrenamiento/foreground completo. No se aislaron capacidad, optimización y dependencia posicional como causas excluyentes. El fallo al acortar el contexto sin reentrenar tampoco las distingue.

Siguiente contraste mínimo, pendiente de decisión explícita: certificar un control de recuperación con contexto corto y la MISMA arquitectura/receta y respuestas balanceadas, frente al contexto completo de distancia96, manteniendo un presupuesto fijado antes de ejecutar. Solo debe cambiar la distribución/distancia, sin nuevas memorias ni tokenizador. Si ese control no aprende, localizar condicionamiento por consulta/representación y señal de aprendizaje antes de entrenar Hielo; si aprende, recién estudiar distancia y transporte con un control positivo válido. No se ejecuta automáticamente aquí.

Se conserva Addressable V1.2, Trapos congelado y todos los negativos. No se autoriza pretraining, GPU ni transición a lenguaje abierto. El conjunto confirmatorio nuevo permanece sellado. La infraestructura V2 está implementada, los contratos pasan y la pregunta central permanece abierta por una compuerta real, no por falta de ejecución del piloto.
''')
if __name__=='__main__':print('Evidence-based reports written')
