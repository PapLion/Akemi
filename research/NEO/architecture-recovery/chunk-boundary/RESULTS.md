# Resultados medidos

|Condición / split|Entidad A|Entidad B|Conjunta|Producto marginales|CE A|CE B|Lector original|
|---|---:|---:|---:|---:|---:|---:|---:|
|same / train|25.00%|25.00%|6.25%|6.25%|1.3857|1.3900|25.00%|
|same / dev|25.00%|25.00%|6.25%|6.25%|1.3861|1.3902|25.00%|
|separate / train|53.12%|52.50%|21.88%|27.89%|1.2257|1.2134|30.00%|
|separate / dev|52.50%|50.62%|20.62%|26.58%|1.2422|1.2304|30.00%|

Referencia descriptiva: producto de las marginales no es una hipótesis de independencia probada ni un límite de capacidad. En separate train, conjunta21.875% frente producto27.891%; ambas asociaciones no se resuelven conjuntamente con la frecuencia que sugeriría independencia. En same, marginales25% y conjunta6.25%, con predicciones constantes por entidad (confusiones guardadas).

Diferencia separate−same conjunta:15.625puntos train y14.375puntos dev. No son diferencias entre varias semillas ni estimación de rendimiento lingüístico. Curvas150updates, CE y predicciones completas por etapa/entidad/valor en *evaluation.json y *curves.json.

El lector original obtiene25% same y30% separate en train/dev. Esto no acredita recuperación fiable. No se ejecutaron600updates ni se ajustaron hiperparámetros.
