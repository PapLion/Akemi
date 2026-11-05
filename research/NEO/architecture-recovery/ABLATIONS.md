# Controles de arquitectura y ablaciones

Se entrenan diez brazos con seeds17/29/43, índices de batch idénticos por semilla y presupuesto de targets idéntico. Tabla completa en `LEARNING_RESULTS.md` y CSV por tarea. Los resultados negativos no se excluyen.

| Brazo | Diferencia de información/cómputo | Qué permite preguntar |
|---|---|---|
| b0_local | Atención solo dentro del fragmento8 en aprendizaje | Control sin acceso a antecedentes; no es una comparación suficiente por sí solo |
| b0_full | Ve los mismos64tokens completos que Hielo y CryoTiny | Control con información visible equivalente, sin memoria latente |
| cryo_history | CryoTiny anterior completo, recurrencia por token | Referencia congelada, FFN/posición distintos y más parámetros |
| event / delta | Backbone local idéntico, Hielo por fragmentos | Si la memoria compacta facilita generalización contextual |
| event_no_memory | Sin lectura/escritura, módulos ineficaces congelados | Contraste de capacidad de memoria, no igualdad de parámetros entrenables |
| event_no_filter | Resumen uniforme, lectura1, borrado/escritura1 | Filtrado conjunto frente a actualización indiscriminada; confunde varios submecanismos, no atribuir efecto a uno solo |
| event_always_write | Escritura1; señales irrelevantes congeladas | Necesidad de regular escritura frente a sobrescribir cada fragmento |
| event_no_persist / delta_no_persist | Estado cero al empezar cada fragmento | Dependencia de transportar antecedentes; parámetros de memoria congelados por no existir trayectoria útil al loss |

Las ablaciones son **modelos entrenados desde inicialización comparable**, no simplemente apagar memoria en inferencia. `probes.py` añade intervenciones de inferencia identificadas por separado. Delta soporta también no_memory/no_filter/always_write en código, pero no se entrenaron esos brazos: no se presentan como resultados medidos.

Todos comparten embeddings iniciales y Event/Delta/control nuevo comparten exactamente el backbone. Los parámetros añadidos no se igualaron quitando capacidad aB0. B0local/full272.480; Event281.953; Delta276.259; CryoTiny285.952. Los embeddings atados ocupan262.144 parámetros: son prototipos mecánicos pequeños, no modelos de12M.

Control por targets y por información disponible ejecutado. **Control de entrenamiento igualado por FLOPs o wall-time no ejecutado.** Se miden costes CPU separados y se conservan diferencias; no se atribuye una eventual ventaja a la arquitectura sin ese control. Tampoco se selecciona la semilla ganadora ni se agregan entradas multiescala a un único brazo.

Resultado observado a1.000updates: ambos mecanismos nuevos mejoran ajuste train respecto al control local (Event44,87%, Delta36,98%, B0local29,84%) pero todos esos brazos obtienen0%dev. No es evidencia de retención generalizable ni de ventaja útil del filtrado. CryoTiny de referencia llega a60,12%dev medio, aunque sus mayores diferencias de cómputo/backbone impiden identificar la causa.
