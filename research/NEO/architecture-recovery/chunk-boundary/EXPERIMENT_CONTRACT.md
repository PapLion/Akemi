# Contrato fijado y ejecutado

160programas por condición:5pares cíclicos×16pares de valores×2órdenes. Todos los pares de valores por pareja aparecen2veces. Se consulta rolA; rolB es la otra entidad. Identidades rotan sobre5entidades, no todas las20parejas ordenadas. Mismos valores, órdenes, targets, consulta, multisets de registros y batches por índice.

Train same escribe en registros2/3; separate en0/3. Cada registro ocupa4IDs. Ambos supervisan ambas asociaciones tras chunk1, enID16. Dev mueve ambos esquemas+4registros:6/7 y4/7, supervisión tras chunk3 enID32. Total64IDs,15registros+consulta final,8chunks de8IDs. Registros neutrales~ son propuestas rechazadas por el oráculo, pero el forward sí actualiza Hielo al final de cada chunk. No se finge que son inertes neuronalmente.

No hay corrección posterior ni CE posterior: se mide formación y conservación neutral. Cada etapa auxiliar tiene2targets, CE media. Pérdida `CE_respuesta +0.1 CE_inicial`. Misma contribución en ambos brazos, sin modificar arquitectura, reglas, decoder ni pesos originales. Respuesta principal sigue propagando gradientes desde consulta. Capturas posteriores solo para evaluación.

CPU FP32,1thread,seed17,decoder101,150updates,batch8,AdamW lr.003,betas(.9,.95),decay.01,clip1,foreachFalse.1200secuencias muestreadas con reemplazo y2400targets auxiliares por brazo; no equivalen a nuevos ejemplos independientes. Umbrales históricos≥90% y CE<.5 no se relajaron.

Dev tiene textos/IDs distintos; comparte combinaciones y órdenes conocidos. Evalúa desplazamiento de layout, no nuevas entidades ni generalización composicional independiente. Nunca se utilizó el final sellado.
