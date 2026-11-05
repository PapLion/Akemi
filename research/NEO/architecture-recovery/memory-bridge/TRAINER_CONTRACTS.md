# Contratos ejecutados

7 tests CPU en release-tests.log: oráculo/balance/separación; paridad de head selectiva con forward V1; ausencia de acceso al prefijo en no-Hielo; causalidad train/eval y sesiones; gradientes hasta H real y proyecciones; etiquetas no entran al forward; AdamW y reanudación.

5 tests CPU en intervention-tests.log: estado previo a consulta equivale al forward directo; sin escritura conserva cero; lectura desactivada en consulta elimina dependencia de H; reset en el microfixture de consulta≤16tokens; donantes compatibles y acceso al prefijo del control completo. No se ajustaron tolerancias: paridad atol2e-6/rtol1e-5, causalidad atol1e-6.

La entrada siempre es prefijo+pregunta. Se toma el hidden del ÚLTIMO token observado y se proyecta al vocabulario ligado; CE se calcula contra el token siguiente de respuesta. El answer nunca se concatena al input de entrenamiento. Cambiar targets sin cambiar input no altera logits. No hay teacher forcing de respuestas anteriores, decoder auxiliar ni máscara de cuatro candidatos; todos8192 IDs compiten.

Head selectiva evita crear logits de texto no supervisado, pero sus valores coinciden con el forward original. Se agrupan ejemplos en batch y se ejecuta el chunk_hidden original, sin editar módulos/ecuaciones. Padding al final no afecta consultas anteriores por máscara causal; se selecciona la posición válida de cada ejemplo. Cada fila empieza con H cero; memoria se mantiene con gradientes a través de todos los chunks del mismo ejemplo, sin truncar el hecho de la pregunta. No mezcla de sesiones.

AdamW incluye exactamente los parámetros requires_grad sin duplicados; todos reciben gradientes finitos y cambian en ingeniería. Sin Hielo/con contexto completo se congelan deliberadamente las proyecciones de memoria; reader/backbone/Delta originales no se reconstruyen después de AdamW.

Reanudación:8updates continuos vs3+guardar/restaurar+5 para tres rutas, igualdad exacta de pesos, estados/contadores AdamW y RNG Torch/Python. Guarda cursor_updates/cursor_samples, orden, seed, datasetSHA, tokenizerFP, config/protocolo, SHA del modelo, microsteps, acumulación1 y schedulerNone. Carga torch.load(weights_only=True). Sin AMP, multiprocessing, acumulación parcial o CUDA.

El protocolo400updates permanece implementado pero bloqueado. El checkpoint real conservado es micro-full-17.pt,200updates y1600respuestas. Se conserva engineering.json anterior al entrenamiento y logs de verificación adicionales; no se reetiquetan intervenciones sobre V1 como certificación de un B V2 entrenado.
