# A/B: respuesta normal sin decoder auxiliar

|Formato|Panel|Entidad A|Entidad B|Conjunta|CE respuesta|Respuesta idéntica|
|---|---|---:|---:|---:|---:|---:|
|A|train|25.00%|25.00%|0.00%|1.392363|24/24|
|A|dev-combinations|25.00%|25.00%|0.00%|1.392362|24/24|
|A|dev-layouts|25.00%|25.00%|0.00%|1.392364|24/24|
|B|train|25.00%|25.00%|0.00%|1.392653|24/24|
|B|dev-combinations|25.00%|0.00%|0.00%|9.539395|0/24|
|B|dev-layouts|25.00%|25.00%|0.00%|1.392657|24/24|

Argmax sobre8192IDs, no selección forzada entre colores. Una respuesta supervisada por secuencia; no teacher forcing de la respuesta. Checkpoint final200 fijado, sin selección por dev. En train ambos predicen exclusivamente5927(white). En dev pares B predice5927 para Nora y6101para Mira, sin resolver ambas asociaciones; cambiar predicción no basta. Exactitud de primer/último valor seguido25%train,12,5%dev pares B. Ambas órdenes factuales dan las mismas tasas; no hay éxito oculto en un solo orden.

A reproduce exactamente todos los pesos finales del control corto anterior40848ae, ver diagnostics.json. La identidad inicial A/B se certifica con hash real de pesos. Esto no garantiza resultados universales: una semilla y doscientas actualizaciones limitan el alcance.
