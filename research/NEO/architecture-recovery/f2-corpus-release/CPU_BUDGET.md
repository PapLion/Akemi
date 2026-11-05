# Presupuesto reutilizado, sin repetir benchmark

Contexto128, batch2, CPU FP32. F2: 1625.28 targets/s; Transformer: 1748.84 targets/s. Fuentes: corpus-recovery-f2/results/f2-benchmark-isolated.json.

5M por modelo: F2 0.855 h de cómputo, Transformer 0.794 h. Con reserva global del30%: F2 1.111 h, Transformer 1.032 h. Reserva no medida específicamente para evaluación; no se disfraza como coste validado del pipeline completo. RAM histórica alrededor de814/825MiB por proceso; sin nueva medición de entrenamiento completo.

Checkpoint histórico F2: escritura 0.0209s, restauración 0.0590s. Evaluación completa, frecuencia de checkpoints y lectura escalada: CONDITIONAL, necesitan parametrizarse con release aprobado. Conteo/preparación de esta selección se midieron aparte; no se añaden al throughput de entrenamiento. Lector pequeño: results/reader-contracts.json.

Alquiler efectuado: USD0. Electricidad/uso del equipo no tarifados. No hay presupuesto GPU ni autorización de entrenamiento. Estas mediciones del equipo son estimaciones de planificación, no SLA.
