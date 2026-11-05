# Contrato ejecutado

640 secuencias por condición, cinco entidades, todas las parejas ordenadas distintas, cuatro valores independientes para cada asociación, dos órdenes iniciales. 64 IDs,15 registros y consulta; tres escrituras semánticas. Supervisión de ambas entidades tras chunks0 y2: cuatro targets por secuencia,2560 por fixture. Chunk0 contiene las dos inicializaciones; chunk2 contiene el evento. Son actualizaciones densas suaves reales, no eventos binarios de compuerta. Etiquetas del último registro aceptado del prefijo causal, comprobadas mediante búsqueda inversa independiente.

A/B modifican entidad consultada; C/D la otra. Igual/diferente se define respecto al valor previo de la entidad escrita, no necesariamente el de la consulta. Valores diferentes usan desplazamientos1–3 determinados por pareja/orden: su frecuencia no es uniforme; no se afirma balance perfecto por desplazamiento. Los marginales entidad/valor/chunk sí se verifican exactamente desde targets usados por CE; ver *-frequencies.json.

Layout diagnóstico desplaza inicialización de registros0/1 a2/3 y evento4 a8; conserva cuatro targets, con sus límites causales ajustados. Comparte combinaciones: prueba desplazamiento estructural, no entidades ni combinaciones inéditas. La respuesta final está fuera de ventana local16, sin KV cache.
