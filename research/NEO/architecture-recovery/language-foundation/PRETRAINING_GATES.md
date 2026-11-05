# Compuertas de pretraining

| Compuerta | Estado |
|---|---|
| BPE8K carga/hash/roundtrip local | PASS de ingeniería; provisional lingüísticamente |
| Foreground/base causal128, shift, padding, aislamiento | PASS CPU del piloto |
| AdamW, gradientes, RNG/cursor, checkpoint seguro | PASS CPU monoproceso FP32; no GPU/DDP/AMP |
| Generación técnica | PASS; utilidad/calidad FAIL |
| Dataset piloto procedencia/permisos | PASS limitado Click/Requests y obligaciones preservadas |
| Corpus lingüístico ES/EN diverso y licencias suficientes | BLOQUEADO |
| Dev representativo por fuentes/idioma/dominio | BLOQUEADO; solo2archivos códigoEN |
| Revisión humana/PII/calidad amplia/contaminación near-duplicate | PENDIENTE |
| Base lingüística útil y generalización composicional | NO DEMOSTRADA |
| Dimensionamiento y benchmark F2/F8 | PROPUESTO, NO EJECUTADO |
| Presupuesto nuevo de entrenamiento significativo/GPU | NO AUTORIZADO |
| Utilidad lingüística Hielo / Trapos | Hielo no validado en lenguaje; Trapos congelado |

No iniciar pretraining significativo. Bloqueos concretos: datos con cobertura y derechos, dev independiente suficiente, base que produzca continuación útil, presupuesto/throughput de modelo candidato y nuevos contratos para el entorno elegido. No convertir la falta de Trapos en veto permanente al base LM: se puede investigar base causal sin memoria, integrarla después. No se cambia CURRENT_READINESS histórico; esta rama contiene su propio estado.
