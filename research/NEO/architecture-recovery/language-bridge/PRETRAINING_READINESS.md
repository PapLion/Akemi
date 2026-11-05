# Compuertas

| Compuerta | Estado demostrado |
|---|---|
| V3 real reversible, IDs explícitos | PASS local/provisional BPE8K |
| Procedencia/licencias | PARTIAL: avisos archivados, derechos individuales OASST no certificados |
| Separación train/dev | PASS exactos/grupos/12palabras en panel; no certificación universal |
| LM causal/máscaras/shift/padding | PASS CPU FP32 |
| AdamW, gradientes y updates | PASS tres brazos |
| Checkpoint/RNG/cursor/orden/reanudación | PASS CPU monoproceso,8updates, sin AMP |
| Generación incremental y sesión | PASS técnica; texto degenerado |
| Baseline local sin Hielo | PASS ejecutado con datos idénticos |
| Tokens/s/RAM | PASS medido; RSS pico acumulado |
| Política de escritura | Documentada/causal; semántica no validada |
| Ventaja funcional en texto distante | FAIL/NO DEMOSTRADA25% |
| Datos suficientes y diversos para pretraining | BLOCKED; sin usar Chinchilla |
| Trapos aprendido | OFF/congelado, no desbloqueado |
| Entrenamiento significativo | NO AUTORIZADO por esta fase; no preparado científicamente |

El puente permite seguir investigación lingüística con modelos pequeños y presupuestos nuevos. Antes de pretraining: cerrar corpus/licencias/dedup/tokenización exacta por su vía independiente, comprobar direccionamiento y recuperación de lenguaje con entrenamiento/evaluación emparejados y exposición suficiente, estimar presupuesto real del tamaño seleccionado, ampliar confirmación y cubrir precisión/hardware que se pretenda usar. No es necesario reabrir Trapos para ello. Ningún certificado de símbolo/CPU se transforma en certificado de lenguaje/GPU.
