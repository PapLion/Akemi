# Integridad de datos medida

| Vista | BASE docs | BASE bytes UTF-8 | SFT separados | JSONL bytes almacenados |
| --- | --- | --- | --- | --- |
| raw1b | 564789 | 2501209022 | 765 | 3378133963 |
| curated500 | 257043 | 1219334156 | 765 | 1805875914 |
| curated1b | 555914 | 2349726579 | 765 | 3603101026 |

| Vista | Problemas medidos |
| --- | --- |
| raw1b | {"empty": 0, "text_sha_mismatch": 0, "byte_mismatch": 0, "missing_required": 0, "email_pattern_documents": 0, "private_key_or_token_pattern_documents": 0} |
| curated500 | {"empty": 0, "text_sha_mismatch": 0, "byte_mismatch": 0, "missing_required": 0, "email_pattern_documents": 0, "private_key_or_token_pattern_documents": 0} |
| curated1b | {"empty": 0, "text_sha_mismatch": 0, "byte_mismatch": 0, "missing_required": 0, "email_pattern_documents": 0, "private_key_or_token_pattern_documents": 0} |

Conteo exhaustivo por streaming, un registro enRAM, SHA dearchivo y texto, longitud UTF-8, JSON y campos obligatorios. Se guardan offsets/metadatos enSQLite derivado, sin duplicar texto. [Relaciones padre](results/integrity.json): `{"curated500": {"keys_without_master": 0, "same_key_changed_text": 2}, "curated1b": {"keys_without_master": 0, "same_key_changed_text": 3}, "500_not_in_1b_keys": 411}`. Diferencias de texto se verifican por key y SHA, no por coincidencia de tamaños.

Los detectores de email/secretos son patrones limitados; cero coincidencias no certifica ausencia de PII, teléfonos, direcciones, contenido sensible o benchmarks. Se reutilizan además las decisiones de calidad originales. Ambos índices refinados pasan `quick_check`; no equivale a auditoría legal ni semántica.

Errores de integración nuevos conservados enlogs: clave SHA distinta entre formatos de manifiesto; se adaptó el lector sin cambiar manifiestos. Errata del hash del tokenizer en el script nuevo corregida contra el artefacto y hash histórico idénticos. No se relajaron comparaciones ni se alteraron fuentes.
