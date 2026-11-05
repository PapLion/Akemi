# Intercambios y cambios de consulta

Cada panel tiene24 historias (valores diferentes, dos órdenes). Para cada par no ordenado de colores y orden hay una historia y su intercambio:12 pruebas estrictas, cuatro respuestas obligatoriamente correctas por prueba. Ambos brazos:0/12 en train y en ambos dev.

Cambiar solo consulta manteniendo hechos exige responder el otro color. Ambos brazos:0/24 historias con las dos respuestas correctas,24/24 con respuesta idéntica. La red predice siempre ID5927 en train (un color admisible), no una secuencia desconocida o token especial. No se restringió argmax a cuatro colores: se evalúan8192 IDs. No hay evidencia funcional de consulta condicionada.
