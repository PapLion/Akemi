# Microfit reparado: decisión

El original150updates y sus checkpoints se conservan en association/, sin modificaciones. Continuación aislada en association-repair/.

Simple:98.75% auxiliar, CE0.247663, PASS. Distractores balanceados:43.75%, CE1.275369, FAIL. Ambos150updates, batch8,lambda0.1,lr0.003,clip1,checkpoint17idéntico de origen. No se ajustaron umbrales ni se ejecutaron los brazos600updates.

Fixture40programas por condición:5entidades×4valores×2posiciones. Los distractores también rotan por todas las entidades y valores. Frecuencias exactas por entidad/valor/chunk/inicial-corrección se calculan sobre los targets de la pérdida; cada estrato tiene igual frecuencia de los4valores. No hay rebalanceo posterior. Oráculo de prefijo y máscara de ausencia originales; soft gate no se interpreta como decisión binaria. Los eventos aceptados son operaciones de la DSL, no saltos de cómputo.

El microfit simple demuestra aprendizaje elemental del decoder/memoria bajo esta receta. El fallo aparece al añadir escrituras supervisadas de otra entidad, manteniendo queries balanceadas: evidencia de interferencia/dificultad de asociación multientidad, no prueba de una gate defectuosa concreta. Cambia también el número de targets por ejemplo; por eso no se atribuye causalidad exclusivamente al contenido distractor. No se inventa solución arquitectónica.

Contratos: logs y contracts.json conservan alcance real; causalidad por perturbación futura y gradientes auxiliares hacia memory_head.value verificados. La prueba de reanudación usa copias de estados después de2updates y compara el tercero; no certifica toda la persistencia de RNG/cursor del entrenador ni interrupción del script. Las verificaciones documentales se ejecutaron después del microfit, no antes: queda registrada esa limitación de procedimiento y no se declara certificación completa del entrenador.

Pendientes: evaluación detallada por entidad/valor, confusiones y estados, RNG/cursor reanudado end-to-end. No se dispone de contraste control/tratamiento ni resultados contrafactuales principales. Se detuvo por compuerta fallida; no se afirma mejora de lectura original. Siguiente diagnóstico estrecho: conservar número/posición de targets y comparar escritura de otra entidad frente a repetición de la misma, sin aumentarupdates ni cambiar modelo.

Reproducción: ejecutar repair.py y contracts.py con el Python del entorno evaluations/cryo-legacy-viability/.venv, OMP_NUM_THREADS=1 y OPENBLAS_NUM_THREADS=1. Los scripts actuales sobrescriben sus derivados: para repetir preservar esta carpeta y usar una copia nueva. Sin GPU/gastos/corpus/tokenizador/evaluación sellada.
