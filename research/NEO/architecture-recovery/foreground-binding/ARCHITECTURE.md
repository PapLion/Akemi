# Arquitectura

Embedding 8192×32 compartido con LM head. Bloque original: RMSNorm, Q/K/V con RoPE, atención causal GQA (4 cabezas, 2 KV), proyección residual; RMSNorm, MLP SiLU gated y residual. Después, dos refinamientos rápidos normalizados por posición; no constituyen atención adicional. Predicción desde último token válido, antes del target.

A: un bloque, MLP interno128. B: dos bloques idénticos de diseño, ancho32. C: un bloque, MLP interno289. C difiere de B en32 parámetros; igualar parámetros no iguala cómputo ni profundidad. Hielo queda desactivado y sus3360 parámetros congelados.

Componentes homólogos idénticos inicialmente. B añade bloque inicializado con seed1017. C conserva submatrices originales y añade pesos seed2017. Arquitecturas diferentes no tienen inicialización idéntica completa. Todos los parámetros activos reciben gradientes y AdamW. Ver parameters.json e initial-weights.json.

La primera capa calcula K/V de cada valor antes de incorporar su entidad anterior. La segunda recibe salidas contextualizadas. Esto no demuestra incapacidad matemática absoluta de una capa.
