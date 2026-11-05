# Resultados de aprendizaje CPU

Todos los brazos y semillas; último checkpoint fijado. No selección de mejores casos. Exactitud = argmax sobre 8.192 IDs. SD entre tres semillas no es intervalo de confianza poblacional.

## learning

| Brazo | Semillas | Dev % ± SD | Train % | NLL dev | s entrenamiento/semilla |
|---|---:|---:|---:|---:|---:|
| b0_local | 3 | 0.30 ± 0.52 | 18.90 | 2.491 | 1.23 |
| b0_full | 3 | 12.05 ± 1.18 | 12.57 | 2.138 | 2.63 |
| cryo_history | 3 | 12.35 ± 1.12 | 12.72 | 2.140 | 14.96 |
| event | 3 | 0.30 ± 0.52 | 19.35 | 2.487 | 2.62 |
| delta | 3 | 0.15 ± 0.26 | 19.20 | 2.482 | 2.19 |
| event_no_memory | 3 | 0.30 ± 0.52 | 18.90 | 2.491 | 1.15 |
| event_no_filter | 3 | 0.15 ± 0.26 | 18.30 | 2.492 | 2.18 |
| event_always_write | 3 | 0.30 ± 0.52 | 19.05 | 2.488 | 2.43 |
| event_no_persist | 3 | 0.30 ± 0.52 | 18.90 | 2.491 | 2.33 |
| delta_no_persist | 3 | 0.30 ± 0.52 | 18.90 | 2.491 | 2.25 |

## learning-1000

| Brazo | Semillas | Dev % ± SD | Train % | NLL dev | s entrenamiento/semilla |
|---|---:|---:|---:|---:|---:|
| b0_local | 3 | 0.00 ± 0.00 | 29.84 | 4.881 | 11.53 |
| b0_full | 3 | 0.00 ± 0.00 | 31.55 | 4.551 | 26.34 |
| cryo_history | 3 | 60.12 ± 10.53 | 75.37 | 1.563 | 146.85 |
| event | 3 | 0.00 ± 0.00 | 44.87 | 5.454 | 24.49 |
| delta | 3 | 0.00 ± 0.00 | 36.98 | 5.030 | 21.78 |
| event_no_memory | 3 | 0.00 ± 0.00 | 29.84 | 4.881 | 11.26 |
| event_no_filter | 3 | 0.00 ± 0.00 | 41.37 | 5.064 | 20.97 |
| event_always_write | 3 | 0.00 ± 0.00 | 38.10 | 5.014 | 24.15 |
| event_no_persist | 3 | 0.00 ± 0.00 | 29.84 | 4.881 | 22.33 |
| delta_no_persist | 3 | 0.00 ± 0.00 | 29.84 | 4.881 | 20.29 |

## Alcance e interpretación

448 documentos train y 224 dev; siete tareas de un DSL con oráculo ejecutable. Cada documento tiene 64 IDs y una sola respuesta supervisada. El primer ensayo consumió 800 targets por brazo/semilla; la extensión exploratoria, 8.000, repitiendo el mismo train. No son 8.000 documentos distintos. Panel, predicciones completas y pérdidas por update permanecen en results/.

La partición exige combinaciones entidad/valor consultadas y estructuras nuevas. Los valores siguen presentes incidentalmente en contexto train. Es un test composicional exigente y artificial, no una evaluación de español/inglés. Una baja loss de train no acredita retención generalizable. El 12,5% es la referencia de escoger uniformemente entre ocho valores, no el azar uniforme entre 8.192 IDs.

La extensión se decidió después de ver el fracaso inicial, se fijó en EXTENSION_PROTOCOL.md y mantuvo los diez brazos, tres semillas, datos y optimizador. No es una confirmación preregistrada desde el primer ensayo. No se ejecuta una tercera extensión automática.

Ver results/task-summary.csv para todas las tareas, results/*-probes para contrafactuales de la extensión y resultados iniciales en results/counterfactual-results.json. Cambiar una predicción tras editar un hecho no basta: se exige acertar ambas respuestas.
