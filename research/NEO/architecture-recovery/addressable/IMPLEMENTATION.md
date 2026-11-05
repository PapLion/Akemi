# Implementación

`address_model.py`: nueva clase, fábrica y carga estricta weights_only. Foreground, embeddings, fast, fast_norm, read, slow_norm y LM head conservan pesos iniciales bit a bit. Nuevos Wk 32×8 sin bias, Wv 32×32+bias y Wout 32×32 sin bias: 2.336 parámetros adicionales. Se inicializan con seed707 después del decoder seed101.

El antiguo memory_head se retiene físicamente para planificación y trazabilidad, con todos sus parámetros congelados porque sus proyecciones ya no participan. No hay parámetros entrenables huérfanos. AdamW se construye después de crear módulos. Decoder auxiliar idéntico al baseline, solo supervisión inicial con etiquetas de prefijo; no se usa durante inferencia normal.

Formato acotado: registros simbólicos de cuatro IDs alineados dentro de chunks de ocho, documentos de 64 IDs en el experimento. El calendario acepta sintácticamente `=`/`!` terminados en `;`. No resuelve borrado, lenguaje natural o detección libre de acontecimientos. No equivale a filtrar relevancia aprendida. No se modifica NeoToken; estos son fixtures simbólicos ASCII del protocolo anterior.

Estado persistente entre chunks de un forward; reset documental y nuevo estado cero en cada llamada. No se certifica API de streaming entre llamadas con caché del foreground. `intervention=reset/swap` actúa únicamente antes de leer el último chunk.
