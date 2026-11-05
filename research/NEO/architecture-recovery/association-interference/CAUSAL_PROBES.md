# Intervenciones ejecutadas

{
  "A": {
    "reset": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.75,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "swap": {
      "original_accuracy": 0.0,
      "prediction_changed": 1.0,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "obsolete": {
      "n": 80,
      "original_accuracy": 1.0,
      "changed_accuracy": 0.75,
      "joint_correct": 0.75,
      "prediction_invariance": 0.75,
      "aux_pair_joint": 0.171875,
      "memory_distance_after_event": 0.7399962544441223
    },
    "current": {
      "n": 80,
      "original_accuracy": 1.0,
      "changed_accuracy": 0.75,
      "joint_correct": 0.75,
      "prediction_invariance": 0.0,
      "aux_pair_joint": 0.1875,
      "memory_distance_after_event": 2.327223062515259
    },
    "compatible_current_donor": {
      "n": 80,
      "follows_donor": 0.75,
      "joint_original_and_donor": 0.75
    }
  },
  "B": {
    "reset": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.05000000074505806,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "swap": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.10000000149011612,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "obsolete": {
      "n": 80,
      "original_accuracy": 0.30000001192092896,
      "changed_accuracy": 0.30000001192092896,
      "joint_correct": 0.30000001192092896,
      "prediction_invariance": 1.0,
      "aux_pair_joint": 0.38749998807907104,
      "memory_distance_after_event": 1.2586023807525635
    },
    "current": {
      "n": 80,
      "original_accuracy": 0.30000001192092896,
      "changed_accuracy": 0.30000001192092896,
      "joint_correct": 0.05000000074505806,
      "prediction_invariance": 0.8999999761581421,
      "aux_pair_joint": 0.44062501192092896,
      "memory_distance_after_event": 1.856022834777832
    },
    "compatible_current_donor": {
      "n": 80,
      "follows_donor": 0.30000001192092896,
      "joint_original_and_donor": 0.05000000074505806
    }
  },
  "C": {
    "reset": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.4000000059604645,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "swap": {
      "original_accuracy": 0.42500001192092896,
      "prediction_changed": 0.625,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "current": {
      "n": 80,
      "original_accuracy": 0.4000000059604645,
      "changed_accuracy": 0.4000000059604645,
      "joint_correct": 0.15000000596046448,
      "prediction_invariance": 0.375,
      "aux_pair_joint": 0.21250000596046448,
      "memory_distance_after_event": 1.491192102432251
    },
    "compatible_current_donor": {
      "n": 80,
      "follows_donor": 0.4000000059604645,
      "joint_original_and_donor": 0.15000000596046448
    }
  },
  "D": {
    "reset": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.0,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "swap": {
      "original_accuracy": 0.25,
      "prediction_changed": 0.0,
      "scope": "last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only"
    },
    "current": {
      "n": 80,
      "original_accuracy": 0.25,
      "changed_accuracy": 0.25,
      "joint_correct": 0.0,
      "prediction_invariance": 1.0,
      "aux_pair_joint": 0.3375000059604645,
      "memory_distance_after_event": 0.6936110854148865
    },
    "compatible_current_donor": {
      "n": 80,
      "follows_donor": 0.25,
      "joint_original_and_donor": 0.0
    }
  }
}

Obsoleto solo A/B: reemplazo posterior explícito, cambiar inicial mantiene verdad. Vigente: cambiar última escritura de entidad consultada cambia respuesta oráculo. En A la repetición pasa a ser corrección en esta intervención: distribución parcialmente distinta. Donante compatible conserva exactamente ventana final visible y cambia solo valor vigente; su memoria real chunk6 se usa en lectura chunk7, sin alterar escritura ni pesos. Reset/swap estándar afectan únicamente lectura final. Swap batch roll no garantiza parejas de entidad compatibles: exploratorio, no prueba concluyente. Distancia de estados no acredita binding.

La submuestra usa cada octavo registro (80 ejemplos); no es una estimación global estratificada de todas las relaciones de valores. Se reportan denominadores y no se extrapolan sus tasas al corpus. Las intervenciones son diagnósticas, no un conjunto final independiente.
