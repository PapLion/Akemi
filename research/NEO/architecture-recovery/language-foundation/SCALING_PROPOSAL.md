# Siguiente escalón: dos candidatos, no implementados

El prototipo width32 tiene suficiente capacidad para demostrar reducción de NLL y ajuste limitado; no evidencia suficiente de una base lingüística útil. El embedding consume88,5% del presupuesto activo. Proponer más capacidad se justifica por ese reparto y por la dieta mínima, no porque se haya aislado una ley de escalamiento con estos dos modelos casi iguales.

| Candidato futuro | Width / bloques | Parámetros activos estimados | Embedding tied | Contexto inicial | Targets propuestos |
|---|---:|---:|---:|---:|---:|
| F2 | 128 /4 | 2082176 | 1048576 (50,36%) | 128 | 5M |
| F8, condicionado al resultado F2 | 256 /6 | 8195840 | 2097152 (25,59%) | 256 | 50M |

Conteos algebraicos para la familia actual sin Hielo: P=8192d+L(15d²+2d)+3d²+3d; incluyen refinamiento rápido, tied head, GQA mismo ratio. No se construyeron modelos nuevos. Baseline futuro: Transformer causal estándar con mismos tokenizer/contexto/targets, presupuesto cercano y FLOPs informados; separar aporte de refinamiento del de Hielo. Primero F2 contra baseline, no entrenar ambos tamaños a la vez.

5M/50M son presupuestos de ingeniería inicial, no cantidades óptimas ni suficientes por ley para dominio del lenguaje. Exigir al menos esas posiciones de texto diverso, derechos revisados y reserva dev por familias, preferiblemente una pasada sin ciclos. El panel actual25355train obligaría a197/1972 pasadas: inadmisible como sustituto de esos corpus. No usar Chinchilla hasta cerrar compuertas de datos por autorización separada.

**Cómputo y dinero:** el modelo actual a5638targets/s tardaría14,8min por5M y2,46h por50M, extrapolación del mismo código/tamaño sin evaluación ni I/O; no es rendimiento esperado de F2/F8. Para esos candidatos se necesita preflight/benchmark propio antes de presupuestar. No hay medición CPU/GPU de ellos.

Referencia histórica concreta, no oferta actual: FIRST_CUDA_RUN.md midió B0~8M a1794,23targets/s, RTX3090,256FP32,batch1; tarifa total entonces0,15222222USD/h. Bajo exactamente ese rendimiento/tarifa:5M≈0,774h/0,118USD;50M≈7,741h/1,178USD. No incluye arranque/transferencias/evaluación/checkpoints, no presupuestar Cryo con esos valores ni asumir esa tarifa disponible hoy. Son escenarios de sensibilidad, no cotización ni permiso de gasto. Estimar coste real mediante C=(targets/throughput/3600 + horas setup/eval)×tarifa total + tráfico; imponer margen y destrucción. No se consultó Vast ni se gastó saldo.

Recomendación: preparar datos reales bilingües y medir F2 primero, con presupuesto futuro expresamente autorizado. No hay razón experimental para lanzar50M parámetros ni1Btargets ahora.
