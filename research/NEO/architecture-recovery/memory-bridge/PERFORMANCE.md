# Rendimiento observado CPU

Única trayectoria neuronal lingüística entrenada: microfit de contexto completo, semilla17,200updates×batch8=1600respuestas supervisadas. Parámetros activos 280,736, asignados 284,096. Inicialización nueva y emparejable; los pesos del microfit se descartan para cualquier contraste principal.

Entrenamiento: 3.6071s, 443.57respuestas-target/s y 49236.64IDs de entrada/s. Medición de CPU de un hilo, head solo en posiciones supervisadas. Los32ejemplos del microfit se exponen50veces cada uno;1600targets consumidos no son1600ejemplos distintos. No confundir IDs de entrada con targets de pérdida. Cold start, construcción de datos, diagnósticos, evaluación y escritura de checkpoint quedan fuera de ese tiempo; tiempos por update/gradiente en micro-full-17.json. RSS high-water del proceso 674.91MiB, no memoria exclusiva del modelo.

Reader explícito diagnóstico:20parámetros/100updates, independiente y no sumado a throughput del LM. Pruebas de ingeniería incluyen8updates para tres rutas, no aprendizajes comparativos. No se midió throughput de B V2 ni speedup de Hielo; los valores de V1 no se transfieren a esta receta answer-only.

Atención completa cuesta O(L²) frente a chunks16 de A/B, además de permitir acceso a más información. Todos los módulos provienen del mismo modelo; A/C tienen280736parámetros activos y B284096, con3360parámetros adicionales de memoria. No se midieron FLOPs completos y no se afirma igualdad de cómputo. No GPU, AMP, servicios pagos ni proyecciones de entrenamiento grande.
