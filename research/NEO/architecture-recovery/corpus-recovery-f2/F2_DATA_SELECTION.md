# SelecciónF2 preparada y bloqueada

Manifiesto reproducible de referencias: [f2-selection.json](results/f2-selection.json). No incluye texto bruto. Fuentes, SHA de documento, ruta original, licencia, split, dominio, idioma y conteosV3 exactos por archivo.

Train3Click: **25,355targets**; dev2Requests: **8,637targets**. Déficit frente5M: **4,974,645**. Usar197pasadas no sustituye diversidad. No se incorporaron textos en cuarentena ni SFT; CPython tiene reserva de test. No se creó un dev con chunks del mismo documento del train.

Esta selección reutilizaD0.1 como smoke/regresión técnica, no satisface el pilotoF2 bilingüe/diverso. La mezcla grande localizada es suficiente en volumen estimado, pero su selección utilizable no está aprobada. Primero cerrar derechos/atribución y dedup/splits de un subconjunto de las fuentes existentes; después manifestar y contar ese subconjunto. No hace falta descargar otro corpus ni completar todos los tokens del maestro para esa decisión.

`python corpus-recovery-f2/selection.py --check-training-gate` aborta sin entrenar. No hay configuración que rellene el déficit por repetición ni promoción silenciosa deWikipedia/web.
