# Recuperación ejecutada

Raíz real: `/PATH/TO/NEO_HOME/research/neo-architecture-recovery/chinchilla-corpus/`.

- Bruto: `releases/growth-1b-v1-estimated-1000000000/`.
- Curado500 preferido: `curation-v1/runs/500m-refined/release/`.
- Curado1B adicional encontrado: `curation-v1/runs/1b-refined/release/`.
- Versiones100M/250M/500M, stop y master-0001 siguen presentes. Solo documentadas a nivel manifiesto en esta ejecución, no recertificadas íntegramente.
- Ingesta/dedup/normalización/tokenización y logs recuperados: [pipeline-inventory](results/pipeline-inventory.json). Incluye hashes de los scripts y registros originales, sin reproducir su contenido.
- Metadatos de fuentes/licencias: `metadata/`; snapshotV1: `curation-v1/runs/500m/token-certificates-snapshot.sqlite`; cachéV1 actual `curation-v1/token-cache.sqlite`.

| Vista | BASE docs | BASE bytes UTF-8 | SFT separados | JSONL bytes almacenados |
| --- | --- | --- | --- | --- |
| raw1b | 564789 | 2501209022 | 765 | 3378133963 |
| curated500 | 257043 | 1219334156 | 765 | 1805875914 |
| curated1b | 555914 | 2349726579 | 765 | 3603101026 |

Inventario de versiones, fechasmtime y hashes: [catalog.json](results/catalog.json). SHA de cada shard: [shard-receipts.json](results/shard-receipts.json). No se localizaron respaldos externos adicionales dentro del ámbito de investigación/evaluaciones inspeccionado; sí versiones locales y snapshot. No se afirma que esa búsqueda abarque medios externos desconectados.

Las vistas curadas son subconjuntos por identidad del maestro, pero no copias textuales estrictas:500Mcontiene2reparaciones y1Bcontiene3. Además411keys del500Mcurado no figuran en1Bcurado; decisiones posteriores distintas, no datos perdidos. Verresults/view-differences.json.

La vista1B refinada existe y está íntegra a nivel de exportación. Esto actualiza el antiguo estado «curación en curso»; no significa aprobación de entrenamiento, derechos o conteo completo.
