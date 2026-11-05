# Contratos comprobados

CPU FP32 monoproceso, un thread; modelos desechables. `results/tests-closeout.log` conserva22 tests PASS. `results/tests-final.log` preserva el corte anterior de17 tests. `results/engineering.json` contiene los diez brazos con tres actualizaciones reales, cobertura del optimizador y reanudación exacta tras dos updates. No se heredan certificados CUDA/BF16 del diseño anterior.

Comprobado por ejecución:

- Causalidad train/eval por perturbación del futuro y gradiente respecto a activaciones futuras; una escritura de un fragmento nunca cambia logits de ese mismo fragmento.
- Aislamiento de documentos y batches, padding, etiquetas desplazadas y máscaras de targets, paridad packed/unpacked.
- Continuación en fronteras completas de fragmento, gradientes a través del estado y rechazo de continuación parcial. Estado vivo conserva autograd; persistirlo en disco implica detach y un límite explícito de BPTT.
- Identidad explícita de sesión por fila para reutilizar estado; una identidad ausente, ajena o reordenada se rechaza. El llamador debe asignar identidades correctas: el modelo no descubre una sesión falsamente etiquetada.
- Actualizaciones de todos los parámetros relevantes, gradientes finitos no nulos, AdamW sin parámetros omitidos ni duplicados inesperados. Los parámetros irrelevantes por ablación están congelados explícitamente.
- El estado cambia, la entrada activa influye en la escritura y cambiar Hielo cambia salidas posteriores. Son efectos funcionales, no prueba de selección semántica útil.
- Composición afín Delta secuencial/paralela con valores y gradientes FP64 y logits/gradientes del modelo FP32; fragmentos32/64 probados estructuralmente.
- Checkpoint con modelo, configuración, AdamW, RNG PyTorch/Python, cursor, sampler, contadores, identidad de tokenizer/dataset y estado de acumulación. Scheduler ausente y acumulación1 son explícitos. Trayectoria y estado AdamW idénticos tras restauración CPU, con dropout0.
- Serialización tensor-only del estado en una frontera detached mediante `weights_only=True`; no se serializan grafos autograd. La persistencia entre fragmentos en memoria sí permite BPTT.
- NeoToken V3 BPE8K real: todo el DSL tiene roundtrip y encode canónico exactos. No se cambia el tokenizer ni se consumen vistas multiescala adicionales.

Fallos y correcciones conservados: importaciones iniciales RED; compuertas de `always_write` que no podían influir detectadas por falta de gradiente y congeladas explícitamente; evaluación del baseline corregida al recibir trazas vacías antes del primer update de aprendizaje. Los cambios posteriores de identidad de sesión/contadores se comparan contra `vendor/next_training_v1.py`: mismos logits y gradientes.

Pendiente: estados maliciosos semánticamente mal etiquetados, secuencias arbitrarias parcialmente recibidas por streaming, reanudación en mitad de un grafo/gradiente acumulado, DDP, AMP y CUDA. No se certifican. Las pruebas no acreditan capacidad lingüística.

Una regresión adicional demostró que identidades duplicadas dentro del batch hacían imposible detectar un reordenamiento. Se rechazan ahora; RED en results/duplicate-session-red.log y prueba de cierre PASS. Es un refuerzo de metadatos, sin cambio de ecuaciones o aprendizaje.
