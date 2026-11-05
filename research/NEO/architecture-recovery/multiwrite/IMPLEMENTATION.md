# Implementación aislada

mw_model.py extiende ObservedHybrid, sin modificar los archivos históricos. K2 sustituye summary_query(1,32) por(2,32); +32parámetros, el resto se carga idéntico. Lector `_read`, read_query,read_out,recover, proyección read, embeddings, blocks, refinamiento y normalización son los originales. Igualdad estructural y de pesos iniciales verificada; los pesos comunes sí aprenden y divergen entre brazos durante entrenamiento.

Estado Hielo sigue8×32. Softmax en tokens válidos; queries no reciben etiquetas. Doc reset antes de lectura, outputs del chunk antes de escritura, memoria enmascarada para chunks vacíos. Mismo índice/packing heredado. No se añade una API de estado persistente entre llamadas: continuidad certificada dentro del forward y mediante la transición real registrada; streaming interllamadas requiere contrato posterior del foreground local.

La normalización por2 cambia el cómputo y la dinámica además del pooling: la mejora no puede atribuirse exclusivamente a disponer de dos queries. No se añadió una pérdida nueva. El decoder auxiliar se mantiene fuera del forward normal.
