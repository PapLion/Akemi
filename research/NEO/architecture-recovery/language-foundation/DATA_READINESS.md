# Datos admisibles y límites

D0.1 contiene49 train y16dev registros; el inventario por categoría/licencia está en data-audit.json. Sus conteos históricos usan V1: no reutilizarlos como targets V3. Solo train/dev de accepted.jsonl; ningún archivo sealed/, test D0 o Chinchilla se abrió para este trabajo.

**Seleccionado para ingeniería local:** Click8.1.7 BSD3 train y Requests2.31 Apache2 dev; URLs resueltas a commits inmutables, archivos completos y licencias archivadas. Se verificaron SHA del texto y bytes fuente, licencia local, roundtrip, parse AST de cuatro archivos Python y documentación RST. Avisos de licencia preservados en notices/. Esta evidencia es más fuerte que una etiqueta de hub; no se ofrece certificación jurídica universal ni auditoría exhaustiva de todo contenido de terceros.

| Documento | Split | Idioma/dominio | Bytes | IDs con BOS/EOS |
|---|---|---|---:|---:|
| click-src_click_parser.py | train | en/code | 19067 | 7492 |
| click-src_click_types.py | train | en/code | 36391 | 14595 |
| click-docs_arguments.rst | train | en/exposition | 8398 | 3271 |
| requests-requests_structures.py | dev | en/code | 2912 | 1252 |
| requests-requests_cookies.py | dev | en/code | 18560 | 7387 |


Dos familias repositorio disjuntas. Cero hashes compartidos train/dev, cero pasajes normalizados de12 y64 palabras; no demuestra ausencia de toda paráfrasis ni contaminación histórica. Inicialización nueva para ambos modelos. Los documentos no se dividieron entre splits. No PII obvia por regex email; código público con procedencia específica, no datos personales de conversaciones.

**Excluido:**42 capítulos Gutenberg train y12 capítulos/ensayos dev: derechos condicionados territorialmente; no resueltos aquí. OASST4train/2dev: licencia de colección archivada, aportes individuales/PII/calidad pendientes, no autorizado por inferencia. Sintéticos y evaluaciones: no mezclados en el piloto. Los conjuntos finales sellados siguen cerrados.

Solo inglés, dos archivos de código train y un documento expositivo; dev únicamente código de otra biblioteca. ES no medido; narrativa y conversación ausentes. Es un subconjunto piloto admisible y pequeño, **no una dieta representativa ni corpus bilingüe listo**. No se rellena el vacío con texto sintético ni se descarga más corpus.
