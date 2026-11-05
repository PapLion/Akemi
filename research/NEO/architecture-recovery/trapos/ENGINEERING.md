# Contratos ejecutados

preflight.json certifica causalidad de logits y scores en train/eval, perturbación futura, máscaras, aislamiento por batch y documentos, resets, parámetros iniciales idénticos, cobertura exacta AdamW, no escritura al rechazar y ecuación Delta conservada al aceptar. BCE produce gradientes no nulos en ambas capas del filtro y una actualización real AdamW modifica sus pesos.

La trayectoria CPU de 10 updates es idéntica a 4 + checkpoint + 6 en los cuatro brazos, incluidos parámetros, AdamW, RNG, cursor y orden materializado. La política aleatoria es determinista y causal por documento. C rechaza oracle_mask. Checkpoints con weights_only=True, carga strict=True; configuración, dataset SHA, fuente SHA y código SHA guardados.

La colisión inicial de nombre `run` con un módulo histórico se corrigió antes del freeze: los módulos nuevos tienen prefijo trapos_. El fallo original permanece en preflight-import-failure.log. No se modificó código histórico para resolverlo.

El certificado se limita a CPU FP32 y el DSL implementado. No acredita CUDA, AMP, entrenamiento lingüístico ni un filtro semántico general.

Cierre: final-integrity.json verifica restauración exacta de los cuatro checkpoints finales y AdamW, inicializaciones idénticas, hashes de los tres checkpoints históricos intactos y archivos preregistrados sin modificaciones. El Jacobiano del foreground final respecto al prefijo oculto es exactamente cero en el fixture medido; Hielo es la ruta declarada de acceso. final-checks.log: FINAL CHECKS PASS.
