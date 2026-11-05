# Addressable V1.1 — consolidación por datos

Arquitectura Addressable V1 conservada byte a byte. Experimento ejecutado: control original A frente a50% de correcciones B,300updates por brazo,semilla17; gate prospectivo aprobado y confirmaciones emparejadas29/43 completadas. Diagnóstico de posiciones separado; resultados y límites en DECISION.md.

Todo el trabajo está en esta carpeta y rama cryo-addressable-consolidation-v1, origen7d203aa. Ningún checkpoint original, tokenizer, corpus o evaluación histórica sellada modificado. Sin GPU ni gastos. La nueva familia confirmatoria permanece sellada y sin evaluación de modelos.

```bash
PY=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" addressable/test_contracts.py
"$PY" addressable-consolidation/test_data_contracts.py
# Solo en copia nueva de la rama, sin resultados de esta ejecución:
"$PY" addressable-consolidation/preflight.py
"$PY" addressable-consolidation/launch.py
# Si se conserva el launcher inicial que falló en un informe:
"$PY" addressable-consolidation/continue_diagnostics.py
"$PY" addressable-consolidation/position_invariance.py
"$PY" addressable-consolidation/final_checks.py
"$PY" addressable-consolidation/write_reports.py
```

No borrar evidencia para repetir: usar otro worktree y excluir results/ y confirmatory/ del nuevo destino. Los entrenadores rehúsan sobrescribir un checkpoint final. Los.pt locales están ignorados por Git; SHA256SUMS identifica los artefactos necesarios. Fuente histórica cargada con weights_only=True y strict=True. README de V1 conserva ubicación del entorno y dependencias.
