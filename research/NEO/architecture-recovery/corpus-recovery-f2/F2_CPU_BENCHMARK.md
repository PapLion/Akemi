# Benchmark CPU técnico real

| Modelo | Contexto | Targets/s | Update ms | SD ms | Save s | Restore s | 5M h cómputo | h+30%reserva |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F2 | 128 | 1625.3 | 156.28 | 2.98 | 0.021 | 0.059 | 0.855 | 1.111 |
| F2 | 256 | 1726.3 | 295.42 | 5.7 | 0.02 | 0.055 | 0.805 | 1.046 |
| Transformer | 128 | 1748.8 | 145.24 | 3.61 | 0.018 | 0.048 | 0.794 | 1.032 |
| Transformer | 256 | 1845.9 | 276.29 | 3.03 | 0.018 | 0.046 | 0.752 | 0.978 |

IntelN100,CPU FP32,1thread,batch2,2warmup+5updates medidos porcaso. Medición final realizada después de terminar el escaneo del corpus; pase inicial concurrente conservado en`f2-benchmark.json`, no usado para presupuesto final. Resultados porupdate, forward/backward/AdamW+clipping: [benchmark](results/f2-benchmark-isolated.json). FixtureIDs sintéticos, sinI/O/tokenización de corpus en la medida. Variabilidad de solo5updates no caracteriza rendimiento largo.

RAM pico proceso (incluye construir/guardar/restaurar modelos): [('F2', 813.8), ('Transformer', 825.5)]MiB. No esRAM incremental exacta por modelo ni límite de un job largo. Checkpoint contiene modelo,AdamW,RNG,cursor,protocolo/hashfuente.

Coste contratadoCPU:USD0, ningún servicio facturable. Electricidad/amortización no medidas: si potenciaPwatts y tarifaRUSD/kWh, coste=horas×P/1000×R. Dos brazos requieren sumar tiempos;30% es una reserva de planificación, no medición de evaluación/I/O ni garantía. No extrapolación desde296K, ni resultadoGPU. Estos son benchmarks, no5Mtargets entrenados.
