# Cierre de esta línea de microfits

|Condición / split|Entidad A|Entidad B|Conjunta|Producto marginales|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|---:|
|same / train|25.00%|25.00%|6.25%|6.25%|1.3857|1.3900|25.00%|
|same / dev|25.00%|25.00%|6.25%|6.25%|1.3861|1.3902|25.00%|
|separate / train|53.12%|52.50%|21.88%|27.89%|1.2257|1.2134|30.00%|
|separate / dev|52.50%|50.62%|20.62%|26.58%|1.2422|1.2304|30.00%|

**Separar escrituras ayuda en esta semilla, pero ninguno aprende bindings robustos.** Same queda en priors constantes; separate obtiene señal parcial transferible al layout desplazado. La prueba fuerte de valores intercambiados falla0/120 en ambos. No afirmar compresión como causa única: también cambian posición, recuperación intermedia y propagación de gradientes. Una confirmación independiente sería necesaria antes de establecer la ventaja de separación.

Se cierra explícitamente la búsqueda de microfits equivalentes con150updates y la receta actual. No ejecutar más posiciones, seeds o más updates automáticamente para perseguir un PASS. Tampoco se concluye incapacidad representacional absoluta ni se descarta un cuello de optimización/readout. El control explícito100% valida el protocolo y una representación alternativa, no certifica toda representación latente.

**Siguiente cambio arquitectónico recomendado, no implementado:** preservar reglas Delta, almacenamiento y lector, pero sustituir la única proyección clave–valor obtenida de un resumen global del chunk por múltiples candidatos clave–valor aprendidos antes de esa reducción, con presupuesto pequeño y fijo (por ejemplo2). No incorporar etiquetas/oráculos al forward; las entidades son entradas, no índices mágicos de slots. Es una intervención aislada sobre representación de escritura; no cambiar a la vez lectura, retención o backbone.

Observaciones que la motivan: el código actual reduce cada chunk a z y una escritura de rango1; mover hechos a actualizaciones separadas aumenta conjunta6.25→21.875% sin añadir parámetros ni tokens, y los fallos de valor se mantienen pese a un decoder que puede resolver el control explícito. Esto justifica probar preservar diferenciación entidad–valor ANTES de comprimir, no demuestra que lo resolverá ni que rango1 haga imposible almacenar dos valores.

Antes de promover ese cambio exigir contraste emparejado contra este baseline, misma pérdida/datos/semillas, parámetros/FLOPs adicionales explícitos y prueba fuerte de intercambio de valores, además de confirmación independiente. Si el cambio no mejora formación y contrafactuales, revisar señal de aprendizaje/presupuesto, no encadenar nuevas arquitecturas. No se autoriza aquí entrenamiento posterior.
