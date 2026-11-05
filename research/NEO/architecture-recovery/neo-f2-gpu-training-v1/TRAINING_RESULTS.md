# Entrenamiento F2 ejecutado

Checkpoint final fijo, sin selección por dev. **4,922,444 targets** en 19,878 updates; una pasada, máximo 5M no excedido. La diferencia frente a 5M son 77.556 targets; no se rellenó repitiendo datos. Nueve artículos excluidos por marcadores explícitos de derechos, sin cambiar fuente ni tokenizer.

NLL online ponderada durante optimización: 6.059438. NLL final de muestra train fija (31658targets): 5.813831. Esas dos magnitudes no se confunden con NLL sobre todo train al checkpoint final. Curvas numéricas completas por update en private/download/results/F2/curve.jsonl y copia local results/F2-curve.jsonl (fuera de Git); CSV por grupos de 100 updates y SVG para revisión; checkpoints periódicos aproximadamente cada 1M targets y final.

AdamW, RNG CPU/CUDA/Python, identidad y cursor/orden de datos presentes. NumPy se usa solo para lectura, sin RNG de NumPy en la trayectoria; numpy_rng=None no omite una fuente aleatoria utilizada. Checkpoints solamente en fronteras de update, sin acumulación parcial. Validación local de carga/inferencia y estados en results/F2-local-verification.json.

El checkpoint final conserva el mismo SHA antes y después de recuperar la evaluación/generación. No se modificaron dimensiones, capas, batch, LR, clipping ni objetivos durante entrenamiento. Gradientes finitos verificados en cada update. No se entrenó Hielo ni Trapos.
