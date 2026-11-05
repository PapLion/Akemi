# Piloto CPU

Dos inicializaciones idénticas del checkpoint DeltaFast17. AdamW fresco,lr0.003,betas0.9/0.95,weight_decay0.01,clip1,batch8,semilla de muestreo17. Decoder lineal condicionado por entidad256→4,cinco cabezas,semilla101; mismas dimensiones/pesos en ambos brazos. Control: decoder sin contribución a loss, gradienteNone, sin estadoAdamW ni weight decay efectivo. Tratamiento: lambda0.1. Inferencia original nunca utiliza decoder.

Cada fragmento de8IDs contiene dos registros. Tras su escritura REAL, consultar cada entidad con operación aceptada =/! en ese fragmento. Oráculo exclusivamente de registros hasta esa frontera; si ausente tras borrado se enmascara. Se supervisa el valor final de prefijo, incluso si hubo otra actualización de la misma entidad. No se utiliza estado futuro/final para una etiqueta pasada. Gradientes atraviesan la memoria real sin detach y el resumen/regla delta/retención/borrado originales.

Microfit20programas: cuatro valores por cinco entidades, presencia constante.150updates máximos; antes de ejecutar se fija puerta:accuracy auxiliar≥90% y CE<0.5. Si falla, no ejecutar los dos brazos de600updates. No adaptar el umbral después de observar resultados. Este es diagnóstico mecánico, no generalización. No se sustituyen los pesos por los aprendidos en microfit para el ensayo principal.

Si pasa: dos brazos600updates; mismos programas/índices aleatorios. Checkpoints separados con AdamW/RNG/cursor/decoder/modelo. Sin scheduler/AMP/acumulación pendiente. No entrenar lenguaje ni usar GPU/corpus/evaluación sellada.
