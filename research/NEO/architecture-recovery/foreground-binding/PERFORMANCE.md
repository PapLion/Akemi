# Coste CPU

|Brazo|Parámetros totales/activos|Segundos train|Respuestas/s|IDs entrada/s|RAM pico proceso MiB|FLOPs forward estimados/secuencia|
|---|---:|---:|---:|---:|---:|---:|
|A|284096/280736|7.956|402.22|47864.58|699.03|8126464|
|B|299520/296160|12.312|259.91|30929.27|706.05|14155776|
|C|299552/296192|10.053|318.31|37879.41|713.88|12083200|

Timing de entrenamiento sin profiler; incluye instrumentación de gradientes, no setup ni evaluación. IDs de entrada procesados no equivalen a targets: un target supervisado por respuesta,119 IDs válidos por ejemplo train. RAM es high-water del proceso compartido secuencial, no pico aislado comparable por modelo. No se midió energía ni rendimiento GPU.

FLOPs analíticos incluyen lineales/atención/refinamiento/head último token; excluyen normalizaciones, activaciones, softmax, RoPE, optimizer y clipping. Backward3×forward es heurística, no perfil medido. B tiene74,2% más forward estimado que A y17,2% más que C. Más parámetros o FLOPs no consiguieron binding fiable. Costes por ID medidos están en training.json; no extrapolar a pretraining grande.
