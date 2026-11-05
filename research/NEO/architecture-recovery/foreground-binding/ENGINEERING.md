# Ingeniería

Siete tests PASS antes del entrenamiento: equivalencia original e inicialización homóloga; datos/tokenizer/oráculos; causalidad train/eval, aislamiento, padding y shift; gradientes y actualización AdamW; entrada contextualizada real al segundo bloque; reanudación exacta8 updates continua frente a3+5 con parámetros/AdamW/RNG/cursor/orden; determinismo eval.

La instrumentación comprueba además atención a ambos hechos, igualdad salida bloque1/entrada bloque2, y reconstrucción manual de atención frente a SDPA con atol2e-6/rtol1e-5. No se cambiaron tolerancias ni checkpoints. Carga weights_only=True y comparación de hashes de código/config/dataset/tokenizer. Ver tests.py, contextualization.py y engineering.json.

Los contratos son CPU FP32; no certifican CUDA/BF16. No hubo reparación de entrenamiento tras observar resultados. El wrapper de checkpoint usa metadatos del protocolo actual, no los metadatos heredados de otro experimento.
