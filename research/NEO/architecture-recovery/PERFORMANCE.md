# Rendimiento CPU observado

Intel N100, un thread PyTorch, FP32; modelos ~0,28M, no extrapolación a12M/50M. `results/performance.json` contiene36casos: longitudes64/128/256, batch1/4, seis variantes. Dos warmups y cinco updates medidos; next-token LM sobre todos los targets del fixture. Estas cifras **no** son el throughput de la tarea de una respuesta por documento. No se ejecutó GPU.

Caso longitud256, batch4, fragmento32:

| Modelo | Parámetros | Targets/s | ms/update aprox. |
|---|---:|---:|---:|
| B0 local |272.480|6.582,03|154,97|
| B0 contexto completo |272.480|5.648,31|180,59|
| CryoTiny referencia |285.952|1.769,50|576,43|
| Event |281.953|5.796,20|175,98|
| Delta secuencial |276.259|5.247,08|194,39|
| Delta scan denso |276.259|5.183,13|196,79|

Event alcanza3,28× el throughput de CryoTiny en este caso; Delta2,97×. Event queda ~11,9% por debajo deB0local. Cambian atención visible, FFN y parámetros respecto aCryoTiny: esta diferencia no demuestra igualdad de FLOPs ni una victoria en capacidad. El scan afín correcto no mejora este casoCPU; su implementación densa añade trabajo.

## Coste estructural y FLOPs

El foreground se calcula sobre fragmentos independientes en paralelo; las dependencias temporales pasan deT pasos aceil(T/C) escrituras. Continúa existiendo una cadena secuencial por fragmento. Para width d, el bloque activo tiene aproximadamente10d² pesos de proyecciones y ~20Td² FLOPs forward, más atención (~4TCd para bloque local denso; ~4T²d para full) y salida2Tdvocab. Backward/AdamW no se reducen exactamente a una constante universal. La salida a8192IDs domina una parte importante del fixture pequeño.

Event añade resúmenes/lecturas de slots (~4TSd cada una), proyecciones de lectura y señales/candidatos por fragmento. Delta añade estado k×d y actualizaciones densas A@H; no se implementó todavía la forma rank1 O(kd). El scan de referencia añade composiciones densas O(NlogN k³). Estas son aproximaciones analíticas, **no FLOPs medidos**; no existe un control de aprendizaje igualado por FLOPs ejecutado.

## Instrumentación

`results/profiling.json` y trazas ChromeCPU en `results/profiles/`. Event128/b1/chunk32: active2,432ms; resumen0,676ms; cuatro lecturas1,639ms; señales0,352ms; candidato0,341ms. Son regiones instrumentadas parciales/nidificadas; no sumarlas como una descomposición completa del update. Delta: lectura1,949ms; proyecciones de control/clave/valor~0,303ms; las actualizaciones matriciales no están aisladas en esa suma. El profiler tiene overhead y sus tiempos no sustituyen throughput sin profiler.

La biblioteca imprimió un error de enumeración `gpuGetDeviceCount code35` al iniciar profiler, aunque las actividades solicitadas fueron exclusivamenteCPU y todos los tensores permanecieron enCPU. Trazas y operadoresCPU se generaron; no se usó GPU ni se presenta un perfilCUDA.

## Escrituras realmente omitidas

`results/hard-skip.json`: modelo Event sin entrenar,16slots elegibles. Soft ejecuta16candidatos y tarda4,713ms forward mediano. Hard umbral0,5 ejecuta0candidatos, pero tarda5,319ms. Umbral1 también omite16, tarda5,263ms. La selección y el indexado cuestan más que las proyecciones ahorradas en este casoCPU. Es una omisión real de cómputo, **no** una aceleración ni selectividad aprendida; hard cambia la función y solo se admite en inferencia.

RSS en JSON es el pico acumulado del proceso (incluyePyTorch y mediciones anteriores), no memoria aislada de cada modelo. No se midió consumo eléctrico ni tráfico de memoria. No se ejecutó compilación/Triton; el presupuestoGPU de este trabajo es cero.

## Todos los contextos, batch1

| Modelo | 64 targets/s | 128 targets/s | 256 targets/s |
|---|---:|---:|---:|
| b0_local | 3702.24 | 6532.30 | 7609.67 |
| b0_full | 4304.28 | 4426.80 | 6278.91 |
| cryo_history | 590.61 | 621.73 | 623.76 |
| event | 3526.86 | 4857.24 | 5250.77 |
| delta | 3726.92 | 4874.25 | 5938.80 |
| delta_scan | 3519.87 | 4565.41 | 4767.59 |

Máximo RSS acumulado observado en el proceso de estos36casos:1.030.324.224bytes (~983MiB). No representa solo los pesos ni memoria aislada por brazo.
