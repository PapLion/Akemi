# CryoCCM: memoria selectiva sin atajos

Experimento CPU aislado sobre b7d4b13, rama `cryo-selective-memory-v1`. No se modifica CryoTiny histórico, EventFast/DeltaFast anteriores, A4, NeoTokenV3 ni Chinchilla. Se usa la celda histórica con una **nueva condición de atención local explícita**; no se equipara a su anterior resultado de atención completa.

La pregunta es si Trapos/Hielo puede conservar y corregir hechos fuera del foreground. Exactitud global, gates no nulos o sensibilidad a Hielo no bastan. Las pruebas centrales son contrafactuales del dato obsoleto/vigente, controles sin memoria con acceso local idéntico y ablaciones desde entrenamiento.

## Artefactos y recorrido

- [Tareas y splits](TASKS_AND_SPLITS.md): máquina de estados simbólica, dos oráculos, gramática, visibilidad y limitaciones.
- [Protocolo y cronología](PROTOCOL.md): decisiones previas y versiones rechazadas; no se ocultan fallos de diseño.
- `data-v5/`:480train,240IID,160composición,240estructural,160ambos. Nuevo final400 sellado localmente y nunca usado para seleccionar modelos.
- [Contratos de ingeniería](ENGINEERING.md): causalidad train/eval, exclusión de prefijo en controles locales, resets, gradientes, AdamW y resume.
- `results/pilot/`:seis brazos,seed17,300updates; `results/extend/`:cortes prefijados1000updates,semillas17/29/43. Seis condiciones: histórico/noHielo/Transformer/EventFast/DeltaFast locales y Transformer completo como referencia de mayor acceso.
- `results/*-predictions.jsonl`, checkpoints locales ignorados por Git, curvas y todas las pérdidas por update. Las versiones exploratorias rechazadas siguen en carpetas separadas.
- [Reproducción](REPRODUCIBILITY.md): comandos, identidad de fuentes/datos y reanudación sin duplicar trayectorias.

La entrada usa IDs ASCII atómicos dentro de8192salidas; es un fixture para mecanismos, no texto BPE ni una demostración lingüística. Cada update supervisa8respuestas;64IDs de entrada por ejemplo no equivalen a64targets entrenados. La evaluación final sellada y cualquier confirmación con semillas nuevas quedan fuera de esta campaña exploratoria.

Los resultados y la decisión se cierran después de completar las ejecuciones y verificar sus artefactos; no se promueve una arquitectura por pasar contratos funcionales.

## Cierre medido

[Decisión](DECISION.md): **memoria funcional, selección/corrección de valores no demostrada**. Se completaron18trayectorias primarias y6ablaciones de escritura (tres semillas,1000updates cada una). El control de presencia que nunca lee valores logra53,33% fuera de ventana; Delta50,28% IID/52,50% estructural. La exactitud agregada permite atajos.

La prueba crítica de42correcciones genuinas exige acierto original, invariancia al valor obsoleto y respuesta correcta al cambiar el vigente: **0/42 en cada modelo primario**, incluyendo24casos con valores dentro del soporte train. [VALUE_BINDING.md](VALUE_BINDING.md) separa este resultado del diagnóstico mixto que incluía borrado→escritura. Los ceros y versiones rechazadas se conservan.

Véanse [ablaciones](ABLATIONS.md), [compuertas](EXECUTION_GATES.md), [coste CPU](CPU_PERFORMANCE.md), [filtro/gradientes](GRADIENTS_AND_FILTER.md), [muestras completas](SAMPLES.md) y [siguiente diagnóstico mínimo](NEXT_EXPERIMENT.md). No hay promoción de arquitectura ni evaluación lingüística; el final continúa sellado.

Certificación de ingeniería:24tests nuevos+19heredados de mecanismos+22fundamentales=65PASS CPU. Los24checkpoints finales se verifican estrictamente, con AdamW finito/cursor/orden, y las seis rutas normales coinciden con sus fuentes congelados en logits, gradientes y dos updates. Inventario de hashes: `SHA256SUMS.json` (incluye checkpoints locales ignorados; excluye finales sellados).
