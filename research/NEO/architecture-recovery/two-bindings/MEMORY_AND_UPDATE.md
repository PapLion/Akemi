# Formación, conservación y actualización

|Brazo / split|Inicial rol A|Inicial rol B|Conjunta inicial|Conjunta posterior|Conjunta retenida|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A / train|40.00%|43.75%|16.25%|13.75%|13.75%|35.94%|
|A / dev-layout|43.12%|41.88%|14.37%|14.69%|12.50%|35.94%|
|B / train|44.38%|47.50%|15.00%|15.00%|11.56%|32.81%|
|B / dev-layout|45.62%|45.62%|14.37%|13.75%|11.88%|31.56%|

Exactitud posterior de entidad afectada y de entidad no modificada, train:
```json
{
  "A": {
    "preserve": {
      "affected_correct": 0.50625,
      "unmodified_correct": 0.34375,
      "n": 160
    },
    "correct": {
      "affected_correct": 0.35,
      "unmodified_correct": 0.35,
      "n": 160
    }
  },
  "B": {
    "preserve": {
      "affected_correct": 0.5375,
      "unmodified_correct": 0.38125,
      "n": 160
    },
    "correct": {
      "affected_correct": 0.43125,
      "unmodified_correct": 0.35625,
      "n": 160
    }
  }
}
```

En preserve, la conjunta posterior es15.625% en ambos brazos. En correct,11.875% A y14.375% B. La señal parcial no demuestra almacenamiento fiable ni actualización sin corrupción. Las métricas marginales no implican que ambas asociaciones sean correctas al mismo tiempo. Retención antes de consulta se mide con el mismo decoder, aunque esa etapa no tiene supervisión directa.

Estados reales, sin simulación, guardados en *-states.pt: [documento,etapa,8claves,32dimensiones], etapas inicial/post/retained, acompañados de IDs. No se usa estado posterior para etiquetar inicial.
