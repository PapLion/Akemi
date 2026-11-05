# Deduplicación no destructiva

| Vista | Exceso duplicados texto SHA exacto |
| --- | --- |
| raw1b | 0 |
| curated500 | 0 |
| curated1b | 0 |

Las vistas se solapan por construcción. No sumar sus documentos/tokens. No asumir que500Mcurado es subconjunto estricto de1Bcurado:411identidades no retenidas en este último;3textos1B reparados frente al bruto. El muestreoV3 se cotejó contra los SHA de textos curados reales. Comparación de pertenencia por key y de contenido por SHA: `{"curated500": {"keys_without_master": 0, "same_key_changed_text": 2}, "curated1b": {"keys_without_master": 0, "same_key_changed_text": 3}, "500_not_in_1b_keys": 411}`.

Cercanos: se reutilizó el grafo histórico de curación, fingerprints y decisiones. Aristas registradas: [('500m-refined', 150809), ('1b-refined', 358268)]. Política v1.1: Jaccard.85, partial_shared_5grams64, partial_containment.2, bucket24 y pair_limit100000. No se certifica recall completo ni todas las versiones/forks posibles; no se ejecutó un análisis cuadrático nuevo.

La selección admisible de cinco documentos pasa dedupSHA y normalización whitespace, separación por repositorios y control de shingles train/dev: `{"5": 0, "12": 0, "64": 0}`. Compartir shingles cortos de código no prueba duplicación; cero64-gramas tampoco garantiza independencia semántica. CPython se excluye por familia histórica, incluso archivos/revisiones no idénticos.
