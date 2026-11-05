# Coste medido CPU

{
  "same": {
    "training_seconds": 10.685808500998974,
    "updates_per_second": 14.037309388987936,
    "ids_per_second": 7187.102407161823,
    "response_targets_per_second": 112.29847511190349
  },
  "separate": {
    "training_seconds": 10.707800431999203,
    "updates_per_second": 14.008479234609176,
    "ids_per_second": 7172.341368119898,
    "response_targets_per_second": 112.06783387687341
  }
}

Tiempos wall de150updates, excluyen control positivo, certificación, evaluación y exportación. IDs incluyen tokens sin target de respuesta; cada secuencia tiene1target de respuesta y2auxiliares. No se confunden IDs/s y targets/s. Mismo número de parámetros,8actualizaciones densas y misma política de gradiente. No hay medición detallada de FLOPs, RAM pico ni perfil de kernels; no se inventa ventaja computacional por estas diferencias pequeñas de tiempo. Sin costes facturables.
