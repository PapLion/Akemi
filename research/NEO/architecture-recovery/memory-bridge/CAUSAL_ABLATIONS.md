# Auditoría de rutas y estados

Diagnóstico previo: V1 no entrenó preguntas/respuestas de recuperación distante; sus historias de exposición no constituían señal para contestarlas. Las evaluaciones eran posteriores. V2 implementa esa señal, pero queda detenido antes de B por la compuerta positiva.

La ruta conserva estados reales H8×32 entre chunks. Un checkpoint V1 inmutable se cargó y se extrajeron estados al terminar cada chunk; volver a consultar desde el estado previo coincide con el forward completo. Los snapshots están en v1-state-audit.pt, con SHA del checkpoint fuente, tokens de ejemplo y fingerprint V3.

Gradiente real de CE de respuesta sobre ese checkpoint: primer H=0.00389748; event_value=0.238496; address=0.0186472; read=0.035319. Llegar con gradiente no demuestra una política aprendida ni buen horizonte de aprendizaje.

Intervenciones implementadas fuera del módulo original:
- Normal: H obtenido causalmente del prefijo.
- Reset: cero justo ANTES de procesar la pregunta, no después de producir la respuesta.
- Swap: H de un prefijo donante real y compatible; se comprueba si la salida sigue su valor.
- Sin escritura: H empieza en cero y no se actualiza en prefijo ni pregunta.
- Sin lectura: mantiene H del prefijo pero anula la salida de read durante la consulta; se etiqueta como ablación de lectura en consulta, no intervención global de entrenamiento.

En los ocho fixtures mecánicos V1, reset/sin escritura/sin lectura alteran logits hasta0.01076; swap hasta2.86e-6. Todos mantienen el token newline,0% de respuesta y de seguimiento del donante. No es una ventaja funcional y no sirve para inferir aprendizaje de B.

Las claves siguen siendo de token, no de entidad semántica. La pregunta termina en el mismo token, y las fronteras suelen terminar en espacio: compartir un token de dirección puede limitar el direccionamiento, pero los estados y el foreground contienen otras dependencias; este diagnóstico no prueba una incapacidad ni una causa única. No se cambia el reader para corregirlo sin un contraste posterior.

Ausencia de atajos: hechos fuera de ventana16 al consultar, estado local sin-Hielo independiente del prefijo, clases balanceadas por pregunta; el control completo conserva explícitamente más información y no cuenta como igualdad computacional. No hay KV cache, labels oraculares ni historial oculto.
