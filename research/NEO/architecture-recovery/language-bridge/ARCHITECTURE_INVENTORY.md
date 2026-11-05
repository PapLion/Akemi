# Inventario real

Referencia inspeccionada: addressable/address_model.py y vendor/cryo_historical.py; estabilidad/README.md y DECISION.md; contract-v2/README.md y DECISION.md. Trapos V2 falló y permanece congelado.

| Componente | Estado anterior | Puente ejecutado |
|---|---|---|
| Foreground | Block histórico GQA/RoPE/RMSNorm/SwiGLU funcional | Una capa, width32, atención causal local16 |
| Refinamiento rápido | Dos iteraciones normalizadas | Mismas ecuaciones, sin profundidad nueva |
| Hielo | Matriz8×32 y Delta direccionable funcional en DSL | Misma representación y ecuación; nueva interfaz determinista |
| Extracción | Registros de4 IDs y `=`/`!`/`;` | Incompatible con texto libre; parser eliminado de esta ruta |
| Lectura | Dirección de entidad difundida dentro de registro | Dirección del token actual, sin entidad oracular |
| Cabeza LM | Proyección ligada a embedding, vocab8192 con IDs DSL | Vocab V3 real8192 y embeddings recién inicializados |
| Entrenador | Respuestas simbólicas y diagnósticos | Cross-entropy de siguiente token, padding/fronteras enmascarados |
| Generación | Evaluación simbólica | Session incremental acotada + continuación guardable |
| Tokenizer | V3 BPE8K real provisional | Integración comprobada, multiescala no usada como entrada |
| Corpus | D0/D0.1 con permisos/defectos distintos |8 documentos naturales locales +32 relatos controlados train |

No existía una ruta de escritura semántica validada para lenguaje libre. Este puente es un adaptador explícito, no una continuación automática del certificado simbólico. No se reutilizaron embeddings ASCII como si sus IDs fueran BPE. No hay parser de entidades, Trapos, RAG ni KV cache oculto. Los certificados de CUDA/BF16 anteriores no se transfieren.
