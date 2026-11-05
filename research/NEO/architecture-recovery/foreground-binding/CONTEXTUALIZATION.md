# Contextualización

Se registraron entradas/salidas reales de bloques, Q/K/V, atención final y logits, antes/después del entrenamiento en todas las historias de los tres paneles. Los cambios contrafactuales intercambian nombres en los hechos conservando tokens de valor y consulta. Embedding del valor permanece idéntico; su salida contextual cambia.

Ejemplo registrado B final: diferencia máxima salida bloque1 en posiciones de valor0,0538354; entrada del bloque2 idéntica a esa salida; diferencia K del bloque2=0,0012852 y V=0,00076294. En bloque1 K/V de valor no cambian (0). Diferencia Q al cambiar consulta:1,3271 capa1 y1,6435 capa2. Atención relativa hacia hechos cambia0,16368/0,13994. Son magnitudes de un ejemplo, no tasas de comprensión ni prueba causal de aprendizaje.

Ambos bloques reciben gradientes de respuesta, incluidos Q/K/V y MLP. Contextualización implementada y sensible no equivale a binding utilizado: B obtiene0/12 intercambios estrictos. Evidencias completas *-contextualization.json, contextualization-summary.json y contextualization-states.pt. No se entrenaron probes ni se utilizó información del oráculo en el forward.
