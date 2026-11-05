# Composición real

| Fuente | Idioma declarado | Dominio | Split | Documentos BASE curados1B |
| --- | --- | --- | --- | --- |
| HuggingFaceFW/fineweb-2 | es | web | dev | 2218 |
| HuggingFaceFW/fineweb-2 | es | web | test | 3524 |
| HuggingFaceFW/fineweb-2 | es | web | train | 329574 |
| HuggingFaceFW/fineweb-edu | en | educational-web | dev | 1408 |
| HuggingFaceFW/fineweb-edu | en | educational-web | test | 1366 |
| HuggingFaceFW/fineweb-edu | en | educational-web | train | 145212 |
| HuggingFaceTB/finemath | en | math | dev | 267 |
| HuggingFaceTB/finemath | en | math | test | 183 |
| HuggingFaceTB/finemath | en | math | train | 40708 |
| python/cpython | zxx | code | train | 7 |
| wikimedia/wikipedia | en | encyclopedia | dev | 148 |
| wikimedia/wikipedia | en | encyclopedia | test | 151 |
| wikimedia/wikipedia | en | encyclopedia | train | 15392 |
| wikimedia/wikipedia | es | encyclopedia | dev | 171 |
| wikimedia/wikipedia | es | encyclopedia | test | 163 |
| wikimedia/wikipedia | es | encyclopedia | train | 15422 |

Idiomas según metadatos heredados/LID, no nueva clasificación independiente. Código=zxx CPython; prosa web/enciclopedia/educación/math tienen etiquetas de dominio, no una segmentación exacta de código incrustado. No se inventa un porcentaje exacto de código dentro de páginas mixtas. Los bytes y longitudes por vista están en [integrity](results/integrity.json), cuantiles completos0/25/50/75/90/99/100%.

El SFT765 separado incluye525ES/240EN; no se añade al BASE. La mezcla masiva dispone de español e inglés, pero la selección aprobada paraF2 conserva solo inglés de código/exposición. No imponer proporciones bilingües sin derechos cerrados.
