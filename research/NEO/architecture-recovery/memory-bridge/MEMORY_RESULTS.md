# Resultados y alcance

| Modelo/condición | Respuesta exacta | Ambas asociaciones | Estado |
|---|---:|---:|---|
| Control oracular explícito |100%|100%|Diagnóstico asistido |
| Foreground completo, microfit train |50% (16/32)|18.75% (3/16)|200updates, FAIL |
| Foreground local A, principal |—|—|NO EJECUTADO |
| Hielo B, principal |—|—|NO EJECUTADO |
| Foreground completo C, principal |—|—|NO EJECUTADO |
| Semillas29/43 |—|—|NO EJECUTADAS |

No existen resultados V2 sobre dev de combinaciones, reformulaciones, corrección o conservación porque la precondición falló. Los datos se generaron y sus oráculos se verificaron, pero no se midieron esos resultados con nuevos modelos entrenados. No presentar el techo analítico25% de A como una exactitud medida.

En el microfit,16/16historias reciben la misma predicción para ambas entidades, incluso cuando sus valores difieren. Los cuatro tokens de respuesta son válidos, pero no se siguen relaciones consulta–entidad–valor. Confusión por clase y predicciones completas en final-metrics.json y micro-full-17-train-predictions.json. Los32ejemplos no son32unidades independientes: hay16programas y una semilla.

Inferencia sin reentrenar, quitando distractores del mismo checkpoint:25% respuesta,6.25% conjunta. Cambian conjuntamente posiciones/distancia, de modo que no aísla causalmente la longitud y no prueba un fallo de capacidad representacional. No se usa para modificar receta.

NLL sobre prefijo+pregunta+respuesta del microfixture: 10.29588, PPL 29610.3 sobre3552targets. El entrenamiento optimizó solo respuesta, cuya CEfinal1.04552 es una métrica distinta. No hay medición de lenguaje real externo en esta fase ni una afirmación de mejor capacidad lingüística.

La prueba central sobre Hielo sigue SIN RESOLVER. El cuello de botella observado primero está en aprender recuperación condicionada por consulta bajo esta configuración, incluso cuando el control ve los hechos. No se puede adjudicar el fracaso a escritura/retención/reader de Hielo porque el brazo B no se habilitó.
