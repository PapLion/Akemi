# Diferenciación y conservación

Estadísticas de B sobre batch fijo8, chunk después de ambos facts:
```json
{
  "query_cosine": 0.6873925924301147,
  "state_cosine": 0.9952541589736938,
  "weight_l1": 0.12642431259155273,
  "query_gradient_norms": [
    0.052941132336854935,
    0.07730450481176376
  ],
  "query_gradient_cosine": 0.9994296431541443,
  "contribution_norms": [
    0.3538020849227905,
    0.3728020191192627
  ],
  "mean_write_gate": [
    0.10209626704454422,
    0.11209622025489807
  ]
}
```

Las queries difieren, ambas escriben y reciben gradientes, pero los candidatos de estado son casi iguales (coseno≈.9953) y sus gradientes casi paralelos(≈.9994). Esto sugiere poca especialización aprendida en este diagnóstico; no hay degeneración algebraica que los obligue a coincidir. No basta para llamar selección de bindings a la atención diferenciada. Pesos completos por token y estados en B-selection-weights.json/B-candidate-trace.pt.

Conservación/corrección fuera de entrenamiento,640programas por brazo con repetición o corrección de cada entidad; mismas reglas causales, sin actualizar pesos:
```json
{
  "A": {
    "preserve": {
      "affected_correct": 0.25,
      "other_correct": 0.246875,
      "follows_initial": 0.25,
      "n": 320
    },
    "correct": {
      "affected_correct": 0.25,
      "other_correct": 0.25,
      "follows_initial": 0.25,
      "n": 320
    }
  },
  "B": {
    "preserve": {
      "affected_correct": 0.496875,
      "other_correct": 0.25,
      "follows_initial": 0.496875,
      "n": 320
    },
    "correct": {
      "affected_correct": 0.428125,
      "other_correct": 0.28125,
      "follows_initial": 0.19375,
      "n": 320
    }
  },
  "C": {
    "preserve": {
      "affected_correct": 0.803125,
      "other_correct": 0.409375,
      "follows_initial": 0.803125,
      "n": 320
    },
    "correct": {
      "affected_correct": 0.440625,
      "other_correct": 0.46875,
      "follows_initial": 0.215625,
      "n": 320
    }
  }
}
```

Todos son diagnósticos de transferencia, no microfits de corrección. Los estados inmediatamente tras escritura, tras evento y antes de consulta se guardan conIDs. Candidate-ablation.json omite cada actualización en inferencia: explora dependencia de cada candidato, no sustituye un entrenamiento sin candidato ni aísla solo el término de valor (también omite retención/borrado). No demuestra asociaciones exclusivas por candidato.
