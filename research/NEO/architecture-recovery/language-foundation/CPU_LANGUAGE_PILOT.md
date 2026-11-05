# Piloto CPU ejecutado

Protocolo fijado antes de entrenar en PROTOCOL.json: seed17,128updates por brazo,batch2,128IDs,stride127,AdamW.003 betas.9/.95,wd.01,clip1,FP32,un thread. Techo32512targets y180s por brazo; ambos terminaron128updates con32433targets. Ninguna ampliación, ajuste dev o selección de checkpoint. Dos corridas pequeñas, no pretraining principal.

Forward foreground utiliza chunk_hidden sobre ventana completa128 y la misma cabeza tied. Es la interfaz de contexto completo de los diagnósticos, **no el forward local16 de Language Bridge V1**. No cambia pesos/módulos/ecuaciones; se declara la política de ventana. Una ventana pertenece a un documento y una fila: no packing mezclado ni estado entre documentos. Baseline usa misma visibilidad y ventanas, inicialización propia documentada.

| Modelo | Parámetros activos | NLL train final | NLL dev inicial → final | PPL dev | Targets/s | RAM MiB |
|---|---:|---:|---:|---:|---:|---:|
| foreground | 296160 | 4.8493 | 8.9941 → 5.7674 | 319.71 | 5638.3 | 773.1 |
| baseline | 293024 | 4.8721 | 8.9901 → 5.8379 | 343.05 | 4943.5 | 773.1 |


Por dominio al final: foreground train código NLL4,7463 / expositivo5,5448; baseline4,7731/5,5414. Dev código5,7674/5,8379; ES/dev expositivo no disponible. No promediar dominios ausentes ni atribuir la diferencia0,0705NLL a arquitectura con una semilla.

Control unigram calculado solo con targets train, smoothing0,1 fijado antes de calcular: train NLL5.4493, dev6.2673. Ambos modelos superan este control marginal en dev; existe señal predictiva transferible adicional a frecuencias simples. No aísla semántica ni composicionalidad.

Generaciones greedy32tokens en3prompts prefijados guardadas por ID/texto: repetición de puntuación/espacios en ambos. Continuación técnica de prefijos nuevos funciona, pero calidad no útil. El descenso de NLL no convierte estas salidas en lenguaje competente. PPL depende de V3, dominio y máscara: no comparar contra otro tokenizer.

Contratos previos: causalidad por perturbación futura, aislamiento de filas, shift/máscara comparada con CE manual, AdamW exacto, gradientes finitos, reanudación7updates vs3+4 con igualdad exacta de parámetros/momentos/RNG/cursor. Verificación adicional: cada parámetro activo tiene gradiente no nulo y cambia, padding no afecta posiciones válidas. Checkpoints0/128, restauración final reproduce dev exactamente. Solo CPU mono-thread/dropout0; no certificado AMP/CUDA/DDP.

Tiempo solo updates foreground5.752s, baseline6.561s; incluye gradientes/clipping, excluye evaluación/encode/setup. RAM high-water del proceso, no comparativa de memoria aislada. Muestreo determinista idéntico, hashes de fuente/datos/orden en reproducibility.json.


Diagnóstico sin reentrenamiento: excluyendo tokens whitespace y especiales quedan7245 targets dev. Foreground NLL6,4944, baseline6,5646, unigram6,8616. La ventaja no se limita a predecir espacios; tampoco prueba comprensión contextual. Los tres prompts prefijados no aparecen literalmente en train, comprobado contra los archivos originales.
