# F2 construido, sin Hielo niTrapos

F2: vocab8192,width128,4bloquesGQA(4query/2KV),RoPE,preRMSNorm,residuales,MLPSwiGLU4d,refinamiento rápido normalizado2veces,embedding/head tied. **2.082.176parámetros**, todos entrenables. Embedding/head1.048.576=50,36%; atención196.608;MLP786.432;norms1.280;fast49.280. Fórmula8192d+L(15d²+2d)+3d²+3d coincide conSCALING_PROPOSAL.

BaselineTransformer: mismosV/d/L/atención/contexto/head tied, sinfast; **2.032.768parámetros**. Diferencia49.408,2,43% sobrebaseline. No se iguala añadiendo parámetros inútiles. Ambos usan bloques históricos sin alterar su implementación. F2 hereda inicialización normal.02, residuales escalados porsqrt(2L) delBaseline; la receta pequeña anterior no aplicaba ese escalado, diferencia explícita al construir el candidato nuevo, no migración de pesos. No se modifican checkpoints históricos.

`f2.py` implementa construcción/forward/loss/update/checkpoint; CPU FP32. Máscaras segmentadas impiden atención y targets entre documentos, posiciones reiniciadas y padding excluido. Generación por recomputación del prefijo, sinKVcache ni memoria oculta. No hay módulosHielo inactivos inflando el conteo.

Pruebas ejecutadas: perturbación futura, aislamiento de filas/documentos, shift/máscara, todos los gradientes finitos, parámetros actualizados, AdamW completo, seisupdates continuos vs2+checkpoint+4exactos (modelo/optimizador/RNG/cursor), generación técnica y unupdate con IDs realesV3 aprobados. Checkpoints técnicos no son modelos preentrenados. Tests9PASS; receipts enresults. El cursor de estas pruebas recorre fixtures deterministas; la integración del futuro lector corpus necesita una regresión equivalente con su manifiesto final antes del entrenamiento5M.

FLOPs orientativos6P/target:12,493M F2 y12,197M baseline, más atención O(LT²d), RoPE/norm/refinamiento/optimizador.6P sobrecuenta el lookup y no es perfil exacto; no se declara cómputo igual. La medida walltime prima para presupuesto.
