# Datos y balance

Train: 1.200 programas, dos consultas coherentes cada uno, 2.400 secuencias de 96 IDs y 2.400 respuestas. Cada secuencia tiene cinco propuestas (12.000 targets BCE adicionales solo en C). Ambas consultas comparten íntegro el prefijo de escrituras; el encabezado final indica causalmente el foco. El orden del par durante escrituras no identifica la consulta final. No se suministran entidades/valores del oráculo al forward.

Tres propuestas son válidas (dos hechos iniciales y corrección o repetición), dos inválidas. Estas cruzan las siete combinaciones inválidas de confirmado/negado/pertenencia al ámbito; la octava combinación es la aceptada. No puede balancearse aceptación dentro de una celda donde la definición lógica fija rechazo. Las frecuencias reales por factor, entidad/valor, posición de consulta, opcode y heurísticas se conservan en frequencies-*.json; no se afirma balance perfecto de cada cruce finito ni 50/50 global. Aceptación global60%.

Train excluye el par A–C, usa layouts0/1 y aliases $/#. Dev mantiene ese par fuera de train, añade layouts2/3 y aliases %/&. focus_change fuerza el cambio de foco entre la primera entidad histórica y la segunda conservada; no cambia el ámbito de conservación. clean reemplaza inválidos con repeticiones válidas. Cada panel tiene192 secuencias; no se agregan capacidades de filtración y recuperación en una única puntuación.

Los nuevos paneles no son evaluaciones selladas históricas ni certificación lingüística. La familia dev comparte alfabeto y reglas; sus filas no son réplicas independientes. El oráculo independiente analiza IDs y un diccionario exacto resuelve100%. Esto certifica realizabilidad, no aprendizaje neural.

Se preservó un preflight borrador en preflight-draft: revisión previa al entrenamiento detectó correlación accidental entre identidad consultada y rotación de foco. Se corrigió antes de medir V1 y antes de entrenar V2; el preflight final añade una aserción explícita de balance. No se ajustaron datos mirando resultados V2.

## Límites de balance observados

Train tiene clases de respuesta [620,540,620,620], y el panel base dev [56,40,56,40]. La mayoría dev es29,17%, no25%; focus_change sí tiene48 por valor. El balance de las dos posiciones de consulta es exacto, pero no todos los cruces entidad/posición/valor están completos: por ejemplo, A consultada desde la primera posición no tiene target1 en train. Estos cruces se publican en balance-audit.json y limitan atribuir los errores exclusivamente al filtro. No se corrigen retrospectivamente ni se ejecuta otra trayectoria para perseguir el resultado.

Las frecuencias de respuesta se cuentan por secuencia y las de acontecimientos por propuesta, no se confunden los denominadores. Las combinaciones de factores inválidos son aproximadamente equilibradas, no una factorial exhaustiva de todos los atributos. El contraste mejora el contrato de consulta, pero no certifica cobertura composicional exhaustiva.
