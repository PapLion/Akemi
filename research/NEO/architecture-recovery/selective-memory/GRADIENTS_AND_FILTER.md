# Gradientes, estado y filtro

Probe diagnóstico sin updates sobre8ejemplos fuera de ventana fijos (dos por replace/multiple/discard/goal). IDs y top5 de salida antes/después en results/gradient-horizons.json. Normas de gradiente son del batch y dependen de dimensión/posición; no comparar absolutos entre arquitecturas como calidad de aprendizaje.

|Checkpoint|Gate medio inicial→final|Fracción final <0.05|Gradiente primer estado|Gradiente penúltimo estado|
|---|---:|---:|---:|---:|
|delta_fast-normal-w16-17.pt|0.4995→0.1151|0.5776|0.296723|0.970916|
|delta_fast-normal-w16-29.pt|0.4931→0.2425|0.0536|0.162399|0.286365|
|delta_fast-normal-w16-43.pt|0.4898→0.1443|0.2712|0.661638|0.908279|
|event_fast-normal-w16-17.pt|0.5018→0.1304|0.6207|0.0555347|0.542382|
|event_fast-normal-w16-29.pt|0.5010→0.3594|0.1768|0.0215772|0.203734|
|event_fast-normal-w16-43.pt|0.5000→0.2012|0.4323|0.107584|0.533755|
|intact-normal-w16-17.pt|0.4994→0.1332|0.5836|0.0773242|0.280425|
|intact-normal-w16-29.pt|0.4988→0.2778|0.0948|7.7371e-06|0.203726|
|intact-normal-w16-43.pt|0.4996→0.2667|0.1410|0.000548676|0.189347|

Los nueve probes tienen gradientes finitos, incluidos parámetros de compuerta/control. La conexión atraviesa fragmentos y los estados cambian; no hay un fallo universal de gradiente ausente que explique el resultado. El último estado híbrido queda sin gradiente porque su escritura ocurre después de la última respuesta: es esperado, no un parámetro huérfano.

El histórico muestra horizontes muy diferentes entre semillas; por ejemplo, su primer estado tiene norma7,7e-6 en seed29 frente a0,077 en seed17. Es una observación compatible con atenuación variable, no una prueba de que eso cause el fracaso. Los híbridos mantienen gradientes tempranos medibles y también fallan en edición de valores: no basta atribuirlo todo a desaparición de gradiente.

Gates finales más pequeños y diferencias entre actualizaciones aceptadas/propuestas muestran adaptación de parámetros, no selección útil de VALORES. El control de presencia sin valores alcanza53,33% en IID/estructural fuera y explica por qué una mejora de exactitud sobre noHielo no certifica binding. La representación interna exacta no se ha identificado; se propone un probe de contenido antes de otro rediseño.
