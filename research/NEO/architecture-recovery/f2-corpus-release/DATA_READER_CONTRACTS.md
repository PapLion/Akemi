# Contratos del lector adicional

reader.py solo acepta documentos APPROVED y verifica SHA, V3 y longitud. Una fila contiene una ventana de un documento; no existe atención ni target cruzado entre documentos. Orden barajado determinista semilla17; identidad del manifest y orden protegidos en estado. Un cambio de configuración o manifest falla al cargar cursor.

Se ejecutaron 4 updates técnicos continuos frente a 2+2 interrumpidos sobre documentos aprobados reales. Total computado: 6 updates al contar la repetición de comparación. Coincidieron exactamente parámetros, AdamW, RNG Python/Torch, cursor, pérdidas y claves/offsets de batches. Checkpoint local integration-resume.pt contiene estados completos e identidad del lector/tokenizer/código. La integración tiene dropout cero; aun así RNG se conserva. Se probaron causalidad real, aislamiento de filas, padding, shift, cobertura única de 25.355 targets y gradientes finitos.

Siete unittest PASS; results/reader-contracts.json y tests.log contienen evidencia. Se reutilizan sin repetir los nueve tests históricos F2/baseline. No es entrenamiento significativo ni experimento de calidad.

Límite: lector single-process, sin workers ni prefetch. Materializa tokens de los cinco documentos aprobados pequeños. El conteo candidato sí lee por streaming y guarda certificados por documento. El lector escalado de una futura selección aprobada bilingüe todavía no fue certificado: no se oculta como PASS. La config de entrenamiento permanece deshabilitada.
