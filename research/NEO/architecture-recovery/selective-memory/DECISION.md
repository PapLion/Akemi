# Decisión: memoria funcional, selección de valores no demostrada

## Respuesta científica

**Esta ejecución no demuestra que Trapos/Hielo conserve y actualice valores relevantes de forma fiable.** Sí demuestra gradientes, persistencia causal y efecto funcional de la memoria. Esas propiedades no equivalen a resolver la tarea que motivó el diseño.

Se completaron seis condiciones primarias × tres semillas ×1000updates con órdenes emparejados. Además, Delta recibió dos políticas de escritura entrenadas por separado: permanente y aleatoria, tres semillas cada una. Las24trayectorias principales/ablaciones representan24000updates y192000respuestas supervisadas; pilotos rechazados y microfits se conservan aparte. No son entrenamiento lingüístico.

## Evidencia que cambia la interpretación

1. DeltaFast obtiene50,28% IID fuera de ventana y52,50% estructural fuera. EventFast48,89%/45,56%; histórico38,06%/41,39%; sinHielo33,61%/31,39%. Existen diferencias exploratorias emparejadas, no igualdad de FLOPs ni certificación poblacional.
2. Un control que **nunca lee valores**, solo presencia por entidad y un prior de respuesta aprendido de train, obtiene53,33% en esos estratos. La distribución está globalmente balanceada, pero eso no elimina priors condicionados por entidad/estado. El panel no puede certificarse «sin atajos».
3. La prueba decisiva exige acertar original, cambio de hecho obsoleto y cambio del valor vigente conservando la operación. En42correcciones genuinas fuera de ventana, **los18modelos primarios obtienen0/42**. También fallan los24casos cuyo valor contrafactual sigue dentro del soporte train de esa entidad. No puede atribuirse todo a combinaciones nunca vistas.
4. Parte del éxito aparente en el diagnóstico contrafactual mixto provenía de pasar borrado→escritura, no de actualizar un valor. Se conserva ese análisis, y se publica su desagregación posterior en VALUE_BINDING.md; no se reetiqueta como prueba previa independiente.
5. Resetear/intercambiar Hielo reduce la exactitud de los híbridos. Por ejemplo, Delta pasa de48,33–53,75% a34,58–37,08% al resetear en el conjunto conjunto IID/estructural fuera. Esto acredita utilidad parcial del estado bajo esta distribución, no su contenido exacto ni edición semántica.
6. Las compuertas tienen gradientes finitos, cambian y reaccionan de manera distinta a actualizaciones/propuestas. Todos los candidatos densos se calculan: no hay ahorro por escrituras omitidas. Gradiente y activación de gates no prueban selección útil.

## Qué preservamos y qué no promovemos

Se preservan histórico, noHielo como control activo positivo y ambos híbridos como implementaciones funcionales. No se reemplaza CryoTiny por EventFast/DeltaFast, no se declara superioridad HRM y no se añade otra arquitectura para escapar del resultado negativo.

La velocidad CPU de los híbridos (~1,9× la del histórico en este fixture) es real, pero no compensa la ausencia de corrección fiable. Los resultados no refutan universalmente la hipótesis del aislamiento: están limitados a esta capacidad, receta, supervisión y presupuesto. Tampoco proporcionan evidencia suficiente para defenderla como mecanismo aprendido de selección de valores.

Las ablaciones completas y su alcance están en ABLATIONS.md y ABLATION_VALUE_BINDING.md. La comparación normal/permanente muestra solo+1,67pp IID fuera en media y signos mezclados; no se interpreta como selección aprendida. El control aleatorio respeta una regla opcional prefijada y una media de coeficiente calibrada en el piloto, no iguala dinámicas de estado ni omite FLOPs.

## Decisión de continuación

**Bloqueada la promoción arquitectónica y la afirmación de memoria selectiva útil.** El siguiente paso de menor coste es localizar si Hielo codifica valores o solo presencia, y eliminar el prior entidad–respuesta con todos los hechos consultados presentes y valores balanceados por entidad. Véase NEXT_EXPERIMENT.md. El final sellado no se abrió: gastarlo ahora no resolvería el fallo del panel.

## Cierre de ablaciones (tres semillas)

La política aleatoria también falla0/42 en cada semilla. Medias de exactitud del runner IID fuera/estructural fuera: aprendida50,28%/52,50%, permanente48,61%/49,72%, aleatoria33,06%/32,78%. Que una política aprendida supere esa escritura aleatoria dispersa no acredita binding: la permanente queda próxima y las tres políticas fallan la prueba crítica. El presupuesto aleatorio iguala solo el coeficiente aditivo esperado del piloto (0,07153), no la amplitud, varianza ni frecuencia de borrado. El resultado no aísla una estrategia óptima de selección.
