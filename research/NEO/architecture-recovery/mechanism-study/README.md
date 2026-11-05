# Cryo: mecanismo de aprendizaje

Investigación CPU aislada en la rama `cryo-mechanism-v1`, worktree `/PATH/TO/NEO_HOME/research/neo-architecture-recovery/cryo-mechanism-study`. Padre histórico `78373cc` permanece en `../cryo-next-generation`, rama `cryo-next-generation-v1`. No se sobrescriben sus checkpoints/resultados. Sin GPU, corpus Chinchilla, A4, cambios de tokenizer ni evaluación sellada.

Leer primero `DECISION.md`, `PERFORMANCE.md` y `NEXT_EXPERIMENT.md`. Consultar `REPRODUCIBILITY.md`. Después `EXPERIMENT_VALIDITY.md`, `PROTOCOL_MATRIX_FROZEN.md`, suplemento de capacidad en `PROTOCOL.md`, `HYBRID_DESIGN.md` y `RESULTS.md`. Las cifras corresponden a DSL simbólico de64IDs, un único target y generalización composicional; no lenguaje natural.

## Reproducción

Desde este worktree, usar el entorno CPU disponible:

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
$PY -m unittest discover -s mechanism-study/tests -v
$PY -m unittest discover -s tests -v
$PY mechanism-study/audit.py
$PY mechanism-study/microfit.py
$PY mechanism-study/run.py --max-seconds 2400
$PY mechanism-study/capacity_run.py --max-seconds 600
$PY mechanism-study/matched_run.py --max-seconds 600
$PY mechanism-study/hybrid_run.py --max-seconds 600
$PY mechanism-study/support_probe.py
$PY mechanism-study/state_diagnostics.py
$PY mechanism-study/gradient_audit.py
$PY mechanism-study/report.py
$PY mechanism-study/task_metrics.py
$PY mechanism-study/stale_fact_probe.py
$PY mechanism-study/hybrid_effects.py
# Ejecutar benchmark únicamente después de finalizar los entrenamientos:
$PY mechanism-study/benchmark.py
$PY mechanism-study/benchmark_interleaved.py
$PY mechanism-study/final_report.py
$PY mechanism-study/validate_results.py
$PY mechanism-study/manifest.py
```

`run.py`/`capacity_run.py` omiten brazos con JSON final ya publicado; no duplicar procesos. El límite se comprueba entre brazos; termina el brazo en curso, por lo que no es un deadline rígido. Guarda pesos/AdamW/RNG/configuración/update/cursor/identidad de datos y orden completo por semilla. Reanudación intermedia del runner ante interrupción abrupta no está implementada: se repite solo el brazo incompleto; la reanudación de trayectoria del modelo/AdamW sí tiene tests después de updates. Los modelos y optimizadores se construyen antes de actualizar; no se crean módulos durante entrenamiento.

Los `.pt` derivados se conservan localmente pero están excluidos de Git. `RESULTS.md` se genera sin seleccionar semillas o checkpoints. `curves.csv` contiene todas las pérdidas y normas de gradiente. La auditoría de logits y la prueba de soporte son derivadas separadas de los resultados originales.

## Alcance de las pruebas

Referencia exacta; logits chunk1/gradientes/updates contra histórico; causalidad train/eval; packing/reset; independencia batch; gradientes finitos no nulos y actualizaciones en fixtures; cobertura AdamW; guardar/cargar seguro tras dos updates y continuación exacta de parámetros; crédito entre pares; control de capacidad. Padding se cubre en equivalencia chunk1. No se hereda certificado CUDA/BF16 ni streaming externo de estados.

`detach` es una ablación de receta, no de forward: se corta BPTT temporal antes de cada token. La inicialización de memoria no puede recibir señal útil del único target final bajo ese corte y se congela explícitamente. Los parámetros no usados de las demás ablaciones también se congelan; no se presentan como parámetros activos.

## Suplementos y cierre

Después de la matriz principal se fijaron controles de capacidad e inicialización (`capacity_run.py`, `matched_run.py`) y los híbridos que conservan el procesamiento rápido (`hybrid_run.py`). Ver la cronología en `PROTOCOL.md`. Cada ejecutor usa carpeta de resultados propia; todos los resultados se incluyen. Estos suplementos reutilizan dev para investigación y no constituyen una evaluación final independiente.

Para reproducir el suplemento híbrido: `$PY mechanism-study/hybrid_run.py --max-seconds 600`. Después, ejecutar `hybrid_effects.py`, `validate_results.py` y `manifest.py`. El primer script suprime lectura únicamente durante inferencia; no representa entrenar un modelo sin memoria.
