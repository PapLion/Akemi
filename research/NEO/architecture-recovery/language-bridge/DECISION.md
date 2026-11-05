# Decisión

1. **Sí**, CryoCCM-Addressable puede adaptarse y ejecutarse como LM causal: forward/backward, AdamW, shift, generación y reanudación comprobados. Es una instancia nueva pequeña, no un checkpoint simbólico convertido silenciosamente.
2. Faltaban contratos libres de DSL para escribir/consultar, entrenador next-token y generación de sesión. Se implementaron explícitamente. El extractor semántico sigue ausente.
3. NeoTokenV3 BPE8K real pasa encode/decode, referencia independiente, streaming y fixtures Unicode/bytes. Es apto provisionalmente para el smoke; no se modifica ni se declara definitivo/multiescala causal.
4. **No** se demuestra ventaja funcional de Hielo en dependencias largas:25% de cuatro opciones, sin caída al reset/swap. Una mejora pequeña de NLL dev no sustituye esa prueba.
5. Coste CPU observado:1838 targets/s con Hielo vs2014 sin él, aproximadamente9.6% más tiempo total. Una semilla y proceso compartido, no evidencia CUDA.
6. Escritura determinista sirve como interfaz técnica temporal y causal. No está validada como solución de memoria lingüística: clave del último token/puntuación, compresión y lectura por token siguen limitando el puente.
7. Limitan la transición la falta de recuperación entrenada en lenguaje, exposición mínima/diversidad, derechos condicionados y ausencia de un contrato semántico para claves; el diagnóstico no aísla cuál causa el negativo.
8. **No se justifica iniciar pretraining significativo todavía.** El siguiente paso razonable es un único contraste pequeño de recuperación lingüística con objetivo de respuesta comprobable, A/B local idéntico y conjunto independiente, con nueva autorización y presupuesto. No rediseñar Trapos automáticamente, no tocar Hielo/tokenizer simultáneamente ni escalar hasta demostrar utilidad.

Operativo: núcleo BPE, adaptador, LM causal, controles, checkpoint, generación y métricas. Experimental: escritura/lectura lingüística determinista, memoria de largo alcance. Pendiente: calidad de lenguaje, recuperación funcional generalizable y gates de datos/coste. Resultados originales, Trapos negativo y conjuntos sellados permanecen intactos.
