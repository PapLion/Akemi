# Modificación mínima: Chunk2

Se conserva el foreground histórico completo, embeddings, cabeza atada, dos refinamientos rápidos, gates, candidato lento y normalizaciones. Solo se cambia la frecuencia/orden de actualización lenta a pares completos de tokens dentro de cada documento.

Para cada par y estado previo s:

```
f_i^0 = x_i
f_i^(k+1) = RMS(f_i^k + tanh(W_f[f_i^k,x_i,R s])) ; k=0,1
z = [s,f_último^2]
g = sigmoid(W_g z)
s_nuevo = (1-g)s + g tanh(W_s z)
h_i = f_i^2 + R s                    ; token interior
h_último = f_último^2 + R s_nuevo     ; frontera completa
```

Un par parcial nunca se cierra anticipadamente. La escritura de su último token, que podría conocer el final del prefijo recibido, no se usa para cambiar salidas anteriores. Los índices se reinician por documento, no por offset físico del packing. Se conserva BPTT entre pares. Las dos posiciones rápidas se procesan juntas con el mismo estado previo; no se supone que sean temporalmente independientes bajo las ecuaciones originales. Esta es una variante arquitectónica, no una optimización numéricamente equivalente al histórico para chunk2.

Con chunk1 se recuperan logits, gradientes y trayectoria de tres updates de referencia dentro de tolerancias fijadas; se prueban padding y fronteras arbitrarias. Con chunk2 se prueban causalidad train/eval, prefijos impares, gradientes cruzando pares, aislamiento y resume. El método compartido `_plans` solo organiza metadatos; no se copia ninguna biblioteca externa.

Esta propuesta no incluye ACT, scan temporal ni salto de escrituras aprendido. Reduce de64a32 actualizaciones lentas por programa y de128a64 invocaciones rápidas vectorizadas; los FLOPs rápidos no se reducen a la mitad. Hielo permanece compacto/editable y Trapos conserva su gate entrenable. La calidad nueva debe medirse antes de promoverla.

## Event y Delta sobre foreground histórico

Se conserva todo el foreground, embeddings y normalización final históricos. Solo se sustituye la cabeza recurrente por lectura y escritura Event/Delta ya definidas en `models.py`, con chunk8 y sin nueva atención ni posición añadida. Resúmenes se calculan sobre representaciones históricas causales; la escritura del chunk actual solo afecta chunks posteriores. Cambian tamaño/forma del estado y parametrización de memoria: son reemplazos de cabeza, no cambios de una sola ecuación. Los módulos históricos no usados se congelan explícitamente y excluyen de AdamW. Todos los módulos nuevos deben tener gradientes no nulos.

## Candidato posterior EventFast/DeltaFast

Tras cerrar la matriz principal, se conserva explícitamente el procesamiento rápido que demostró suficiencia en no_ice. En cada chunk8:

1. Foreground histórico causal `x`.
2. Recuperación Event/Delta desde memoria anterior, proyectada por el `read` histórico.
3. Dos refinamientos rápidos históricos por token, con esa lectura como tercer argumento y RMSNorm histórica.
4. Salida normalizada de rápido+lectura.
5. Resumen del rápido, edición Event/Delta; solo chunks posteriores reciben ese estado.

La fase rápida se vectoriza sobre tokens de un chunk porque utiliza la misma memoria anterior, aunque las lecturas consultadas por cada token sean distintas. No se paraleliza una dependencia temporal existente: se cambia explícitamente la regla de memoria. Estado, gates y resúmenes reciben BPTT. Pesos originales de memoria Event/Delta y pesos rápidos históricos se conservan en la inicialización. Se congela únicamente la vieja actualización lenta/gate/memory_init sustituida.

Es una intervención secuencial fundamentada en no_ice, no una prueba confirmatoria independiente ni un resultado seleccionado entre arquitecturas infinitas. Retiene estado Hielo compacto y filtrado Trapos, pero todas las escrituras soft se ejecutan: no hay ahorro de cómputo por gates cercanos a cero. No certifica streaming externo ni que memoria dé ventaja fuera de la ventana local. La comparación de aprendizaje y coste decide si merece más estudio.
