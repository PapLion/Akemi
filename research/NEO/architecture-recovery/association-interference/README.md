# Interferencia multientidad — CPU FP32

Origen f417526. DeltaFast semilla17 inmutable; ningún cambio arquitectónico. Cuatro entrenamientos de150updates, no brazos de600. Evidencia anterior intacta.

|Condición|Aux train|CE|Respuesta original|Aux layout nuevo|Respuesta layout|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|A|45.59%|1.2182|99.22%|40.90%|67.50%|22.0|
|B|56.48%|1.0504|28.91%|51.21%|30.00%|22.0|
|C|54.26%|1.0540|41.09%|30.43%|25.62%|26.5|
|D|52.38%|1.0484|25.00%|38.28%|25.00%|24.8|

Reproducción: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python interference_runner.py`, después `analyze.py` y `report.py`, desde este directorio. El ejecutor rechaza un directorio results existente; archivar/copiar el directorio de ejecución antes de repetir. No lee finales sellados.
