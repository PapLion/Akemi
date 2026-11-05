# Contratos ejecutados

`results/all-tests.log` registra la suite nueva; `original-tests.log` conserva los22tests originales. Los tests cubren referencia histórica exacta; causalidad train/eval; reinicios por documentos y separación de batch; equivalencia chunk1 con logits,gradientes y tres updates; prefijos impares chunk2; BPTT cruzando pares; gradientes finitos y no nulos en fixtures; parámetros actualizados; cobertura única AdamW; carga segura tras dos updates y trayectoria exacta de parámetros en el update posterior. También inicializaciones de foreground y memoria igualadas, equivalencia de ecuaciones Event/Delta para hidden idéntico y reducción del no_ice al readout de consulta.

CPU FP32,sin dropout. Tolerancias fijadas antes de ejecución: logits atol2e-5/rtol2e-4,gradientes atol3e-6/rtol2e-3; referencia intacta y resume misma ruta CPU exactos. No se certifican CUDA,BF16,AMP,multiproceso ni continuación de estados por API externa. No se afirma utilidad científica por pasar contratos.

El fixture de gradientes usa longitud16. `gradient_audit.py` añade mediciones al contexto64 real, inicial y final, por tensor: presencia,finitud,norma,número de elementos no nulos y cambio respecto a inicialización. Una norma global finita no garantiza crédito a todos los horizontes.

## Fallos preservados

- `variants-red.log`: import falló antes de existir variantes; contratos escritos primero.
- `capacity-red.log`: control preliminar excedía la banda de parámetros prevista. Se cambió el FFN del segundo bloque antes de entrenar; no se relajó el test ni se escogió arquitectura por dev.
- Warning al convertir loss a float: logging CPU, no hay GPU ni sincronización CUDA. No afecta el grafo usado por backward; se conserva el log.
- El contador y runner publican JSON final tras guardar checkpoint; la continuación automática solo omite brazos finalizados. No se promete recuperación a mitad de un brazo ante apagado.

## Estados y gradientes históricos

`state-diagnostics.json` usa siete ejemplos dev fijos (uno por tarea) y tres semillas, antes/después del entrenamiento histórico. Mide gates, norma del estado y gradientes de loss final respecto a estados/hidden por posición. Es una observación local de sensibilidad, no una prueba de selectividad semántica. La señal a estados tempranos cambia de aproximadamente1e-19 inicialmente a0.00059–0.0193 después de aprender. Ese aumento no demuestra que la vía sea necesaria: la ablación no_ice lo comprueba por separado.

## Cierre de los contratos

La suite ampliada contiene19tests nuevos; se reejecuta también la suite histórica de22tests. `final-tests.log` y `final-original-tests.log` conservan la verificación final. Se cubren gradientes desde prefijo sin dependencia futura, padding que reinicia estado, equivalencia del optimizador completo y resume con batches cambiantes, RNG de sampler/cursor y clipping, además del resto de contratos.

La auditoría del contexto64 real contiene1434mediciones por tensor/semilla/etapa: ningún gradiente ausente ni no finito. Tres mediciones iniciales de memory_init del brazo no_filter tienen norma0 (horizonte/underflow FP32); no se oculta como gradiente útil a largo plazo. Los fixtures cortos sí acreditan conexión diferenciable. En no_ice las columnas rápidas del argumento de memoria son inútiles y su gradiente es cero; el tensor fast participa parcialmente. Decay puede mover entradas sin gradiente de datos: un cambio de peso no basta para demostrar aprendizaje de cada entrada. Los módulos completos sin uso se congelan explícitamente.
