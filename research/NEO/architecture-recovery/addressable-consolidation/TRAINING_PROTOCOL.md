# Protocolo fijado antes de entrenar

`protocol.json` y results/FREEZE.json registran UTC y hashes de arquitectura,generador,trainer y preflight antes del primer brazo. Semilla17,CPU FP32,un hilo,300updates,batch8,AdamW lr0,003 betas(0,9;0,95),decay0,01,clip1. L=CE_respuesta+0,1 CE_inicial. No supervisión auxiliar posterior ni pérdida nueva.

A: los160registros originales literales y el mismo Random(17).randrange(160). B: mismo índice base, variante=(step*8+slot)%12, seis variantes sin corrección y seis con corrección(2entidades×3transiciones no nulas). 50% correcciones exacto en cada batch; cuatro respuestas nuevas por batch no necesariamente, pues solo la mitad corrige la entidad consultada. Longitud64IDs,consulta final,escrituras iniciales en registros2/3,corrección en8. Cada ejemplo conserva una respuesta y dos targets auxiliares iniciales; cada brazo consume2400/4800targets,153.600IDs de entrada. Supervisión inicial idéntica entre A y B antes de las correcciones. La única intervención primaria es distribución de acontecimientos de entrenamiento.

Las dos copias iniciales son exactamente iguales. A17 termina con modelo,decoder y AdamW exactamente iguales a V1: reconstrucción fuerte del control, no aproximación. Las órdenes de índices base de A/B coinciden los300updates por semilla. B expone1200correcciones adicionales y necesariamente otra distribución de estados/gradientes. No afirmar igualdad de exposición semántica ni de gradientes.

Gates prospectivos: valor corregido≥90% en familias fija/pares nuevos y nuevo layout; no modificada≥95%; intercambios normales y conjuntos≥95%; formación≥95%; conjunta de pares nuevos≥90%; respuestas de formación ambas entidades≥95%,correcciones≥90%; parejas contrafactuales normales≥90%. Ingeniería, no significación estadística. Final update300 fijo, sin búsqueda por dev.

Tras pasar17,confirmaciones A/B29y43 con mismos datos/hiperparámetros. Se reutiliza en cada semilla el warmstart histórico correspondiente(17/29/43), mismas congelaciones; nuevos módulos seed707+(s−17),decoder101+(s−17),sampler s. No son modelos independientes desde cero: comparten familia de datos, arquitectura y entrenamiento histórico; diferencias A/B emparejadas. No se cambian hiperparámetros tras fallos de confirmación.

La evaluación confirmatoria nueva no se usa para estos gates ni se consulta. El tercero P se autoriza solo por el criterio de posición prefijado y compara exclusivamente variedad posicional con B, desde la misma inicialización17.
