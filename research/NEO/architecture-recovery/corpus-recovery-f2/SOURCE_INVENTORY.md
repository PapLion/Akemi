# Inventario de fuentes y procedencia

| Fuente | Decisión nueva | Evidencia local | Condición |
| --- | --- | --- | --- |
| python/cpython | APROBADO | metadata/CPython-LICENSE.txt; CPython-sources.json file SHA | Retained7 quality-approved files; EXCLUDE F2 training due historical D0 CPython test-family reservation |
| wikimedia/wikipedia | CUARENTENA | metadata/wikimedia--wikipedia.md; original curation rights audit | Attribution/share-alike and per-document provenance conditions not closed; public availability is insufficient |
| HuggingFaceFW/fineweb-2 | CUARENTENA | metadata/HuggingFaceFW--fineweb-2.md | Collection metadata does not clear underlying web rights |
| HuggingFaceFW/fineweb-edu | CUARENTENA | metadata/HuggingFaceFW--fineweb-edu.md | Same underlying-document rights gate |
| HuggingFaceTB/finemath | CUARENTENA | metadata/HuggingFaceTB--finemath.md | Underlying web rights unresolved |
| OpenAssistant/oasst1 | CUARENTENA | metadata/OpenAssistant--oasst1.md | 765 SFT separate; individual provenance/PII and conditions unresolved; never auto-convert to BASE |
| D0.1 Click | APROBADO | data/d0.1/raw/click-LICENSE.rst; accepted.jsonl file hashes | BSD-3-Clause, preserve notices; original train family |
| D0.1 Requests | APROBADO | data/d0.1/raw/requests-LICENSE; accepted.jsonl file hashes | Apache-2.0, preserve notices; original dev family |
| D0.1 Gutenberg/OASST | CUARENTENA | language-foundation/DATA_READINESS.md | Territorial/individual rights unresolved; no F2 use |
| quality/evaluation-conflict records | EXCLUIDO | curation decision manifests and read-only index | New F2 use prohibited; original preserved |

[Catálogo](results/catalog.json) conserva rutas, hashes, tamaños, fechas y estado. [Composición completa](results/integrity.json) identifica fuente/idioma/dominio/split de todos los registros verificados. Las versiones históricas solo-manifiesto se distinguen de las tres vistas verificadas por contenido. CONTEXTUAL está vacío en el bruto1B; SFT no es BASE.
