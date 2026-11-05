# Language Learning Foundation V1

Cerrada la cadena de microfits simbólicos. Piloto causal real CPU ejecutado, sin Hielo/Trapos, sin cambios al modelo ni a V3. Base eb2ee86; rama neo-language-learning-foundation-v1.

| Modelo | Parámetros activos | NLL train final | NLL dev inicial → final | PPL dev | Targets/s | RAM MiB |
|---|---:|---:|---:|---:|---:|---:|
| foreground | 296160 | 4.8493 | 8.9941 → 5.7674 | 319.71 | 5638.3 | 773.1 |
| baseline | 293024 | 4.8721 | 8.9901 → 5.8379 | 343.05 | 4943.5 | 773.1 |


Existe aprendizaje transferible a dos archivos de otro repositorio bajo este panel inglés de código. No existe un modelo lingüístico útil: generación repetitiva, sin prueba bilingüe ni generalización semántica. No autoriza pretraining significativo.

Ver DECISION.md, PROTOCOL.json, manifiestos y tests en results/. Reproducir scripts únicamente en una salida/worktree nuevo: pilot.py → analysis.py → checks.py → reports.py. Rechazan sobrescribir evidencia. Python CPU local usado: /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python; OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1. Los originales D0.1 se referencian por hash, no se descargan ni se modifican.
