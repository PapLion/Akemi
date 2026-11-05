# Visibilidad real y límites de atribución

Las máscaras reales se capturan con hook del primer bloque. Último token de segunda escritura en train(ID15) ve claves0–15 en ambos brazos; consulta(ID63) solo48–63. Ambas escrituras pertenecen al mismo bloque foreground16, incluso cuando están en chunks de memoria distintos. Sin KV ni prefijo accesible desde consulta excepto Hielo. Dev: segunda escrituraID31 ve16–31, no0–15.

Diferencias inevitables: primera escritura cambia posición2→0, recencia y contexto previo; en separate ya modifica Hielo en chunk0 y puede influir en fast del chunk1. En same chunk0 contiene neutrales. La segunda representación puede atender a la primera en ambos, pero los estados recuperados y horizontes de gradiente difieren. Hay8actualizaciones densas por secuencia en ambos; chunks con hechos explícitos son1frente2. No es una ablación exclusivamente de compresión.

Causalidad train/eval comprobada: cambiar IDs desde16 deja estado supervisado y CE inicial idénticos. Equivalencia de estado con ejecución del prefijo de16IDs, tolerancia1e-5; batch permutation atol1e-6,rtol1e-5; documentos atol/rtol1e-5; padding inválido no altera outputs. Dev también supera causalidad/máscara al corte32. Gradientes auxiliares finitos alcanzan memory_head.value.
