# Optimización

No se modificó LR, optimizador, clipping, inicialización, arquitectura ni dimensiones. AdamW alcanza400 pasos en todos los tensores activos del nivel4. Multiplicador de decay por paso0,99997; estados first/second moment quedan en checkpoint.

Clipping actúa en87,75% de los updates; norma inicial4,630721, última3,347909, escala mínima0,087843. No se ha demostrado que clipping cause el bloqueo. Actualizaciones no nulas y normas completas están en las curvas, con deltas inicial/final en forensics.json.

Sondeo de fast pre-tanh en primer batch (todas las posiciones, no solo respuesta): fracción |preactivación|>3 pasa por48,18% en el primer refinamiento y7,86% en el segundo al final. RMS y máximos de normalizaciones en optimization-diagnostics.json. Hay saturación parcial, no bloqueo total: la misma implementación sobreajusta nivel3. Esto no justifica cambiar tanh automáticamente.

Los minibatches de8 extraídos de una permutación fija repetida no están perfectamente balanceados: algunos contienen solo3 de4 valores. Cobertura total3200 respuestas:1600 por entidad y803/800/797/800 por valor. Balance del dataset no implica balance de minibatch. No se cambió el sampler para probar otra hipótesis.

Clasificación: existen competencia de objetivos, saturación parcial y señales desiguales, pero ninguna causa aislada demostrada. No se realizó una corrección arbitraria de optimización. La única intervención de señal se documenta por separado.

Incidencia de verificación preservada: el primer comparador de checkpoint denso falló por claves enteras de pred_counts convertidas a strings por JSON, no por pesos o logits distintos. Se normalizó solo la representación JSON y el contraste exacto completo pasa sin relajar tolerancias; log original conservado. Warning float de tensor con grad corresponde a lectura de métricas, no a detach de la ruta de pérdida.
