# Datos y exposición

Se filtra el generador histórico sin modificar tokens, plantillas ni campos. Dos valores son los del nivel3, índices0/1 (red/white); cuatro incluyen black/gold. Orden0 conserva Nora antes de Iris; orden1 los invierte. Consultas a ambas entidades, valores distintos, todas las parejas ordenadas posibles y NeoToken V3 BPE8K intacto.

Número verificado: A4 respuestas/2 historias; B24/12; C8/4; D48/24. Tamaños explicados por m×(m−1)×órdenes×2 consultas. A coincide byte a byte lógico (JSON) con nivel3; D con nivel4; hashes exactos en frequencies.json. Todas las longitudes train son119 IDs válidos, padding128. No hay datos futuros ni respuesta dentro del forward.

Todos reciben3200 targets,400 updates,batch8. Mismo muestreador histórico: permutación seed17 repetida. A800 ciclos completos, C400; B133 ciclos+8 respuestas, D66 ciclos+32. Valores efectivos A/C1600 por valor; B801/800/799/800; D803/800/797/800 según identidad registrada. Dataset y ciclos completos balanceados; último ciclo B/D no perfecto. Alterarlo impediría reproducir el protocolo histórico D. Esta tensión se documentó antes de entrenar, no se sustituyó silenciosamente el sampler.

Diversidad y exposiciones por ejemplo cambian: A800 por respuesta, C400, B133–134, D66–67. No es igualdad de exposición por ejemplo ni de pasadas. El factorial identifica cambios de distribución bajo un presupuesto total fijo.

No se reservaron combinaciones dentro de train: se exigen fixtures factoriales exhaustivos e identidad D. Generalización se mide aparte: estructura verbal alternativa, nuevo par que incluye Mira nunca entrenada, y orden opuesto solo para A/B. El nuevo par no aísla combinaciones conocidas: también introduce entidad nueva. No se abrieron confirmatorios sellados. Frequencies.json incluye frecuencias condicionadas, órdenes, targets y todos los IDs.
