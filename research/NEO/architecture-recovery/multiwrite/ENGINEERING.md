# Contratos ejecutados antes de entrenar

{
  "k1_logits_gradients_exact": true,
  "candidate_gradient_norms": [
    0.0003186067915521562,
    0.0002584520261734724
  ],
  "value_perturbation_norms": [
    0.8494283556938171,
    0.8890818357467651
  ],
  "reader_unchanged": true,
  "causal_train_eval": true,
  "mask_reset_batch": true,
  "continuation_recurrence": true,
  "optimizer_exact": true,
  "preflight_losses": [
    2.9608657360076904,
    2.887003183364868,
    2.295316696166992,
    1.8815277814865112,
    1.6312613487243652,
    1.5219802856445312,
    1.4320725202560425,
    1.351275086402893,
    1.311279535293579,
    1.2815667390823364,
    1.2406418323516846,
    1.1897773742675781,
    1.1372225284576416,
    1.0899569988250732,
    1.048034906387329,
    1.0080755949020386,
    0.9639073610305786,
    0.9135474562644958,
    0.8696337938308716,
    0.8364028334617615
  ],
  "resume_exact": true
}

K1 logits y gradientes exactos contra referencia; además A/C en update150 coinciden exactamente con los históricos en modelo, decoder, AdamW, RNG y cursor (historical-150-parity.json). K2 causalidad train/eval ante perturbación después deID16, CE inicial invariante, padding y reset documental, independencia batch. Igual lector y pesos comunes iniciales. AdamW cubre exactamente todos los parámetros entrenables, incluidas las dos consultas. Gradientes independientes no significa ortogonales: se exige no nulos y no idénticos. Perturbar valor real del chunk alcanza ambos candidatos.

Preflight20updates sobre batch fijo descartable: pérdida total disminuye, sin NaN/Inf. No se interpreta como binding. Reanudación3+3updates vs6continuos exacta con archivo real y weights_only: modelo,decoder,AdamW,Torch/Python/samplerRNG, cursor y orden. El estado entre chunks recibe gradiente. Transición reconstruida desde candidatos reales coincide con memoria registrada.

Chequeos posteriores: gradient-audit.json no encuentra parámetros entrenables sin gradiente en batch diagnóstico; frozen originales se enumeran. additional-checks.json verifica transición K1 y presupuestos. Historical-integrity.json comprueba hashes anteriores sin modificar los archivos. Las pruebas adicionales posteriores additional-causality-edges.json verifican cortes dentro y entre chunks(4,8,12,16,24,32,48) en train/eval y actualización de ambas filas de query. Se distinguen de los contratos previos al entrenamiento. Alcance CPU FP32,dropout0,monoproceso; no CUDA/BF16 ni streaming de sesiones externas.
