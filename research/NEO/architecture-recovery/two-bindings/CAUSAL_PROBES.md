# Contrafactuales y estados reales

Diagnósticos completos en diagnostics.json, sin usar final sellado. Obsolete cambia primer valor de entidad corregida, dejando vigente inalterado (solo correct). Current cambia última escritura de entidad consultada. Oráculo recalcula cada etiqueta; se reportan conjuntas por versión y por asociación, no solo cambio de logits.

Donante compatible cambia solo valor vigente consultado y mantiene idénticos últimos16IDs. Se sustituye memoria real chunk6 en lectura chunk7; no se inyecta un vector inventado. Resultado conjunto lector original+donante: A14/320(4.375%); B11/320(3.4375%). Son intervenciones diagnósticas, no pruebas de uso exitoso. Algunas ediciones current convierten repetición en corrección; se reconoce el desplazamiento de distribución.

Resumen de métricas contrafactuales:
```json
{
  "A": {
    "obsolete": {
      "all": {
        "n": 160,
        "original_joint": 0.225,
        "original_invariance": 0.64375,
        "post_joint_both_versions": 0.09375,
        "post_query_joint": 0.2875,
        "post_other_joint": 0.31875
      },
      "query_corrected": {
        "n": 80,
        "original_joint": 0.175,
        "original_invariance": 0.625,
        "post_joint_both_versions": 0.1125,
        "post_query_joint": 0.3125,
        "post_other_joint": 0.2875
      },
      "other_corrected": {
        "n": 80,
        "original_joint": 0.275,
        "original_invariance": 0.6625,
        "post_joint_both_versions": 0.075,
        "post_query_joint": 0.2625,
        "post_other_joint": 0.35
      }
    },
    "current": {
      "all": {
        "n": 320,
        "original_joint": 0.04375,
        "original_invariance": 0.75625,
        "post_joint_both_versions": 0.021875,
        "post_query_joint": 0.09375,
        "post_other_joint": 0.340625
      },
      "query_corrected": {
        "n": 160,
        "original_joint": 0.025,
        "original_invariance": 0.78125,
        "post_joint_both_versions": 0.0375,
        "post_query_joint": 0.1125,
        "post_other_joint": 0.28125
      },
      "other_corrected": {
        "n": 160,
        "original_joint": 0.0625,
        "original_invariance": 0.73125,
        "post_joint_both_versions": 0.00625,
        "post_query_joint": 0.075,
        "post_other_joint": 0.4
      }
    }
  },
  "B": {
    "obsolete": {
      "all": {
        "n": 160,
        "original_joint": 0.1875,
        "original_invariance": 0.675,
        "post_joint_both_versions": 0.11875,
        "post_query_joint": 0.325,
        "post_other_joint": 0.35625
      },
      "query_corrected": {
        "n": 80,
        "original_joint": 0.1375,
        "original_invariance": 0.6125,
        "post_joint_both_versions": 0.1,
        "post_query_joint": 0.3375,
        "post_other_joint": 0.2875
      },
      "other_corrected": {
        "n": 80,
        "original_joint": 0.2375,
        "original_invariance": 0.7375,
        "post_joint_both_versions": 0.1375,
        "post_query_joint": 0.3125,
        "post_other_joint": 0.425
      }
    },
    "current": {
      "all": {
        "n": 320,
        "original_joint": 0.034375,
        "original_invariance": 0.76875,
        "post_joint_both_versions": 0.015625,
        "post_query_joint": 0.140625,
        "post_other_joint": 0.334375
      },
      "query_corrected": {
        "n": 160,
        "original_joint": 0.01875,
        "original_invariance": 0.8,
        "post_joint_both_versions": 0.025,
        "post_query_joint": 0.19375,
        "post_other_joint": 0.25
      },
      "other_corrected": {
        "n": 160,
        "original_joint": 0.05,
        "original_invariance": 0.7375,
        "post_joint_both_versions": 0.00625,
        "post_query_joint": 0.0875,
        "post_other_joint": 0.41875
      }
    }
  }
}
```
