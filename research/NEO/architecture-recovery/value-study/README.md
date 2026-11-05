# Diagnóstico de representaciones de Hielo

Worktree `cryo-value-representation-study`, rama `cryo-value-representation-v1`, origen198b681. Modelos históricos y24checkpoints del estudio previo permanecen inmutables. Este estudio entrena solo decoders auxiliares CPU sobre estados congelados; no otra arquitectura, pretraining ni una política nueva de memoria.

- [Protocolo](PROTOCOL.md), [datos controlados](CONTROLLED_DATA.md), [extracción](STATE_EXTRACTION.md).
- [Decodificación](VALUE_DECODING.md), [escritura](WRITE_PATH.md), [lectura](READ_PATH.md).
- [Intervenciones](CAUSAL_INTERVENTIONS.md), [filtro](FILTER_DIAGNOSTICS.md).
- [Causa identificada y límites](ROOT_CAUSE.md), [decisión mínima](NEXT_DECISION.md).
- `results/`: características de estados locales `.pt`, métricas/predicciones JSON, curvas CSV, intervenciones y trazas numéricas. Los `.pt` se ignoran enGit, se inventarían porhash al cerrar.

El diagnóstico principal usa nuevos layouts y un panel balanceado por entidad. El suplemento composicional, declarado post-hoc, cambia la identidad del distractor manteniendo posiciones; no reemplaza el dev estructural. La presencia puede ser localmente evidente en ejemplos borrados; los valores se evalúan solo cuando están presentes.

## Reproducir

```bash
cd /PATH/TO/NEO_HOME/research/neo-architecture-recovery/cryo-value-representation-study
bash value-study/run.sh
```

Un solo worker y un thread, CPU FP32. Se requiere el entorno local indicado por el script y los checkpoints existentes en el worktree original; `extract.load_model` fija esas rutas explícitas. Nunca se descargan ni copian pesos deA4. Los finales sellados no se leen. No hay CUDA, AMP, Vast.ai ni gastos. Los scripts de extracción/probes omiten artefactos completos; conservarlos y sus manifests en lugar de borrar resultados para reanudar.

Los probes por entidad ofrecen capacidad adicional al lector original. Decodificabilidad no acredita que CryoCCM utilice esa información; fracaso del decoder no demuestra ausencia absoluta de cualquier codificación.

## Resultado de cierre

Hielo contiene presencia fácilmente decodificable y señales parciales de valores, pero no una asociación vigente robusta. Probes lineales dev: valor29,69% histórico/32,60% Event/29,38% Delta frente a25% azar; presencia98–100%, también alta en inicializaciones. El control explícito100% y presencia sola25% delimitan la capacidad del decoder.

Los nueve modelos fallan la prueba conjunta de intercambio válido (0/120por modelo). No se certifica «Hielo almacena bien, solo arreglar lectura». Se propone una única intervención de supervisión auxiliar de asociación, todavía no ejecutada, sin nueva arquitectura. [Resumen por semillas](REPRESENTATION_SUMMARY.md), [causa y límites](ROOT_CAUSE.md), [siguiente decisión](NEXT_DECISION.md).
