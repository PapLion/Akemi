# Conteos NeoTokenV3 BPE8K

Artefacto `8489cd9a98fb4a7339fe802be74621774f2ee68b465cfb0b16846a07fe99a156`, fingerprint `813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b`. PAD256/BOS257/EOS258. RoundtripES/EN/Unicode y determinismo comprobados, artefacto intacto. Solo núcleoBPE; no vistas multiescala como entradas adicionales. Tokens del BPE pueden cambiar al añadir sufijos de texto por merges: el contrato causal opera sobre la secuencia tokenizada fijada, no promete estabilidad de prefijos arbitrarios de caracteres.

Conteo nuevo **exacto parcial:** 287,911IDs en120documentos masivos únicos; 893,559bytes y884,030caracteres. Además33.987IDs de texto en5documentosD0.1, con25355train/8637dev targetsBOS/EOS. Certificados content-addressed reanudables enSQLite local, no tokensV1 reutilizados comoV3.

| Fuente | Idioma | Docs muestra | IDs exactos | IDs/byte | IDs/carácter |
| --- | --- | --- | --- | --- | --- |
| HuggingFaceFW/fineweb-2 | es | 24 | 19021 | 0.2957 | 0.3015 |
| HuggingFaceFW/fineweb-edu | en | 24 | 38264 | 0.2902 | 0.2911 |
| HuggingFaceTB/finemath | en | 24 | 49971 | 0.4303 | 0.4333 |
| python/cpython | zxx | 0 | 0 | pendiente | pendiente |
| wikimedia/wikipedia | en | 24 | 108248 | 0.3177 | 0.3199 |
| wikimedia/wikipedia | es | 24 | 72407 | 0.3011 | 0.3072 |

Muestra fija uniforme por estrato,24documentos por fuente/idioma/dominio, seed17005. Estimación exploratoria de los estratos no-code curados1B: **705.69M ±160.75M** (intervalo normal95%, muestras pequeñas/colas pesadas). No es conteo certificado ni intervalo robusto en colas; siete documentosCPython reservados quedan fuera de esa estimación. No trasladar esta estimación al bruto o500M.

No hay totalV3 exhaustivo, tokens aprobados masivos ni desglose exacto global por idioma/fuente. [v3-counts](results/v3-counts.json) conserva cada certificado de muestra, pendientes y estimaciones por estrato; [v3-summary](results/v3-summary.json) separa cobertura. Reejecutar`count_v3.py` reutiliza certificados; aumentar muestra es una decisión explícita, no un contador completo oculto. Para terminar el total se debe extender la cola a todos los documentos únicos con checkpoint, previa política de reservas. El corpus entero no necesita completarse antes deF2: sí es obligatorio contar exactamente la selección aprobada suficiente.

Targets futuros: por documentoBOS+texto+EOS→n_text+1, ventanas stride=context−1 cubren cada target una vez, padding/fronteras enmascarados. IDs únicos, targets y exposiciones no son sinónimos. El presupuesto5M no está cubierto con repeticiones.
