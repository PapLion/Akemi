# Decisión científica

|Brazo / split|Inicial rol A|Inicial rol B|Conjunta inicial|Conjunta posterior|Conjunta retenida|Lector original|
|---|---:|---:|---:|---:|---:|---:|
|A / train|40.00%|43.75%|16.25%|13.75%|13.75%|35.94%|
|A / dev-layout|43.12%|41.88%|14.37%|14.69%|12.50%|35.94%|
|B / train|44.38%|47.50%|15.00%|15.00%|11.56%|32.81%|
|B / dev-layout|45.62%|45.62%|14.37%|13.75%|11.88%|31.56%|

**Resultado compatible con caso A bajo esta receta:** el brazo sin supervisión posterior ya falla en formar dos asociaciones fiables. No observamos que A aprenda y B destruya ese aprendizaje. B mejora marginales iniciales de40/43.75% a44.375/47.5%, pero conjunta baja16.25→15.00%; una semilla no justifica afirmar mejora o daño causal generalizable.

1. No se demostró aprendizaje robusto de dos bindings simultáneos con150updates; hay señal parcial superior al azar de referencia. No equivale a incapacidad representacional absoluta de DeltaFast.
2. Añadir CE posterior no revela una degradación grande y consistente de formación inicial. Cambia señal total y clipping; no es igualdad de carga de optimización.
3. La asociación no modificada no se conserva de manera fiable; revisar métricas afectada/no modificada y conjuntas.
4. Corrección y conservación simultáneas tampoco se demostraron.
5. Lector original train35.94% A/32.81% B, frente25% nominal; intervenciones de estado vigente no acreditan recuperación fiable. Mejoras del decoder no se interpretan como uso funcional.
6. **Siguiente contraste mínimo:** mantener la arquitectura y supervisión inicial únicamente; situar las dos escrituras en un mismo chunk frente a chunks diferentes, con igual número total de chunks, ambos supervisados al mismo límite después de las dos escrituras, valores/órdenes/targets/receta iguales. Esto aislaría la compresión de dos hechos juntos frente a acumulación recurrente entre chunks. No se ejecutó ni se modificó el modelo para forzarlo.

No se ha aislado una gate, el borrado ni una causa única. Formación/representación, capacidad del decoder y dificultad de optimización siguen parcialmente mezcladas. La pérdida de respuesta común también permanece activa. No iniciar600updates, rediseño ni promoción arquitectónica por esta semilla.
