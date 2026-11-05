# Reproducción y preservación

Worktree aislado `cryo-selective-memory-study`, rama `cryo-selective-memory-v1`, padre `b7d4b13`. Los fuentes anteriores en `mechanism-study/`, `vendor/`, `models.py` y `experiment.py` no se editan. Las ramas históricas siguen en sus propios worktrees. No se accede a A4, NeoToken, Chinchilla ni evaluaciones históricas selladas.

Desde este worktree:

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
$PY selective-memory/verify_panel.py
$PY -m unittest discover -s selective-memory/tests -v
$PY selective-memory/learn.py pilot
$PY selective-memory/learn.py extend --max-seconds 1800
$PY selective-memory/validate_results.py
$PY selective-memory/diagnose.py extend
$PY selective-memory/report.py
$PY selective-memory/summarize_diagnostics.py
$PY selective-memory/performance.py
```

`learn.py` omite finales ya completos y restaura checkpoints parciales estrictamente; repetir una invocación acotada continúa los brazos pendientes sin duplicar los completados. Ejecutar UN solo entrenador y nunca `performance.py` simultáneamente con él. Las mediciones almacenadas no requieren reentrenar. Un checkpoint/JSON incongruente debe investigarse, no borrarse automáticamente. Para una reproducción desde cero usar una copia nueva del worktree con `results/` vacío y los mismos datos/versiones; nunca borrar las evidencias originales.

`verify_panel.py` regenera únicamente splits no sellados en memoria y compara bytes/hash. No ejecutar `panel.py` sobre los artefactos existentes: se niega a sobrescribir. El nuevo final local permanece con permisos000 y fuera de Git; su hash se toma del manifest registrado durante construcción, no de una nueva lectura. Esto no equivale a custodia independiente de terceros. No hay resultados finales sellados ni selección de modelos sobre él.

Los checkpoints locales `.pt` están excluidos de Git; sus hashes y rutas se inventarían al cerrar. `weights_only=True` y `strict=True`; no pickle genérico. JSONL/CSV contienen predicciones, pérdidas, índices y métricas completas, también resultados negativos. El checkpoint guarda configuración, AdamW, RNG Torch/Python/sampler, cursor, contador, acumulación explícita1 y datasetSHA. No scheduler, AMP, CUDA, workers distribuidos ni gradientes pendientes.

El hash serializado del dataset que guarda el runner usa `json.dumps(rows,sort_keys=True)`; el SHA de archivo del manifest usa JSONL. Son identidades distintas deliberadas, no certificados intercambiables. `v5-code-manifest.json` identifica los fuentes antes del aprendizaje; los scripts de análisis añadidos después no modifican la ruta entrenada.

## Versiones exploratorias rechazadas

`data/` (v1), `data-v2/`, `data-v3/`, `data-v4/`, sus snapshots de generador y resultados `micro*`, `pilot-v4/`, `extend-v4/` se preservan separados. Las correcciones y motivos están en PROTOCOL.md. Solo `data-v5/`, `results/pilot/` y `results/extend/` alimentan los resultados actuales. Los microfits v3 son diagnósticos de capacidad de optimización; no se presentan como entrenamiento sobre v5 ni como generalización. Los programas anteriores y sus finales nuevos tampoco se abren para seleccionar arquitectura.

## Análisis y ablaciones de cierre

```bash
$PY selective-memory/source_equivalence.py
$PY selective-memory/shortcut_audit.py
$PY selective-memory/semantic_audit.py
$PY selective-memory/value_binding_audit.py extend
$PY selective-memory/ablate.py
$PY selective-memory/random_control.py
$PY selective-memory/diagnose.py ablations
$PY selective-memory/value_binding_audit.py ablations
$PY selective-memory/ablation_report.py
$PY selective-memory/show_samples.py
```

El control random tiene presupuesto esperado0,0715298131 fijado desde32programas IID del piloto; su puerta opcional está en results/random-control-gate.json. La política aleatoria usa estado RNG restaurado para reanudar; el diagnóstico empareja máscaras RNG991 sin compactar ni reordenar batches. Las métricas finales del runner y ese diagnóstico son realizaciones aleatorias distintas, explícitamente separadas.

`network_trained_v5.py` y `learn_trained_v5.py` conservan los bytes de fuentes previos al entrenamiento primario. Después se corrigió el acceso a trazas histórico y se incorporó identidad/configuración de random; la ruta normal se compara con el snapshot mediante logits, gradientes y dos updates exactos en source_equivalence.py. `SHA256SUMS.json` inventaría fuentes, datos no sellados, resultados y checkpoints locales, sin abrir finales sellados. Los hashes de finales permanecen en sus manifests originales. Los `.pt` quedan locales ignorados por Git; para trasladarlos usar ese inventario y no regenerarlos silenciosamente.
