# Coste CPU medido

| Brazo | Parámetros activos | NLL train real inicial → final | NLL dev real inicial → final | Targets/s | Tiempo 64 updates |
|---|---:|---:|---:|---:|---:|
| no_ice | 280,736 | 8.9912 → 5.9867 | 8.9776 → 7.2575 | 2013.9 | 6.225s |
| ice | 284,096 | 8.9912 → 5.9912 | 8.9776 → 7.1039 | 1838.3 | 6.820s |
| transformer | 277,600 | 8.9901 → 6.0290 | 8.9732 → 8.0506 | 3490.7 | 3.592s |


Hielo aumenta tiempo total de training 9.6% frente al mismo foreground sin Hielo, y reduce throughput 8.7%. Asignados284096 parámetros en todos; activos280736/284096/277600. Diferencia A/B3360 parámetros activos; embeddings ligados8192×32=262144 dominan el tamaño. No se afirma igualdad de FLOPs.

Promedios/stdev de update y tiempos completos en summary.json. Medición end-to-end incluye construcción local de batches fuera de la curva del update, con128 ventanas en64updates; no profiler. RSS pico del proceso secuencial713.8–715.3MiB es high-water acumulado, no asignación incremental por brazo. Hielo persistente256float32=1024bytes por sesión, además del prefijo local pendiente y activaciones para backward.

Estimación estructural: lectura H y proyecciones cuestan aproximadamente2L(8×32+32×32+32×32) operaciones multiply/add, más2L×32×8 para direcciones y coste de norma; una escritura cada16tokens añade proyección32×32 y Delta rank1. Excluye activaciones, backward, layout y overhead Python: no es medición de FLOPs completos. Atención C usa longitud hasta128 en train y contexto completo mayor en diagnóstico, frente bloques16 de A/B.

Proyección puramente mecánica de100k targets al throughput observado: sinHielo49.7s, Hielo54.4s, Transformer28.6s. No autoriza entrenar ni predice un modelo12M/50M/GPU. Repeticiones, dataset, longitud y evaluación cambian el coste. No hubo GPU, mixed precision ni benchmark CUDA; generación recalcula prefijo de chunk y aún no está optimizada.
