# Extracción real de estados

Pesos de198b681 referidos desde el worktree original, cargados `weights_only=True`, `strict=True`; nunca se sobrescriben. Nueve checkpoints normales: histórico/EventFast/DeltaFast×17/29/43, junto con sus inicializaciones recreadas con la semilla/configuración exacta. Seis checkpoints Delta de escritura permanente/aleatoria sirven como controles adicionales; no se repiten sus entrenamientos.

`extract.observe` utiliza el forward congelado y su trace. Histórico: vector slow32 y gates por token, fast/candidate de la escritura. Event: slots reales aplanados; Delta: matriz asociativa real8×32. Wrappers temporales de `_summarize`/`_read` y hook de `read` observan los mismos tensores, luego se retiran incluso ante excepción. No se sustituyen estados por códigos simulados. `results/*-trained.pt` y `*-initial.pt` contienen estados tras cada8IDs, gates, características de escritura, lectura final, hidden local y predicción original sobre8192clases.

Las etapas detalladas se alinean con los instantes de escritura reales de cada implementación. `timelines.json` conserva, para24programas de corrección múltiple y semilla17, todos los estados antes/después y gates de64pasos históricos u8fragmentos híbridos. Antes de la primera escritura es el memory_init real/estado inicial de la trayectoria, no un ejemplo artificial. Los híbridos no tienen una escritura independiente por cada registro dentro del fragmento: «antes/después de corregir» se interpreta en esas fronteras y no se inventan estados intermedios.

Probe principal: estado después del token55 y antes del fragmento final56–63. La última atención local ve48–63 y es idéntica al variar valores. El estado puede legítimamente incorporar tokens hasta55; no se incorpora respuesta ni target. La lectura observada en63 puede usar los tokens de consulta, que son idénticos en los pares. Para histórico la lectura del paso final y el estado anterior a56 son etapas diferentes; se informa así.

Tests verifican igualdad exacta de predicción con/sin observación, invariancia de estados hasta47 al modificar48–63, pesos sin gradientes y sham de intervención. No se extiende esto a CUDA/AMP. La causalidad/resets del forward proviene además de los tests heredados; aquí no se repite D1 ni se abre ninguna evaluación sellada.

Campo `candidate` en los archivos de híbridos conserva un alias de la característica resumida; **no debe interpretarse como la proyección candidata**. El análisis `write_value` llama explícitamente al módulo congelado candidate/value sobre esas características y registra sus propias métricas. En histórico ese campo sí contiene el candidato real de la celda.

## Verificación ejecutada

Nueve tests CPU PASS en `results/tests.log`, incluidos controles de balance/oráculos, foreground constante, disjunción, extracción normal/always/random con RNG controlado, causalidad de estados, sham, decoder explícito/negativo y persistencia del readout.24artefactos de características corresponden a15checkpoints entrenados únicos más9inicializaciones. SHA-256 de todos los checkpoints usados se comprueba al cerrar y los tensores extraídos son finitos.

Los readouts lineales del suplemento se guardan con estado, normalizador train, dimensiones y configuración en `results/readouts/*.pt`, recargables con weights_only/strict y test de reproducción de predicción. Los primeros probes conservan curvas/predicciones y se reproducen mediante el ajuste determinista; no se afirma que sus pesos estén todos serializados.

Un fallo de importación fue detectado en tests: colisión con `mechanism-study/probes.py`. Se conserva `results/import-collision-red.log`; el módulo nuevo se llama `value_probes.py`, con wrapper CLI `probes.py`. No se modificó la ecuación del decoder ni se ocultó el error. El guardado opcional y la reanudación idempotente de extracción no cambian la matemática medida.
