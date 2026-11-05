# Datos y contratos

Se reutilizan literalmente A (4 respuestas) y C (8 respuestas / 4 historias) del factorial histórico. Nora/Iris, rojo/blanco según IDs originales; las dos consultas de cada historia están balanceadas, valores distintos. Targets solo fuera del forward. Cada minibatch C contiene exactamente los ocho ejemplos; A repite sus cuatro dos veces.

Ambos brazos reciben 5600 respuestas. Directo: 2800 por orden. Currículo: 4000 orden original, 1600 inverso; esta diferencia de exposición es deliberada. Últimos 400 batches idénticos, comprobados por SHA en exposure.json. No igualdad de datos en los primeros300.

Los devs heredados son layout verbal nuevo y par Nora/Mira (incluye una entidad nueva, no solo recombinación). No existe una reserva composicional interna adicional en el fixture exhaustivo de dos valores. No se abrió ningún conjunto sellado. Frecuencias y dataset completos en results.

Tests históricos: tres PASS (datos, causalidad/máscaras/target/AdamW/gradientes, reanudación). Nuevos contratos: estados reales AdamW300, continuación 300→304 idéntica con interrupción/restauración302 en ambos brazos; parámetros, optimizer, RNG y cursor exactos. Esto certifica la frontera, no una comparación independiente completa de 700 updates interrumpidos.

Verificación posterior: los seis checkpoints 0/300/700 reproducen exactamente las métricas guardadas tras recarga, con contadores AdamW correctos. La primera comprobación de igualdad de diccionarios encontró claves enteras frente a cadenas serializadas en JSON; se corrigió únicamente la comparación canónica JSON, sin tocar valores, tolerancias, pesos ni entrenamiento. Resultados en reload-verification.json.
