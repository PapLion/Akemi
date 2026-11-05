# Contratos del entrenador

16 tests únicos ejecutados en extra_tests.py (incluye las8 pruebas de tests.py), todos PASS; no sumar ambas ejecuciones como24 pruebas distintas. Logs iniciales y final preservados.

- Causalidad train/eval: cambiar sufijo desde posición21 no cambia logits anteriores, tres brazos; dropout0, CPU FP32, tolerancia1e-6.
- Atención por documento, independencia entre filas, padding y packed/unpacked: salida de documentos juntos coincide con separada; logits en padding cero. Loss shifted se compara contra CE manual; excluye cruces de documentos y padding, incluye EOS legítimo.
- Gradientes finitos y no ausentes para todos los parámetros activos; cambian tras AdamW; identidad exacta de grupos sin duplicados ni huérfanos; estado AdamW para cada parámetro activo. Sin módulos reconstruidos después de crear optimizador.
- No-Hielo congela deliberadamente address/event_value/address_out/read. Transformer congela además fast y fast_norm. Estos parámetros siguen asignados para mantener inicialización compartida, pero no se contabilizan como activos.
- Gradiente de un logit posterior alcanza embeddings escritos en chunk anterior; actualización rank1 sin alterar logits del chunk actual; no-Hielo es invariante al prefijo que salió de ventana.
- Generación incremental vs forward completo: atol2e-6/rtol1e-5. Nuevo session_id sin reset rechazado. Sesión guardada después23tokens (H y prefijo pendiente) continúa exactamente hasta39tokens tras recarga segura.
- Reanudación completa:8 updates continuos vs3+save/restore+5, tres brazos. Igualdad exacta de parámetros y todos los tensores/contadores AdamW al final. Se guardan torch/Python RNG, cursor, updates/microsteps, orden, datasetSHA, tokenizerFP, config, acumulación1 y schedulerNone. No NumPy/AMP/DDP/worker RNG utilizado. Sin acumulación parcial pendiente.

Reanudación certificada exclusivamente CPU FP32 monoproceso, dropout0, un thread. No transferible automáticamente a CUDA, AMP, multiproceso ni generación con muestreo aleatorio. Checkpoints torch.load(weights_only=True), .pt locales ignorados por git y hasheados. Código histórico intacto; freeze protocol.json antes de entrenar.
