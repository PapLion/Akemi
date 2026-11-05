# Contrafactuales y ablaciones mínimas

Intercambio de los dos valores distintos:120parejas train y120layout,100% en criterio estricto (ambos bindings correctos antes y después); también100% pareja de respuestas normales.

Correcciones:320pares. Cambiar el obsoleto conserva predicción normal100%, pero ambas respuestas correctas87,5%; criterio conjunto de ambos bindings75%. Cambiar el vigente cambia la predicción100%, pero solo75% de parejas responden correctamente ambas veces; criterio conjunto de bindings62,5%. Sensibilidad no equivale a corrección.

Resetear Hielo antes de consulta: respuesta100→25%, cambia75% predicciones. Intercambio dentro del batch16:87,5% respuesta, cambia12,5%. Este intercambio no garantiza valores diferentes en cada pareja; no extrapolar el pequeño efecto como independencia de memoria. La ablación reset es más informativa aquí. Ninguna prueba desactiva memoria durante entrenamiento.

No se han añadido nuevas pérdidas ni realizado nuevas trayectorias de ablación. Controles explícitos con clave errónea y valor erróneo están separados del modelo aprendido.
