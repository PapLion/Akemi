# Contratos y preservación

Antes de entrenar: tests de pares/multiconjuntos y balance, causalidad train/eval, independencia batch, alineación siguiente-token, gradientes de consulta/prefijo, parámetros/AdamW, etiqueta fuera del forward, checkpoint y reanudación exacta continua8updates contra3+5 en ambos formatos. Se compararon pesos, AdamW, RNG Torch/Python y cursor/orden. Ingeniería con fixtures de8updates, separada de los200updates por brazo.

Siete tests reproducibles adicionales PASS: tokenización de cuatro nombres, datos emparejados, atención real, checkpoint/optimizador, causalidad/labels, reanudación exacta y swaps oraculares. Las tolerancias se fijaron en código antes de ejecutar. No se trasladó certificado CUDA/BF16: soloCPUFP32 monoproceso.

Modelo/Block/tokenizer importados sin editar.13tensores activos; AdamW completa cobertura, gradientes finitos y parámetros cambian. Checkpoints guardan modelo, AdamW, RNG, dataset/cursor/orden, tokenizer y hash fuente, acumulación1 y schedulerNone. Su campo protocol es el heredado V2 del runner e incluye metadatos históricos; PROTOCOL.json de esta carpeta y cursor200 son la configuración efectiva del contraste, vinculados por manifest. No se confunden los campos400updates heredados con el entrenamiento ejecutado.

Una primera instrumentación de masa por hecho detectó una diferencia de segmentación BPE al tokenizar cada frase por separado (espacio fusionado con entidad siguiente). Ocurrió ANTES de todo entrenamiento principal. Se conservó el fallo en results/diagnostic-attempt-0/, se corrigió únicamente el corte de spans del diagnóstico sobre los IDs reales y se comprobó la reconstrucción contra atención real. No se cambiaron datos, modelo, umbrales ni entrenamiento para ocultar un resultado. El preflight de ingeniería se repitió; no se repitieron entrenamientos principales.

Sin Hielo entrenado, sin Trapos, GPU, servicios pagados, Chinchilla ni acceso al confirmatorio sellado. Los resultados anteriores y fuentes permanecen intactos. SHA256SUMS cubre código, configuración, resultados y checkpoints locales; no se lee ningún cuerpo sellado.
