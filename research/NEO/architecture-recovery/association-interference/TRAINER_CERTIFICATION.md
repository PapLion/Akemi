# Certificación ejecutada antes de entrenar

results/certification.json: causalidad train/eval, logits anteriores y Hielo chunk2 invariantes al modificar futuro desde ID24; independencia por permutación de batch; segundo documento concatenado equivale a sesión aislada; cobertura AdamW sin duplicados. Aux backward alcanza memory_head.value con gradientes finitos.

Reanudación real:3updates → torch.save → nueva instancia → torch.load(weights_only=True) →3updates. Comparación exacta con trayectoria continua6: parámetros modelo/decoder, estados AdamW, RNG torch/sampler, secuencia de índices y métricas por update. Cursor24 al corte, sin acumulación pendiente (microstep0, acumulación1), sin scheduler, dropout0. RNG Python global se guarda/restaura, no interviene en muestreo (Random17 dedicado). No certificado CUDA/AMP/multiproceso.

Identidad dataset por brazo en *.identity.json: el checkpoint tiene por error el hash de referencia fixtureA compartido; se documenta sin reescribir pesos. Los sidecars identifican datos efectivos y la configuración. El decoder se aplica solo al estado trazado, nunca al forward normal ni sus predicciones.

Verificación adicional posterior a los cuatro entrenamientos: padding invariante, CE auxiliar invariante a futuro, reconstrucción independiente exacta de identidad/orden de targets. No se afirma que estos tests adicionales se ejecutaran antes. Comparar prefijos de longitudes diferentes produjo error máximo2.98e-8: igualdad bit a bit falló; equivalencia pasa con tolerancia1e-5 ya usada para aislamiento documental. Se preserva esa limitación. Primer intento de importación falló por colisión del nombre experiment con un módulo histórico; se renombró el runner, sin modificar modelos ni repetir entrenamientos.
