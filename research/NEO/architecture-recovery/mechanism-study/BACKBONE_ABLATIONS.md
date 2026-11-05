# Ablaciones y atribución

Todos los brazos comparten el embedding8192×32, primer bloque GQA/RoPE/FFN4d y normalización de salida iniciales del histórico por semilla, salvo el control adicional de capacidad que agrega un segundo bloque. Cabezal de salida atado; los targets y órdenes son idénticos. No hay ajuste de receta por brazo.

| Brazo | Cambio respecto a histórico | Parámetros sin uso |
|---|---|---|
| intact | Ninguno; checkpoints originales reproducidos | Ninguno |
| transformer | Elimina cabeza rápida/lenta; conserva foreground y norma final | Fast,slow,gate,read,memory_init,fast_norm congelados |
| no_ice | Mantiene dos refinamientos rápidos; elimina toda lectura/escritura lenta | Slow,gate,read,memory_init congelados |
| no_filter | Gate lento fijado a1; candidato y lectura intactos | Gate congelado |
| depth1 | Un refinamiento rápido en lugar de dos | Ninguno; pesos compartidos, menos aplicaciones |
| event/delta | Cabeza por chunks sobre foreground histórico | Cabeza rápida/lenta original congelada; nueva memoria entrenable |
| detach | Mismo forward, corta BPTT temporal cada token | Memory_init congelado explícitamente; es ablación de receta |
| chunk2 | Actualiza estado cada dos tokens; rápido vectorizado por par | Ninguno |
| capacity_transformer | Dos bloques de atención, FFN4d+2d, sin cabeza recurrente | No mantiene módulos muertos; todos entrenables |
| event_matched/delta_matched | Injerto con inicialización exacta de memoria Event/Delta originales | Igual que injertos; evita confundir foreground con otra inicialización de memoria |

Los totales de `parameters` incluyen módulos congelados retenidos para procedencia de pesos. Para comparar capacidad usar `trainable_parameters`; restar262144 del embedding común para examinar capacidad no léxica. El control de un bloque pierde~13K parámetros activos de cabeza: no se presenta como comparación de capacidad igualada. El control de dos bloques se ajustó antes de entrenarse mediante un test de conteo, no mediante resultados dev.

## Causalidad de la atribución

Una ablación desde inicialización y con entrenamiento igualado puede demostrar que un componente no es necesario en estas condiciones; no prueba que sea inútil en todas las tareas. Quitar un gate cambia también estabilidad y horizonte de gradiente: un fracaso no demuestra selección semántica. El brazo detach no evalúa utilidad del estado quitándolo, sino utilidad del gradiente temporal bajo la misma función forward inicial.

Cambiar foreground incorpora un grupo de diferencias históricas: atención local→completa, RoPE, FFN y escala de inicialización. Incluso con memoria exactamente igualada no separa cada una de esas decisiones. El control B0 full antiguo ya tenía contexto completo y falló: aumentar visibilidad por sí solo no explica todos los resultados. Ningún brazo actual certifica retención más allá de una ventana de atención, porque el foreground histórico ve el prefijo completo.

## Reducción exacta de no_ice en esta tarea

Al no existir estado temporal y aplicarse loss solo al último token, los refinamientos rápidos de posiciones anteriores no contribuyen al target. `query_head.answer_only` obtiene exactamente el mismo logit final y gradientes usando solamente el último hidden del foreground. Los tests verifican esa equivalencia. Por ello un buen resultado no_ice demuestra suficiencia de un readout no lineal normalizado sobre atención causal completa; no demuestra memoria recurrente aprendida. Esta reducción es exclusiva del diagnóstico answer-only y no se aplica a un LM con loss denso ni al modelo con Hielo.

## Injertos que conservan el readout rápido

EventFast/DeltaFast mantienen dos pasos fast, RMSNorm, read y foreground históricos. Sustituyen slow/gate/memory_init por edición por chunk8; esos módulos viejos quedan congelados. Se igualan pesos de memoria con Event/Delta originales. Cambian simultáneamente la forma del estado, regla/frecuencia de escritura y fuente del resumen (ahora fast); no se llaman ablación de una sola ecuación. Ver HYBRID_DESIGN.md y todos los resultados de tres semillas.
