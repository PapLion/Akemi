# Realizabilidad y precondición fallida

Oráculo exacto de memoria por entidad:100% en train/dev/micro. Se verifican etiquetas mediante recorrido causal del diccionario y una segunda implementación de búsqueda inversa por entidad. Es selección asistida por el oráculo, no un logro de CryoCCM.

Reader lineal20parámetros sobre el valor explícito one-hot:100% tras100updates, CE 1.4397→1.0210. Diagnóstico de realizabilidad, no usa Hielo aprendido ni se incluye entre parámetros de los brazos.

Control sin valores: el mejor prior de clase condicionado por consulta/entidad/idioma llega exactamente25% tanto en train como micro. Heurística primer valor global:43.75%train/62.5%micro; último valor global62.5%. Recuperación por última escritura DE LA ENTIDAD logra100% porque implementa el oráculo. El panel exige binding, no mera recencia global. Un porcentaje superior a25% no basta para demostrarlo.

Control con contexto completo: mismo foreground/refinamiento rápido del brazo local sin Hielo; se llama al chunk_hidden original sobre toda la secuencia causal. La única diferencia respecto a A es visibilidad/posiciones de atención; no se usa la variante Transformer sin refinamiento de V1. Modelo pequeño nuevo desde semilla17, no warmstart lingüístico. Los tests comprueban que la pérdida tiene gradiente hasta el hecho visible.

Compuerta microfit congelada: exactitud≥95% y CE<.3 tras200updates sobre32ejemplos. Resultado50%, CE1.04552; ambas consultas correctas18.75%. La curva baja desde una CE cercana a9 y aprende los cuatro tokens de respuesta, pero no la recuperación por entidad. Fallan ambos requisitos sin cambiar umbrales ni extender presupuesto.

El fallo es de esta configuración/receta, no prueba de incapacidad del Transformer ni de Hielo. El oráculo resuelve los datos, pero no sustituye la precondición de aprendizaje del control neuronal. Por esa razón no se entrenaron A/B/C ni semillas adicionales.
