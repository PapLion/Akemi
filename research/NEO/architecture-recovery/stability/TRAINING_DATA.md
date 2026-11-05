# Datos y cobertura

B reconstruye literalmente los registros e índices del tratamiento V1.1: 50% sin corrección, 50% con una corrección, repartida entre la entidad consultada y la otra. Cada secuencia mantiene 64 IDs y la gramática de acontecimientos de cuatro IDs.

C conserva esos valores, roles, índices y presupuesto. Amplía a nueve pares no ordenados de cinco entidades; reserva **A–C**, en ambas direcciones, para evaluación. Varía escrituras iniciales entre (0,1),(2,3),(4,5), corrección entre registros 6/8/10 y añade una tercera entidad en el registro 11 en 25% de secuencias. La consulta queda al final. Los hechos válidos permanecen fuera de la ventana local de consulta; no hay caché oculta.

En cada brazo hay exactamente 1.200 secuencias corregidas: 600 consultan la corregida y 600 la preservada. Las 1.200 restantes no contienen corrección. Todos los valores tienen soporte en cada par/rol observado. El muestreo original de valores e identidades es aleatorio y emparejado: **no se afirma igualdad exacta de cada celda condicionada en las 2.400 exposiciones finitas**. Los conteos reales, transiciones, programas únicos y heurísticas están en *-frequencies.json. Las proporciones de roles sí son exactas; frecuencias finitas desiguales limitan el alcance del balance.

No se eliminaron registros después de mirar sus resultados. No hay duplicados exactos train/dev en ninguna familia evaluada. El par A–C completo no aparece en train C. Los layouts de dev usan (6,7)/11, (1,4)/9 y tercera entidad intermedia, excluidos de train. Los valores y símbolos individuales son conocidos: generalización composicional, no vocabulario nuevo.

El control última escritura por entidad resuelve el DSL por definición; primera escritura, última global y presencia constante se reportan como atajos. No se interpreta esta tarea como comprensión lingüística. La memoria recibe escrituras sintácticas deterministas: Trapos semántico no fue entrenado.

Se detectó antes de entrenar una correlación accidental entre el calendario de pares y el tipo de evento; preflight-draft-preserved.py conserva el borrador. Se corrigió antes del freeze y no hubo entrenamiento principal con ese borrador.
