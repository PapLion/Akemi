# Trapos V1 — selección sobre Addressable

Rama `cryo-trapos-selection-v1`, desde `5f2a166`. Prototipo implementado y CPU ejecutado. Piloto negativo: no se habilitaron semillas 29/43. Semillas ejecutadas: [17]. Resultados funcionales y decisión en DECISION.md.

El diseño de Hielo, Delta, key/value, lector y foreground se conserva. Solo se añade una cabeza de aceptación de 545 parámetros. El extractor compartido ofrece también propuestas inválidas. No se usa lenguaje natural, tokenizer, corpus ni GPU. No se abrió evaluación sellada.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# Reproducción únicamente en copia nueva sin resultados; nunca borrar esta evidencia.
"$PY" trapos/preflight.py
"$PY" trapos/trapos_train.py
"$PY" trapos/final_checks.py
"$PY" trapos/reports.py
```

Los checkpoints .pt se conservan localmente e identifican por SHA256SUMS. El entrenador rechaza sobrescribir un checkpoint final y el preflight rechaza sobrescribir FREEZE. Fuentes y datos históricos son de solo lectura.
