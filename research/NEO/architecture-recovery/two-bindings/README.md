# Cryo: dos bindings y supervisión por etapa

Rama cryo-two-bindings-v1, origen6f3acf1. Dos brazos150updates CPU FP32, semilla17, DeltaFast y decoder originales intactos. Sin GPU, corpus, evaluaciones selladas ni600updates.

|Brazo / split|Inicial rol A|Inicial rol B|Conjunta inicial|Conjunta posterior|Conjunta retenida|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A / train|40.00%|43.75%|16.25%|13.75%|13.75%|35.94%|
|A / dev-layout|43.12%|41.88%|14.37%|14.69%|12.50%|35.94%|
|B / train|44.38%|47.50%|15.00%|15.00%|11.56%|32.81%|
|B / dev-layout|45.62%|45.62%|14.37%|13.75%|11.88%|31.56%|

Rol A es entidad consultada; rol B es la otra. No confundir esos roles con nombres de brazos. El azar marginal es25%; conjunta independiente6.25%, referencia que no sustituye controles de priors. Ambos brazos fallan el microfit inicial bajo esta receta.

Ver DECISION.md y resultados completos en results/. Scripts: two_bindings.py (datos, contratos, entrenamiento/evaluación), diagnostics.py (contrafactuales/gradientes/estados donantes), verify_outputs.py, make_report.py.
