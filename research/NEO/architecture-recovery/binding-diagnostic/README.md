# Language Binding Diagnostic V1

Contraste CPU ejecutado: dos brazos de 200 updates, semilla 17, batch 8. Resultado negativo de aprendizaje básico bajo la receta fijada; no es un resultado de Hielo.

| Condición | Train respuesta / conjunta | Dev pares nuevos | Dev layouts | Intercambios estrictos dev |
|---|---|---|---|---|
| Hechos cercanos | 25% / 0% | 25% / 0% | 25% / 0% | 0/12 |
| Hechos lejanos | 25% / 0% | 25% / 0% | 25% / 0% | 0/12 |

Ambos producen el mismo token de respuesta para las dos entidades en 24/24 historias de cada panel. No certifican el control corto (conjunta e intercambios >=90%). Se cierra esta línea de memoria lingüística y no se entrena Hielo.

Se conserva el modelo V2 sin cambios. Código en experiment.py/audit.py/tests.py; PROTOCOL.json preregistrado; resultados, curvas, predicciones y checkpoints locales en results/. Artefactos .pt fuera de git, identificados por SHA256SUMS. No GPU, corpus externo, servicios pagados ni evaluaciones selladas.

Ver DECISION.md para el mecanismo observado y sus límites. Reproducción: bash binding-diagnostic/reproduce.sh en un worktree nuevo con results vacío (se niega a sobrescribir evidencias). Los tests sin entrenamiento adicional: Python del entorno local ejecutando binding-diagnostic/tests.py. Se reutilizan sin editar memory-bridge/runner.py y language-bridge/model.py.
