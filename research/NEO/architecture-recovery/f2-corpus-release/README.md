# F2 Corpus Release V1 — BLOCKED

Se ejecutaron clasificación, atribución, conteo exhaustivo de una selección candidata bilingüe y certificación del lector con documentos aprobados. No se entrenó F2.

- [Decisión](DECISION.md), [derechos](SOURCE_RIGHTS_MATRIX.md), [condiciones pendientes](REMAINING_BLOCKERS.md).
- [Selección y conteos exactos](NEOTOKEN_V3_EXACT_COUNTS.md), [lector](DATA_READER_CONTRACTS.md).
- Base ddbd348; rama neo-f2-corpus-release-v1. Ningún archivo histórico fue modificado.

Reproducir: `python f2-corpus-release/release.py` con el entorno V3/PyTorch existente; `python f2-corpus-release/reader.py`; `python -m unittest discover -s f2-corpus-release -p 'test_release.py' -v`. release.py reutiliza certificados por SHA; no entrena ni descarga corpus. Solo recupera cuatro documentos pequeños de evidencia oficial. SQLite/token arrays y checkpoint de integración permanecen locales, fuera de Git.

Los manifests condicionales NO habilitan el entrenamiento: Reader exige APPROVED. El entrenamiento significativo sigue desautorizado.
