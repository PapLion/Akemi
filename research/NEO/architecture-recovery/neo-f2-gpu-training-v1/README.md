# NEO — primer entrenamiento F2 en GPU

F2 y Transformer comparable completaron **4,922,444 targets cada uno**, semilla 17, CPU de referencia y entrenamiento CUDA FP32 en una RTX 3090. Hielo y Trapos permanecieron OFF.

| Modelo | Parámetros | NLL dev | PPL dev | Targets/s de updates |
|---|---:|---:|---:|---:|
| F2 | 2,082,176 | 5.559083 | 259.585 | 4083.95 |
| Transformer | 2,032,768 | 5.287873 | 197.922 | 4315.55 |

El baseline obtuvo mejor validación y rendimiento en este único ensayo. Las generaciones F2 son muy repetitivas; completar el entrenamiento no demuestra competencia conversacional.

- [Decisión](DECISION.md), [validación por idioma](EVALUATION.md), [generaciones sin selección estética](GENERATIONS.md).
- [Configuración y uso privado de datos](TRAINING_CONFIG.md), [entorno y reparaciones operativas](GPU_ENVIRONMENT.md).
- [Rendimiento](GPU_PERFORMANCE.md), [comparación](BASELINE_COMPARISON.md), [coste y cierre](COST_REPORT.md).
- [Curvas](results/learning-curves.svg); CSV por grupos de 100 updates en results/. Curvas completas fuera de Git.

Checkpoints completos locales: `private/download/results/F2/final.pt` y `private/download/results/Transformer/final.pt`. Cada carpeta contiene también checkpoints periódicos, latest.pt, curvas y generaciones. Cargas CPU, inferencia y SHA-256 verificados. `results/artifact-hashes.json` conserva los hashes de todos los artefactos descargados; `SHA256SUMS.json`, los del código e informes.

GPU destruida y ausencia de instancias/volúmenes confirmada. Descenso de crédito observado: USD 0.15979852; pueden existir ajustes pendientes. No se publican corpus ni pesos. La clasificación histórica CONDITIONAL se preserva; el uso privado específico y sus límites están documentados, sin aprobación general de redistribución.
