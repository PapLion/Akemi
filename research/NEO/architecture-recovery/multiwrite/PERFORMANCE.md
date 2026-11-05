# Coste CPU medido

Recursos de ejecución completa:
```json
{
  "A": {
    "seconds": 21.483083408998937,
    "seconds_per_update": 0.07161027802999645,
    "model_params": 289731,
    "trainable_params": 285539,
    "decoder_params": 5140,
    "peak_process_rss_kib": 963640,
    "note": "RSS cumulative high-water mark; sequential process, not isolated per-arm peak"
  },
  "B": {
    "seconds": 23.596351936001156,
    "seconds_per_update": 0.07865450645333719,
    "model_params": 289763,
    "trainable_params": 285571,
    "decoder_params": 5140,
    "peak_process_rss_kib": 963640,
    "note": "RSS cumulative high-water mark; sequential process, not isolated per-arm peak"
  },
  "C": {
    "seconds": 21.47292350999851,
    "seconds_per_update": 0.07157641169999503,
    "model_params": 289731,
    "trainable_params": 285539,
    "decoder_params": 5140,
    "peak_process_rss_kib": 963640,
    "note": "RSS cumulative high-water mark; sequential process, not isolated per-arm peak"
  }
}
```

B tarda9.84% más que A en300updates. +32parámetros (~0.011% del modelo), sin ampliar Hielo. No se ejecutó control adicional de capacidad: la comparación no separa completamente efecto de esos parámetros, inicialización, doble escritura y mayor cómputo. No se afirma causalidad por descarte debido a su pequeño tamaño. Se mantuvo matriz primaria de3brazos; tras fallar gate no se añaden controles posthoc entrenados.

Forward/backward separados: cinco updates medidos tras2warmups sobre copias descartables:
```json
{
  "A": {
    "steps": 5,
    "warmup": 2,
    "means": {
      "forward_ms": 37.013791999197565,
      "backward_ms": 39.454549200308975,
      "clip_adamw_ms": 4.041314400092233
    },
    "scope": "Disposable loaded copy; includes common loss extraction; not pure model forward"
  },
  "B": {
    "steps": 5,
    "warmup": 2,
    "means": {
      "forward_ms": 43.384043199330335,
      "backward_ms": 50.884799800405744,
      "clip_adamw_ms": 4.033068599528633
    },
    "scope": "Disposable loaded copy; includes common loss extraction; not pure model forward"
  },
  "C": {
    "steps": 5,
    "warmup": 2,
    "means": {
      "forward_ms": 39.54460880122497,
      "backward_ms": 43.972346398368245,
      "clip_adamw_ms": 3.9792110001144465
    },
    "scope": "Disposable loaded copy; includes common loss extraction; not pure model forward"
  }
}
```

Proxy aislado del writer,50mediciones después de5warmups, batch8 y estados sintéticos fijos:
```json
{
  "A": {
    "forward_median_ms": 0.5707105010515079,
    "backward_median_ms": 1.078917000995716,
    "iterations": 50,
    "warmup": 5,
    "scope": "Isolated writer re-expression, fixed random fast/memory batch8; no reader/refinement/optimizer. Not additive attribution of full update."
  },
  "B": {
    "forward_median_ms": 0.8839304991852259,
    "backward_median_ms": 1.6016709996620193,
    "iterations": 50,
    "warmup": 5,
    "scope": "Isolated writer re-expression, fixed random fast/memory batch8; no reader/refinement/optimizer. Not additive attribution of full update."
  }
}
```

No sumar esos tiempos al forward del modelo ni atribuir un porcentaje exacto del update: son regiones reexpresadas y entradas diferentes. Perfiles CPU completos en *cpu-profile.txt; no CUDA. RAM es high-water RSS acumulativo del proceso, no pico independiente por brazo.

Estimación explícita de operaciones, no medición hardware:
```json
{
  "extra_query_pool_flops_per_chunk": 1024,
  "extra_key_value_control_projection_flops_per_chunk": 2752,
  "extra_delta_transition_approx_flops_per_chunk": 1832,
  "total_extra_forward_approx_flops_per_chunk": 5608,
  "additional_training_heuristic": "~3\u00d7 extra forward; not measured backward FLOPs",
  "not_counted": [
    "sigmoid/tanh/softmax exact transcendental cost",
    "square roots/powers",
    "normalization",
    "mask/scheduler/Python overhead"
  ],
  "state_shape": [
    8,
    32
  ],
  "extra_parameters": 32
}
```
