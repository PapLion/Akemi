# CryoCCM — Language Bridge V1

Implementado y ejecutado en CPU FP32, rama `cryo-language-bridge-v1`, base `1841b99`; evidencia de Addressable estable `5f2a166`. Trapos aprendido OFF. Modelo pequeño, inicialización nueva: no se migraron pesos simbólicos ni históricos.

**Puente autoregresivo operativo; utilidad lingüística de Hielo no demostrada; pretraining significativo bloqueado.**

| Brazo | Parámetros activos | NLL train real inicial → final | NLL dev real inicial → final | Targets/s | Tiempo 64 updates |
|---|---:|---:|---:|---:|---:|
| no_ice | 280,736 | 8.9912 → 5.9867 | 8.9776 → 7.2575 | 2013.9 | 6.225s |
| ice | 284,096 | 8.9912 → 5.9912 | 8.9776 → 7.1039 | 1838.3 | 6.820s |
| transformer | 277,600 | 8.9901 → 6.0290 | 8.9732 → 8.0506 | 3490.7 | 3.592s |


16 tests únicos PASS (`results/release-tests.log`), tres smoke tests de 64 updates/semilla17 y 12.537 targets expuestos por brazo. Sin GPU, Chinchilla, servicios pagos ni evaluaciones selladas. Generación técnica válida pero repetitiva: los seis prompts fijos producen 24 puntos. La pérdida no demuestra comprensión.

Leer LANGUAGE_ADAPTER.md: sustitución explícita del contrato de eventos DSL por escrituras deterministas de frontera, y consultas por token. No es un extractor semántico. MEMORY_EVALUATION.md registra 25% en cuatro opciones para todos, sin ventaja de Hielo.

## Ejecutar

Desde este worktree, verificación sin entrenar:
```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python language-bridge/extra_tests.py
sha256sum -c language-bridge/SHA256SUMS
```
Reproducción completa exclusivamente en salida nueva (otros ~17s de entrenamiento, más tests/evaluación):
```bash
bash language-bridge/reproduce.sh /PATH/TO/NEO_HOME/research/neo-architecture-recovery/language-bridge-reproduction-NEW
```
El script rechaza directorios existentes; los checkpoints originales nunca se sobrescriben. Reutiliza los entornos locales Python3.11/Torch y V3 tokenizers0.23.3/regex2026.9.29, sin instalar paquetes ni modificar V3. La identidad está en results/summary.json y SHA256SUMS. Texto local de fuentes en results/data.json, deliberadamente ignorado por git; se reconstruye desde fuentes D0.1 ya adquiridas y hashes, sin nueva descarga.

Artefactos: model.py; engine.py; build_data.py; evaluation.py; tests.py/extra_tests.py; results/*-final.pt (locales, carga weights_only); curvas.csv; generaciones con bytes exactos; manifests de fuentes/licencias/tokenizer y métricas por idioma/dominio. Resultados negativos conservados. No se autoriza automáticamente un siguiente entrenamiento.
