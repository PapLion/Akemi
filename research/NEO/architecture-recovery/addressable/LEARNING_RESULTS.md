# Aprendizaje ejecutado

Microfit:32registros, entidades A/B, cuatro valores cada una,16combinaciones×2órdenes. 300updates, semilla17,batch8,AdamW LR0,003 betas0,9/0,95 decay0,01 clip1. L=CE_respuesta+0,1 CE_inicial; mismo decoder auxiliar anterior. Compuerta fijada antes de entrenar: ambas marginales y conjunta≥90%, CEmedia<0,5. Resultado100% conjunto y lector normal100%; CE_A=0.0000199, CE_B=0.0000144. Gate PASS.

Contraste principal:160registros, cinco pares cíclicos de entidades,16pares de valores×2órdenes;300updates con idéntica receta. Ambas asociaciones se supervisan solo después de formarse. No se enseñan correcciones en este entrenamiento. Mismos índices de batch que rango1 original, comprobados los300updates. Se reutiliza su ejecución previa inmutable; no se afirma haberla reentrenado.

|Sistema|Conjunta inicial train|Conjunta nuevo layout|Respuesta normal layout|
|---|---:|---:|---:|
|DeltaFast rango1 original|8,125%|6,875%|25%|
|Addressable|100%|100%|100%|
|Explícito diagnóstico|100%|No equivalente|No modelo Cryo|

En Addressable, consultar separadamente ambas entidades y exigir ambas respuestas normales correctas:100% en train y layouts. No es solo un probe. Marginales A/B100%, matrices completas en JSON. CE inicial dev A=0.0001060, B=0.0001060.

Generalización adicional:480casos de pares de entidades no usados juntos en train, mismos cinco tokens de entidad/cuatro valores y layouts desplazados:90% conjunta auxiliar y95% respuesta normal. No vocabulario nuevo. No independencia estadística entre todos los contrafactuales ni confirmación multisemilla.
