# Generalización de posiciones

|Brazo|Mín.lector rejilla|Máx.lector rejilla|Celdas|
|---|---:|---:|---:|
|A|68.75%|100.00%|80|
|B|100.00%|100.00%|80|

Rejilla congelada antes del entrenamiento:inicial(0,1),(2,3),(4,5),(6,7),(0,3),(3,6);corrección4,5,6,8,9,10,11,12 cuando está en chunk posterior;ambos órdenes.80casos/celda. Todas corrigen la entidad consultada; la tasa de cambios injustificados de una consulta no modificada no tiene denominador y se marca null. Métricas,confusiones y predicciones completas en position-grid.json y *position-grid-predictions.json. La celda con corrección12 entra en la ventana visible y no acredita retención fuera de ventana. Familias principales y holdout con corrección11 están completamente fuera.

El layout alternativo histórico movía escrituras de fase2/3 a0/1 dentro del bloque local de16IDs; desplazar4registros(16IDs) conserva fase,desplazar2registros(8IDs) la cambia. position-shift-invariance.json verifica sin updates desplazamientos comunes de ambas escrituras y corrección,conservando distancia entre hechos. Esto permite distinguir fase local de una simple posición absoluta en el alcance probado. No generaliza a todas las posiciones posibles.

Cambiar orden puede modificar contexto causal y orden de actualizaciones Delta. Separar chunks también cambia lectura de memoria durante la escritura. No atribuir diferencias exclusivamente a compresión,frontera o a una compuerta. Formato de cuatroIDs permanece constante:no se ha probado parsing de lenguaje natural.

No se habilitó P según el criterio prospectivo.

B corrige el layout alternativo original sin variar posiciones iniciales de entrenamiento: la cifra56,25% anterior no prueba una incapacidad arquitectónica fija. Exposición a correcciones basta para mejorar esa condición,pero no aísla qué parámetros compartidos produjeron la generalización. No se ha cambiado diseño ni hiperparámetros.

Medición adicional, 40 pares por desplazamiento: al desplazar 16 IDs, logits y Hielo coinciden exactamente en A y B. Al desplazar 8 IDs, A cambia el 25% de predicciones (máxima diferencia de logits 17,7441); B no cambia predicciones, aunque sus logits cambian hasta 0,6836 y su memoria hasta 0,2885. La invariancia de respuesta de B no implica invariancia del estado.
