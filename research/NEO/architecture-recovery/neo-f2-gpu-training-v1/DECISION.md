# Primer checkpoint F2 lingüístico completado

Se entrenó F2 sobre 4.922.444 targets reales ES/EN, sin repetición de relleno, Hielo OFF / Trapos OFF. Dev NLL 5.559083, PPL 259.585. Estado final y optimizador descargados, hashes cotejados y carga/inferencia CPU verificadas. La instancia fue destruida y la API confirmó ausencia. No se publicaron pesos ni corpus.

La reducción de NLL frente a inicialización muestra aprendizaje estadístico en ambos idiomas cuando así lo respaldan las métricas desglosadas; no se afirma comprensión. Generaciones completas congeladas en GENERATIONS.md permiten observar repetición y limitaciones sin escoger ejemplos bonitos. El dev es enciclopédico; no certifica otros dominios.

El siguiente escalón se justifica por curvas de aprendizaje, validación y comparación baseline, no por los microfits simbólicos. Antes de ampliarlo: revisar calidad/diversidad y obligaciones de publicación, replicación y presupuesto nuevo. No se inicia F8, Hielo lingüístico, Trapos, otra arquitectura ni entrenamiento adicional automáticamente. Los límites de derechos del release histórico siguen documentados: este uso privado concreto no es una aprobación general de distribución.

En este contraste el Transformer obtiene menor NLL dev (5.287873 frente a 5.559083) y 5.67% más targets/s de actualización. No hay evidencia aquí para preferir F2 al baseline. Antes de aumentar escala, usar el baseline como referencia y estudiar de forma aislada la contribución del refinamiento rápido o de la receta; no iniciar esa investigación automáticamente. Una semilla no establece superioridad general.
