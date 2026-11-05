# Selección reproducible

Hay dos manifiestos separados:

1. approved-selection.json: 3 documentos train Click y 2 dev Requests, 25.355/8.637 targets. Único permitido al lector.
2. conditional-selection.json: Wikipedia EN/ES de la vista 1B actual; no autorizado para entrenamiento.

Selección candidata por SHA256(clave), sin usar contenidos de test; artículos completos hasta 30.000 IDs de texto por artículo. Se conserva split histórico train/dev, se excluyen conflictos de componente y hashes duplicados antes de aceptar un documento. Las vistas 500M/1B no se suman. La elección no usa resultados de entrenamiento. Se retienen suficientes artículos para superar 2,5M targets train y 100k dev por idioma; el exceso es disponibilidad, no permiso de exceder el presupuesto futuro de 5M.

La fuente dominante sigue siendo Wikipedia: dos ediciones y muchos artículos no equivalen a muchas familias de fuentes independientes. Código/documentación aprobados son mínimos y solo EN. No se inventa una mezcla ideal. No hay repetición de exposiciones para rellenar el déficit. La reserva independiente de trabajos/código permanece fuera de train.

Si se resuelven derechos, el próximo manifest autorizado deberá fijar exactamente el corte de 5M targets y sus máscaras; esta selección condicional no es todavía un release entrenable.
