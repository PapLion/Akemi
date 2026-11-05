# Panel controlado para representaciones

`data_panel.py` construye1280programas train,640dev y640estructurales: cinco entidades, cuatro valores iniciales y cuatro nuevos, presencia/ausencia, cuatro regímenes y layouts disjuntos. No utiliza Chinchilla, BPE ni conjuntos sellados. IDs ASCII de la misma DSL del estudio anterior; fixtures de mecanismos, sin afirmación lingüística.

Regímenes: conservar/rechazar propuesta; corrección aceptada; dos correcciones; corrección de otra entidad. Valores0–3 balanceados por entidad, presencia, régimen y layout. Train cubre todos los pares entidad–valor; no confundir la división antigua por soporte de etiquetas con este diagnóstico. Todos los programas tienen distractores y consulta fuera de ventana. Se conservan párrafos de operaciones completos de64IDs.

En presencia=0 se borra la entidad en registro12; la ausencia puede ser evidente localmente. Ese control acredita decodificabilidad de presencia, no retención lejana de una entidad ausente. Los probes de valores excluyen ausencia, con azar25%; el objetivo presencia está balanceado50%. «Corregida» identifica una operación aceptada, aunque reescriba el mismo valor. Para la prueba causal de corrección se exige inicial≠vigente.

Dos oráculos (diccionario forward y búsqueda inversa) concuerdan. Tests comprueban balance, disjunción de programas y que el último bloque visible es idéntico al variar valores. Un control que solo recibe presencia tiene25% en valor; no cuenta como éxito aunque prediga bien presencia. El registro de entidad y la cabeza por entidad tampoco permiten resolver valores balanceados por entidad.

Dev principal y estructural cambian posiciones respecto a train: ambos son generalización estructural, no confirmación independiente ni cambios de algoritmo. Un suplemento post-hoc separado mantiene posiciones train y cambia la asociación con entidad distractora; se declara su alcance estrecho y la cronología en PROTOCOL.md. No se cambia el panel principal después de observar resultados.

Familias contrafactuales permanecen dentro del mismo split. Son programas factoriales correlacionados, no miles de observaciones naturales independientes. La evaluación es exploratoria, sin revisión humana independiente ni final confirmatorio consumido.
