# Valores vigentes, obsoletos e intercambio

{
  "A": {
    "value_swap": {
      "n": 120,
      "strict_binding_pair_accuracy": 0.0,
      "original_joint_accuracy": 0.0
    },
    "obsolete": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.0625,
      "original_joint_accuracy": 0.25
    },
    "current": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.0,
      "original_joint_accuracy": 0.0
    }
  },
  "B": {
    "value_swap": {
      "n": 120,
      "strict_binding_pair_accuracy": 0.0,
      "original_joint_accuracy": 0.0
    },
    "obsolete": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.125,
      "original_joint_accuracy": 0.25
    },
    "current": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.015625,
      "original_joint_accuracy": 0.0
    }
  },
  "C": {
    "value_swap": {
      "n": 120,
      "strict_binding_pair_accuracy": 0.0,
      "original_joint_accuracy": 0.25
    },
    "obsolete": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.2,
      "original_joint_accuracy": 0.44375
    },
    "current": {
      "n": 320,
      "strict_binding_pair_accuracy": 0.05,
      "original_joint_accuracy": 0.253125
    }
  }
}

Swap intercambia los valores de las dos entidades, conservando presencia y layout;120casos con valores diferentes por brazo. Criterio fuerte: las dos asociaciones correctas en original Y editado. Los tres brazos obtienen0/120, también C pese a mejor exactitud marginal y lector.

Obsolete cambia la primera escritura de la entidad corregida y conserva corrección final. Current cambia última escritura de entidad consultada; si no fue la corregida, se modifica su escritura inicial. Etiquetas siempre recalculadas por prefijo. Se evalúan ambas asociaciones tras evento y lector original; no se confunde invariancia con comprensión. No se usó final sellado.
