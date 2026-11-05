# Foreground Contextual Binding V1

Semilla 17; CPU FP32, un thread; 400 updates finales fijos por brazo, batch 8, LR 0,003, clipping 1. Sin Hielo ni Trapos.

Ejecutado: tres brazos y 1.200 updates totales. Resultado negativo frente a las compuertas prospectivas: no existe control positivo neuronal de binding. La segunda capa contextualiza, pero no aprende recuperación fiable con esta receta.

Ver [DECISION.md](DECISION.md), [TRAINING_RESULTS.md](TRAINING_RESULTS.md), PROTOCOL.json y results/.

Reproducción: ejecutar reproduce.sh desde este worktree. Se rechaza sobrescribir evidencias existentes; usar una copia limpia de la rama y retirar únicamente results/ de esa copia. Las importaciones históricas permanecen de solo lectura. Dependencias: entorno CPU existente de viability, sin instalación ni GPU.
