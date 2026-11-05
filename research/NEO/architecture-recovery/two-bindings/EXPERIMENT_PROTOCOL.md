# Protocolo ejecutado

A: `CE_respuesta + 0.1 CE_inicial`. B: `CE_respuesta + 0.1 CE_inicial + 0.1 CE_posterior`. Cada CE de etapa es media de2targets por secuencia; la contribución inicial es idéntica antes de añadir posterior. Autograd certifica coeficientes (.1,0) y (.1,.1). El tratamiento aumenta señal total y trabajo; no se afirma igual carga de optimización. Clipping global1 puede modificar escalas efectivas después de sumar gradientes, parte de la receta común.

CPU FP32,1thread,150updates,batch8,AdamW lr.003,betas(.9,.95),decay.01,foreachFalse. Mismos índices con Random17. Checkpoint histórico DeltaFast17 estricto, decoder condicionado por entidad seed101. Ningún hiperparámetro se seleccionó con dev. Umbrales auxiliares previos≥90% y CE<.5; no se ampliaron updates.

El objetivo principal de respuesta permanece en ambos brazos y puede enviar gradiente desde la consulta a estados iniciales. «Supervisión inicial» significa exclusivamente la pérdida auxiliar, no truncamiento de gradiente de respuesta. Los estados recurrentes no se detachan entre chunks.

Versión y configuración exactas en protocol.json. Estados iniciales y finales guardados por brazo, igual número de parámetros. Identidad y orden verificados tras entrenar.
