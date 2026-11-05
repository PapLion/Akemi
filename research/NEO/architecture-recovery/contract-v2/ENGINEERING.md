# Certificación ejecutada

preflight.json: causalidad train/eval de logits y scores, máscaras, aislamiento de documentos/batch, reset, no escritura al rechazar, ecuación Delta intacta al aceptar, gradientes reales del filtro, AdamW sin omisiones/duplicados y actualización real. Reanudación exacta10updates frente4+save+6 en A/B/C/D; B/D son solo fixtures mecánicos, no nuevas trayectorias de300updates.

final-integrity.json: modelo byte-idéntico V1, código preregistrado sin cambios durante campaña, checkpoints finales y estados AdamW restaurados exactamente, inicializaciones A/C iguales, fuentes históricas intactas y consultas emparejadas sin cambiar prefijo/etiquetas. C no puede recibir oracle_mask; solo intervenciones explícitamente D reciben etiquetas de selección.

CPU FP32 monoproceso; no se certifica CUDA/AMP. No se abrió test sellado, no se usó GPU ni servicios pagos.
