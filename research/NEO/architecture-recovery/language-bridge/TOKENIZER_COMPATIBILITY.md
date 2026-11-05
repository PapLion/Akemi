# NeoToken V3: compatibilidad medida

Artefacto real preexistente `../neotoken-v3/artifacts/bpe-8192.json`, fingerprint `813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b`, 80964 bytes. Carga JSON restringida y fingerprint esperado, sin pickle. Algoritmo byte BPE, vocab8192; bytes0…255, controles256…266, reserva267…511, merges512…8191. PAD256/BOS257/EOS258 explícitos. Sin UNK ni normalización Unicode destructiva. Los controles literales en texto no inyectan roles especiales.

Tests ejecutados: encode_reference Python = encode nativo sobre ES/EN, código, Unicode; roundtrip exacto acentos, emoji, combinaciones, NUL, espacios, Markdown/control literal y fórmulas; bytes0…255 por encode_bytes/decode_bytes; vacío; recarga con IDs iguales; rechazo de surrogates y controles en token_bytes; StreamingEncoder con trozos1/2/7bytes y StreamingDecoder incremental. PASS en release-tests.log.

Una tokenización BPE completa de un prefijo puede cambiar en su última pieza al añadir texto: no se promete que encode(prefijo) sea prefijo literal de encode(texto completo). El encoder streaming retiene piezas abiertas y emite IDs equivalentes al texto completo al terminar. La causalidad del modelo se prueba sobre los IDs fijos ya adquiridos; ninguna vista calculada con el futuro entra al forward.

Prueba local de216.000 bytes: encode 1139152 bytes/s, decode 16504862 bytes/s. Repetición corta, no benchmark exhaustivo de corpus. Estructuras multiescala existen como sidecars, incluidas rutas offline; no se consumen aquí ni se les atribuye causalidad sin contrato.

**Apto mecánicamente para este smoke test**, todavía candidato provisional: código, conversación, compresión óptima y selección de vocabulario final no certificados universalmente. V1/A4 intactos; ninguna migración de IDs o embeddings históricos.
