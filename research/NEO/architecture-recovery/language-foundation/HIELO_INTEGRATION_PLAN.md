# Integración futura, sin implementación

Separar modelo base LM causal (embeddings/bloques/logits/entrenador), productor de escrituras, Hielo direccionable8×d, lectura y política. Addressable estable demuestra asociaciones en DSL; no demuestra extracción lingüística. Trapos V1/V2 congelado OFF.

Primero certificar base LM en datos diversos y dev independiente. Después conectar estados causales del foreground a las proyecciones clave/valor de Hielo, manteniendo una interfaz versionada y dimensionalidad definida. No migrar automáticamente pesos simbólicos ni interpretar IDs de entidad como claves mágicas. Cambio de width futuro exige contrato explícito de proyecciones/estado, no compatibilidad asumida.

Política temporal: escrituras solo al completar chunk, resumen causal o estado de frontera declarado; ninguna escritura del chunk actual influye en su principio. Estado conservado solo dentro del documento/sesión, reset al cambiar documento; lectura y escritura con gradientes a través de frontera según horizonte de BPTT documentado. Normalización Delta y reader se certifican de nuevo para la integración. Política determinista no detecta hechos ni correcciones semánticas.

Comparación futura mínima: mismo base/contexto local con y sin Hielo; full-context separado como control de acceso a más información. Evaluaciones lingüísticas fuera de ventana solo después de certificar aprendizaje neuronal de la tarea. Reset, lectura OFF y swap con seguimiento del valor donante, no meros cambios de logits. No repetir microfits simbólicos ni reactivar filtrado para ocultar un fallo de base LM.
