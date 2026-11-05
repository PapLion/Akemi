# Control positivo antes de entrenar

Un diccionario explícito de dos asociaciones implementa escritura y recuperación por entidad. Recorre solo prefijos disponibles; verifica los cuatro valores en todas las posiciones/órdenes train/dev de ambas condiciones. Exactitud100%. No reemplaza Hielo ni participa en comparación de arquitectura.

Representación explícita256dimensiones: indicador entidad×valor en las primeras20coordenadas. Decoder original condicionado por entidad, capacidad idéntica256→4, seed202;100updates fullbatch AdamW lr.03,decay0. Se entrena únicamente con mapping same/train; evalúa todos los layouts/condiciones. Accuracy 1.0, CE 0.07583770155906677. Datos y representación explícita son deliberadamente ideales, no prueba de equivalencia de dificultad con Hielo.

Acredita que oráculo, etiquetas y evaluación pueden recuperar dos valores y que este decoder puede aprender un código explícito. No demuestra que el decoder lineal sea suficiente para cualquier código latente ni que un fallo de probe pruebe ausencia de información. Curva y checkpoint en positive-control.json/positive-decoder.pt.
