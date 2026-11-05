# Experimento mínimo que falta

## Pregunta

¿El refinamiento rápido normalizado mejora optimización/generalización por sí mismo, y aporta Hielo editable una ventaja cuando el hecho ya no está en la ventana visible? Son dos preguntas distintas. No se resuelven aumentando tamaño ni repitiendo el panel actual.

## Paso1: eliminar el atajo antes de comparar memorias

Crear un generador versionado con oráculo y registro de cada operación. Posición de la entidad consultada, hecho inicial, corrección y consulta deben variar independientemente. El primer hecho no debe predecir sistemáticamente la respuesta; balancear respuestas, operaciones y distancia. Incluir borrado SIN reemplazo y opción explícita de ausencia. Evitar que la cantidad de distractores o la posición de consulta revele la etiqueta.

Separar cuatro paneles: combinaciones entidad–valor vistas/no vistas × familias estructurales vistas/no vistas. Holdout por programas y familias; congelar hashes antes de entrenar. Reservar nuevas familias confirmatorias no utilizadas para elegir arquitectura. El dev actual ya se utilizó para investigar y no cumple esa función.

Invariantes del generador: cambiar un hecho obsoleto conserva respuesta; cambiar el hecho vigente cambia respuesta; permutar distractores irrelevantes conserva respuesta; renombrar entidades coherentemente conserva semántica. Un predictor de primer hecho, último valor y frecuencia debe quedar cerca del azar balanceado. Si alguna regla trivial resuelve la tarea, corregir el diseño antes de entrenar y conservar el fallo.

## Paso2: identificar el readout suficiente

Mismo foreground histórico, embeddings, norma final, semilla y receta. Controlar por separado: sin refinamiento; un refinamiento; dos refinamientos; dos refinamientos sin RMS intermedio. Inicializaciones comunes para pesos existentes y construcción RNG aislada para módulos nuevos. No cambiar a la vez FFN, posición, tamaño de memoria o receta. Si quitar RMS vuelve inestable la loss, documentarlo sin ajustar silenciosamente el learning rate de ese brazo.

Tres semillas fijas17/29/43. Presupuesto exploratorio máximo1000updates×batch8 por brazo (8000respuestas), sin selección del mejor checkpoint. Evaluar todos los cortes prefijados100/300/1000. Reportar train/dev, exactitud por tarea y las cuatro celdas de generalización. La variación entre semillas impide declarar superioridad por una sola corrida.

## Paso3: prueba identificable de Hielo

Conservar el mejor control rápido como backbone fijo del diseño, sin seleccionar por el nuevo test. Comparar histórico, no_ice entrenado, EventFast y DeltaFast con ventana local que NO incluya el antecedente. Añadir control Transformer de contexto completo que sí vea las mismas entradas históricas; informar su mayor coste. También control local sin memoria: identifica la dependencia de información ausente, no igualdad de información disponible.

Ablaciones entrenadas: escritura siempre activa, sin gate selectivo y memoria reiniciada por chunk. Suprimir memoria solo en inferencia se conserva como diagnóstico secundario. Mismos ejemplos/targets por brazo, y una comparación separada limitada por tiempo/FLOPs contabilizados; no llamar equivalentes a esos presupuestos.

Criterio de utilidad: ganancia reproducible en retención Y corrección respecto al control local sin memoria, contrafactuales coherentes, sin empeorar sistemáticamente las otras tareas; reportar coste por respuesta correcta y latencia. Una mejora en la media dominada por tareas fáciles no basta. Prerregistrar el margen práctico y análisis de incertidumbre antes de ejecutar, según el presupuesto real de nuevos ejemplos; tres semillas no permiten una conclusión poblacional fuerte.

## Recursos y parada

CPU FP32, un thread, modelos pequeños, sin corpus lingüístico ni GPU. Primero oráculos y microfit; después contratos causales/gradientes/AdamW/resume sobre el nuevo masking. Parar un brazo ante NaN/Inf, fuga, parámetros omitidos o generador defectuoso. No ampliar updates por observar resultados favorables. No se ejecutó este experimento confirmatorio durante el presente estudio; los artefactos actuales permiten implementarlo sin reconstruir el histórico.
