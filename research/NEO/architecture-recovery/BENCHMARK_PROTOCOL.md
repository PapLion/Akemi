# Protocolo complementario de medición

La configuración de aprendizaje, semillas 17/29/43, 100 updates por brazo, fue fijada en DESIGN.md y results/learning-config.json. No se eligen prompts ni hiperparámetros tras observar exactitud.

Los contrafactuales y profiling se especificaron con la ejecución ya iniciada y algunas primeras métricas visibles: son análisis exploratorios, no confirmatorios preregistrados. No se cambiaron datos de aprendizaje, semillas ni hiperparámetros.

Además de accuracy/NLL dev por tarea, se medirá un contrafactual por cada documento dev: cambiar solo el valor de la última escritura relevante para la consulta, conservar distractores/consulta y comprobar respuesta mediante tasks.oracle. Se informará ambas respuestas correctas, cambio de predicción y precisión individual. Cambiar la predicción por sí solo no demuestra una memoria correcta.

Intervenciones sobre modelos ya entrenados: Event hard threshold 0,5 y Hielo reseteado antes de cada fragmento. Son diagnósticos de inferencia separados de los brazos entrenados con ablaciones. Comparar write_mean de fragmentos relevantes para la tarea y no relevantes; no interpretar correlación como semántica universal ni ahorro: soft ejecuta todos los candidatos.

Rendimiento sin profiler: B0 local/full, CryoTiny histórico, Event, Delta secuencial y scan; longitudes64/128/256, batch1/4, FP32, un thread. Dos warmups y cinco updates sostenidos con LM next-token sobre todos los tokens válidos (diferente de un target por ejemplo del aprendizaje). Repetir entradas/seed por brazo. El RSS es máximo acumulado del proceso, no una asignación exclusiva por módulo. Guardar bloques/dispersion. No extrapolar CPU a GPU.

Un perfil CPU acotado por prototipo, longitud128 batch1: regiones active/local, Trapos resumen, borrado/escritura, lectura. Separar medición instrumentada de throughput. La selección hard se mide además con threshold1 (control que omite todos) y0,5 (fijado); considerar coste Python de selección, no asumir aceleración.

Todos los casos que fallen se conservan; no se repetirá entrenamiento cambiando seed/config para mejorar resultados. Se conserva el fallo inicial de reporter (intentaba leer gates vacías de B0) previo a cualquier update, su regresión y corrección. La captura a float del loss produce una advertencia de autograd pero ocurre después de backward; los registros deben usar detach explícito en futuras ejecuciones, sin modificar esta trayectoria ya iniciada.

## Límite del contrafactual derivado

Cambiar v por(v+1)%8 transforma las combinaciones consultadas dev (mod4=3) en combinaciones del soporte train (mod4=0), aunque el documento y su estructura sigan siendo nuevos. Por tanto la exactitud contrafactual aislada no es una segunda medida composicional independiente. Se reporta el par con ambas respuestas correctas, cambios de predicción y esta asimetría; no se seleccionan casos favorables ni se entrena sobre los pares.
