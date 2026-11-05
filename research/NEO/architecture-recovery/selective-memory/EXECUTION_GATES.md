# Compuertas del estudio

|Compuerta|Estado|Evidencia|
|---|---|---|
|Conservación de fuentes históricas|PASS|Rama nueva desde b7d4b13; fuentes anteriores sin cambios|
|Oráculos, hashes y splits reproducibles|PASS acotado|verify_panel.py; finales no abiertos; misma implementación generadora, sin custodio independiente|
|Causalidad train/eval y aislamiento del foreground|PASS CPU FP32|Perturbaciones futuras, resets, batches y ausencia de gradiente del prefijo en controles sin memoria|
|Gradientes, AdamW y reanudación|PASS CPU FP32 monoproceso|Tests y validación de checkpoints después de updates|
|Aprendizaje mecánico|PASS acotado|Microfits v3; las seis condiciones memorizan10registros; no prueba de generalización v5|
|Aprendizaje de correcciones genuinas|FAIL observado|0/42 en cada uno de18modelos primarios; incluye24cambios dentro del soporte train|
|Estado Hielo funcional|PASS parcial|Reset/intercambio reduce exactitud; no identifica contenido de valores|
|Panel sin atajos relevantes|BLOCKED|Control de presencia sin valores53,33%; priors entidad–respuesta|
|Selección aprendida de Trapos útil|NO DEMOSTRADA|Ablaciones y contrafactuales no acreditan la capacidad buscada|
|Promoción de EventFast/DeltaFast|BLOCKED|Velocidad no sustituye utilidad de valores|
|Confirmación independiente/final sellado|NO EJECUTADA|No consumir antes de resolver controles|
|Lenguaje/GPU/AMP/distribuido|FUERA DE ALCANCE|No se ejecutaron ni certificaron|
