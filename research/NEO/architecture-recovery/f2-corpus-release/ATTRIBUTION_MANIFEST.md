# Atribución materializada

results/attribution.jsonl contiene una entrada por artículo candidato: título, crédito a Wikipedia contributors, URL de artículo y de historial, licencia declarada y enlace, revisión HF, shard/fila, hash limpio y modificaciones conocidas. No contiene los textos.

El historial se enlaza para identificar contribuciones; no se afirma que el historial actual sea la revisión original extraída. La revisión HF fija los bytes del dataset. La modificación declarada incluye extracción mwparserfromhell y reparaciones históricas registradas. No se publica una lista ficticia de autores ni se elimina una atribución conocida.

Para Click/Requests se reutilizan los hashes y licencias de corpus-recovery-f2/results/f2-selection.json y los textos LICENSE locales. La atribución técnica generada no resuelve avisos adicionales perdidos durante extracción de contenido externo; external_attribution_review sigue PENDING.
