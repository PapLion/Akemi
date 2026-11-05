# Language Memory Bridge V2 — ejecución cerrada por compuerta

Rama `cryo-language-memory-v2`, origen `485f552`. Trapos OFF. Hielo, Delta, reader, foreground y NeoTokenV3 sin cambios. Implementación importada directamente desde language-bridge/model.py, sin copia modificada.

**No se demuestra ni se refuta recuperación lingüística de Hielo. Falló antes el control positivo de contexto completo.**

| Ejecución | Estado | Resultado |
|---|---|---|
| Contratos del entrenador | PASS |7 pruebas CPU |
| Contratos de estados/intervenciones | PASS |5 pruebas CPU |
| Memoria exacta oracular | PASS diagnóstico |100% en los paneles generados |
| Reader lineal sobre valor explícito | PASS diagnóstico |100%,100updates,20parámetros |
| Microfit de foreground con contexto completo | FAIL |200updates;16/32 respuestas,3/16 relatos con ambas correctas; CE1.04552 |
| Contraste principal A/B/C400updates | NO EJECUTADO |Bloqueado por el microfit preregistrado |
| Semillas29/43 | NO EJECUTADAS |No se habilitaron |
| Confirmatorio nuevo | SELLADO |1024 ejemplos, nunca evaluados |

Datos controlados:2048 ejemplos train,1024 dev combinaciones y2048 dev estructuras; dos consultas por programa, todos sintéticos de código, no lenguaje natural abierto. Una respuesta = un token real V3; la exactitud usa argmax de8192 IDs, no selección forzada entre colores. La pérdida es exclusivamente de respuesta, no pretraining ni SFT general.

Guardar el negativo es parte del protocolo. No aumentar automáticamente updates, dimensiones ni modificar Hielo/Trapos/tokenizer. Ver DECISION.md. No GPU, Vast.ai, Chinchilla ni evaluaciones selladas históricas. Código, curvas, predicciones y controles en esta carpeta; .pt locales y datos grandes se conservan fuera de git, con hashes.

## Reproducir

Solo contratos (sin entrenamiento principal; los tests incluyen updates diminutos de ingeniería):
```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python memory-bridge/intervention_tests.py
```
Las7 pruebas conservan engineering.json y verifican su identidad al repetir; para reproducir todo, usar salida NUEVA:
```bash
bash memory-bridge/reproduce.sh /PATH/TO/NEO_HOME/research/neo-architecture-recovery/language-memory-reproduction-NEW
```
Rechaza directorios existentes. Reutiliza Python3.11/Torch y el backend V3 local; sin instalaciones ni descargas. El código respeta la compuerta del microfit, nunca fuerza el contraste principal. La auditoría V1 requiere el checkpoint local `../cryo-language-bridge-v1/language-bridge/results/ice-final.pt`; no se modifica.

SHA256SUMS verifica resultados/código/datos locales excepto el cuerpo sellado; su hash se produjo durante la escritura sin releer contenido. ARTIFACT_MANIFEST.json registra identidad y localización. La receta/cuerpo confirmatorio no deben utilizarse para ajustar la siguiente intervención.
