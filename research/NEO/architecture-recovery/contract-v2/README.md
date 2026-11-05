# Trapos V2 — contrato de objetivo, conservación y consulta

Continuación aislada desde 23cb2d7. Modelo byte a byte idéntico a V1. Intervención única: distribución de programas y consultas. CPU FP32, un thread, 300 updates máximo por brazo A/C; semilla17. No se accede a corpus, tokenizer, A4, GPU ni evaluaciones selladas.

Contrato y diseño preregistrados: SELECTION_SEMANTICS.md y protocolo generado antes de entrenar. Resultados se agregarán únicamente tras ejecutar. Los criterios exigen precisión/recall95%, respuesta95%, conservación95%, conjunta90%, ventaja5pp sobre A y controles aleatorio/confirmación, contrafactuales90% y escenario limpio sin caída>5pp. Si falla el piloto, no hay confirmación29/43 ni búsqueda posterior.

Los controles de políticas en el mismo C son intervenciones diagnósticas, no entrenamientos emparejados de esas políticas. No permiten atribuir toda diferencia de A/C únicamente al filtro: C tiene BCE adicional0,1.

## Ejecución cerrada

Estado del piloto: FAIL; Trapos congelado, sin más semillas. Evidencia y límites en DECISION.md, resultados en results/summary.csv. Modelo original y resultados V1 preservados.

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
# En copia NUEVA: preflight y train rehúsan sobrescribir evidencia.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/preflight.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/v1_diagnostics.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/trapos_train.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/final_checks.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY" contract-v2/make_reports.py
```
Los checkpoints locales ignorados por git permanecen en results y están hasheados en SHA256SUMS.
