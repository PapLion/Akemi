# Language Bridge V1 — estado añadido sin alterar históricos

Rama `cryo-language-bridge-v1`, base1841b99. Implementación y resultados en [language-bridge/README.md](language-bridge/README.md).

Operativo: NeoTokenV3 BPE8K provisional, LM causal pequeño, entrenamiento CPU, control sin Hielo, generación incremental, estados guardables y reanudación exacta. Trapos aprendido OFF.

Experimental: consultas por token y escritura al final de chunks16 sobre Hielo8×32. La pérdida dev baja, pero el diagnóstico de memoria distante queda en25% y no demuestra utilidad de Hielo. No se hereda automáticamente la capacidad simbólica de AddressableV1.2.

Pretraining significativo: NO preparado/autorizado por este smoke. Consultar PRETRAINING_READINESS.md y DECISION.md. No Chinchilla, GPU, pagos ni evaluaciones selladas. Se preservan los resultados previos.
