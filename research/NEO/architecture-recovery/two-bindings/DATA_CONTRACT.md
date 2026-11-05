# Fixture único y splits

320 programas train:5pares cíclicos de entidades×16pares de valores×2órdenes×2eventos. Cuatro valores0–3; todas las parejas de valores por par de entidades aparecen4veces. Consulta rota sobre5entidades; la otra es sucesora cíclica. No cubre todas las20parejas ordenadas de entidades.

15registros DSL4IDs y consulta4IDs=64. Inicialización en registros0/1 o2/3 según orden, independiente de valores; evento en6. Ambos facts caen en el mismo chunk de8IDs. Memoria capturada tras ambos facts (chunk0/1), tras evento(chunk3), y antes de consulta(chunk6). Foreground local16 sin KV. Los otros registros son propuestas rechazadas~; aun así su procesamiento genera actualizaciones suaves de Hielo, no son cómputo omitido.

Evento preserve repite valor de entidad afectada; correct lo cambia con desplazamiento1–3 fijado por identidad. Entidad afectada depende de identidad/orden, no del valor. Se registran esas dependencias: no se presenta como panel totalmente libre de pistas de operación. Oráculos causales recalculados por prefijo, ausencia nunca supervisada, exactamente2targets iniciales y2posteriores. A enmascara etapa posterior entera; B no.

Dev320 mueve inicialización a4/5 y evento a10, e invierte orden emparejado. IDs documentales disjuntos. Comparte valores, identidades y combinaciones: evalúa layouts/orden relativo nuevos, no generalización léxica/composicional independiente. Ambos órdenes ya existen en train; no afirmamos orden categórico jamás visto. No es evaluación final sellada.

Frecuencias reales por etapa/chunk/entidad/valor/evento en frequencies.json; marginales entidad–valor balanceados incluso tras corrección. Programas completos train.json/dev-layout.json y hashes preservan trazabilidad.
