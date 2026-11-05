{
  "name": "trapos-selection-v1",
  "source": "5f2a166, seed-specific Addressable V1.2 C final checkpoints",
  "updates": 300,
  "batch": 8,
  "seeds": [
    17,
    29,
    43
  ],
  "lr": 0.003,
  "betas": [
    0.9,
    0.95
  ],
  "decay": 0.01,
  "clip": 1.0,
  "precision": "CPU FP32, 1 thread",
  "objective": "response CE + (C only) 0.1 acceptance BCE; no value auxiliary",
  "policy": "C hard threshold .5 forward, straight-through sigmoid backward (biased estimator); hard eval",
  "architecture": "only 545-parameter 32->16->1 policy head; shared existing parameters trainable in all arms; same 8x32 Hielo/Delta/key/value/reader",
  "candidates": "all framed opcodes =!~^+; no semantic rejection by extractor",
  "acceptance": "confirmed AND not negated AND entity in active goal pair; valid repeats accepted; novelty not evaluated",
  "random_calibration": "train C first, evaluate deterministic final acceptance fraction over TRAIN only; B same fixed probability, causal stateless hash, no dev calibration",
  "order": "C then A then B then D per seed; same 2400 records in original order",
  "main_targets": 2400,
  "C_aux_targets": 12000,
  "selection": "final update300; no dev selection or adaptive hyperparameters",
  "evaluation": "train pairs exclude A-C; dev A-C, novel layouts2/3, held surface aliases %, &, opcode+ shared extractor; clean control",
  "triage": {
    "precision": 0.95,
    "recall": 0.95,
    "normal_contaminated": 0.95,
    "joint_contaminated": 0.9,
    "joint_layout_surface": 0.9,
    "clean_normal": 0.95,
    "clean_drop_vs_D": 0.05,
    "advantage_vs_A_B": 0.1,
    "counterfactual_joint": 0.9,
    "C_override_all_drop": 0.1,
    "random_rate_difference": 0.05
  },
  "confirmation": "all gates C17 then paired A/B/C/D29,43 unchanged; stop after failed pilot; no sealed sets",
  "limits": "no GPU, money, language training, tokenizer or corpus access"
}

Interpretación de «congelar Hielo»: se congelan sus ecuaciones, dimensiones y organización, no todos sus pesos. Los parámetros compartidos parten idénticos de C V1.2 por semilla y siguen entrenables en los cuatro brazos. Solo C entrena la cabeza adicional; A/B/D la instancian idéntica pero congelada. No se atribuye por ello cualquier ganancia exclusivamente a la arquitectura: se evalúa la intervención sobre decisiones del mismo C.

Los ejemplos y su orden son idénticos por semilla. El control B se calibra después de entrenar C, exclusivamente sobre TRAIN, con la política final hard; nunca usa dev. Se registra fracción prevista y realizada. Sus decisiones son un hash pseudoaleatorio causal del prefijo por documento y semilla, estable entre batches y reanudaciones. No usa etiquetas ni el objetivo futuro.

D recibe explícitamente la máscara oracular: límite superior asistido, no resultado autónomo. La API prohíbe suministrar oracle_mask a A/B/C. C recibe 12.000 targets de aceptación extra frente a cero en A/B/D. La diferencia de supervisión es intencionada y declarada; no constituye comparación de igual señal total de entrenamiento.
