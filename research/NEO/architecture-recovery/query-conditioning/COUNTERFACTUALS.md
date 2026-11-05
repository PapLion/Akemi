# Intercambios de valores y consulta

Para cada combinación de dos colores diferentes hay historia A=x,B=y y su intercambio A=y,B=x, ambas órdenes.12pruebas estrictas por panel; cada una exige cuatro consultas correctas. Ambos formatos obtienen0/12 en train y en ambos dev. Las predicciones de las cuatro consultas están preservadas e identificadas por program_id/valores en datasets.json.

Cambio exclusivo de consulta:0/24historias con ambas respuestas correctas en todos los paneles. A produce respuesta idéntica en24/24; B también en train/layouts. En pares nuevos B produce respuestas distintas, pero ambas correctas en0/24. Esa diferencia de identidad es compatible con sobreajuste del último token y no prueba recuperación.

Los tests del oráculo comprueban que los valores son distintos, que el intercambio cambia necesariamente el target y que la pregunta no introduce la respuesta. No se utilizaron etiquetas para indexar memoria o seleccionar atención.
