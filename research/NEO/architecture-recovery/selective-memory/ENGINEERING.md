# Contratos y alcance

`network.py` reutiliza pesos iniciales y ecuaciones de b7d4b13; no modifica sus fuentes. Modelos ~0,28M, no8M/12M/50M. Histórico significa celda original bajo una visibilidad local experimental; no su anterior atención completa. Transformer de capacidad comparable mantiene sus dos bloques y pesos iniciales del control anterior.

El foreground usa máscara causal por bloques disjuntos de16tokens, reiniciada por documento. Ambas capas del Transformer obedecen la misma partición: no hay ruta multicapa hacia bloques antiguos. La implementación de atención conserva matrices densas64×64 en esta referencia CPU; aislamiento lógico no significa kernel local eficiente. No hay KVcache, estado global ni lectura del target. Solo Hielo declarado transporta información entre fragmentos. Se comprueba invariancia exacta de controles sin memoria ante perturbación fuera del bloque final y gradiente0 respecto a ACTIVACIONES de entrada anteriores.

EventFast/DeltaFast mantienen chunks de memoria8 y lectura desde estado previo; escritura solo llega a chunks posteriores. Histórico actualiza por token con su gate. Trapos puede recibir gradientes a través de bloques; se acredita conexión, no utilidad. Estados se crean por forward/documento y se resetean ante frontera/padding; no se certifica aún API de streaming externo.

Tests: referencia contra ecuaciones congeladas, causalidad train/eval, independencia batch/documentos, padding, gradientes finitos y cambios de todos los tensores entrenables en fixtures, cobertura AdamW única, equivalencia de trayectoria tras updates, pérdida y RNG/sampler/cursor del runner real. Dropout0,CPUFP32,threads1. Tolerancias logits atol2e-5/rtol2e-4; resume misma ruta CPU exacto. No certifica CUDA/BF16/AMP ni multiproceso.

## Fallos y correcciones preservados

- Primeros tests fallan por módulos aún ausentes; logs RED conservados.
- Generadorv1: recencia demasiado predictiva, rechazado antes de generalización.
- v2: nombre de retención no correspondía a su cadena de operaciones, detectado con caso literal; datos y microfit preservados.
- v3: devIID contenía familias nuevas, detectado por comprobación de pertenencia; v4 instancia familias train. Train no cambia.
- Evaluación aleatoria consumía RNG del entrenamiento. Test reproduce fallo, `fork_rng` restaura estado al evaluar; corregido antes de cualquier entrenamiento aleatorio.
- Test inicial del horizonte inspeccionaba peso de embedding atado: el gradiente del head no implica fuga de entrada. Se retiene la activación de entrada para medir la dependencia pertinente; no se cambió el forward. Log negativo conservado.

Los checkpoints derivan exclusivamente de inicializaciones desechables. `weights_only=True`, state_dict estricto; guardado atómico temporal→rename. Modelo/configuración/AdamW/RNGTorch/Python/sampler/cursor/updates/datasetSHA/sin scheduler/acumulación1 quedan registrados. Reanudar invocación no duplica updates ya completados; corte persistente cada100updates. Una interrupción pierde como máximo los updates posteriores al último corte, que se repiten desde ese estado, no se cuentan dos veces en el artefacto final.

- v4: reservar solo una respuesta por entidad hacía trivial la etiqueta composicional si se conocía la entidad. La prueba de balance condicional falló; se detuvo exclusivamente el runner experimental propio. Pilotos y checkpoints parciales quedan intactos en carpetas v4. v5 reserva dos respuestas por entidad; sus18tests previos al piloto pasaron. Sigue existiendo un prior condicionado a soporte (33,33%/50%) que se informa explícitamente.
- La regeneración exacta de los cinco splits no sellados v5 pasó, sin abrir el final. Los scripts `verify_panel.py` y `validate_results.py` distinguen integridad de datos, integridad de checkpoints y utilidad científica; una no acredita la otra.

Después de terminar los18entrenamientos primarios se corrigieron dos defectos de instrumentación/identidad, con tres fallos RED preservados: el wrapper histórico de trace pasaba un keyword que Variant no exponía; ahora llama la implementación base congelada. El presupuesto random no figuraba en config; ahora se registra solo en ese modo y se pasa explícitamente al runner. No cambia el forward normal entrenado. `network_trained_v5.py`/`learn_trained_v5.py` conservan exactamente los hashes previos; source-preservation.json los verifica.21tests pasaron antes de las ablaciones; después se añadieron controles de presencia y RNG común para contrafactuales random.

Para random, originales y twins usan RNG991 con batches de igual tamaño/posición, evitando confundir cambios de valor con nuevas máscaras aleatorias. Los controles no aleatorios conservan su ruta. La evaluación se aísla del RNG del entrenamiento y su reanudación real después de updates se comprueba también en el modo aleatorio. No se igualan sus diferentes políticas por declarar la misma media de coeficiente.

## Cierre ejecutado

24tests nuevos PASS (results/final-tests.log),19tests heredados del estudio de mecanismos y22de fundamentos PASS en sus logs conservados:65tests, CPU FP32 monoproceso. `source_equivalence.py` compara las seis condiciones normales actuales con el fuente congelado previo al entrenamiento: logits, gradientes y parámetros tras dos AdamW exactos PASS. No se extiende esa igualdad a algoritmos de memoria distintos ni a CUDA.

18checkpoints primarios y6de ablaciones cargan estrictamente; sus estados AdamW son finitos y alcanzan1000updates/cursor8000. Los órdenes de minibatches de las ablaciones coinciden con su brazo normal por semilla. La prueba del runner aleatorio verifica reanudación de RNG además de pesos/AdamW/cursor. Sin gradientes acumulados pendientes, AMP, scheduler ni múltiples workers en esta ruta.
