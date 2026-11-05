# Decisión: contraste cerrado, control positivo NO certificado

Semilla 17; CPU FP32, un thread; 400 updates finales fijos por brazo, batch 8, LR 0,003, clipping 1. Sin Hielo ni Trapos.

B falla las compuertas congeladas en ambos devs. No se ejecutan confirmación seed29, más capas, más updates ni Hielo lingüístico.

1. Sí existe segunda contextualización real: bloque2 recibe estados modificados por bloque1 y K/V de valores sensibles a entidades previas.
2. No hay relaciones entidad–valor utilizables de forma fiable: conjunta train0%, dev pares8,33%, layouts0%; intercambios0/12.
3. B no supera de manera funcional consistente al original. Dos historias acertadas en un dev no cumplen criterios.
4. Tampoco demuestra ventaja sobre C; C supera B marginalmente en respuestas de pares nuevos, pero ambos fallan binding.
5. No se certifica generalización a asociaciones/estructuras nuevas.
6. Coste adicional registrado en PERFORMANCE.md; capacidad comparable no implica FLOPs iguales.
7. No hay control positivo neuronal válido.
8. No está justificado retomar Hielo lingüístico sobre esta receta.

Se cierra esta familia de microfits arquitectónicos. Siguiente intervención debe abordar receta de aprendizaje del foreground: señal autoregresiva de respuesta única, representación efectiva de nombres/valores y dinámica de optimización, con diagnóstico de curvas/gradientes y controles de aprendizaje básico. Este estudio no identifica una causa única ni demuestra incapacidad de dos capas. No autoriza rediseño de memoria, tercera capa, búsqueda de hiperparámetros ni pretraining.

Históricos preservados; sin GPU, gasto, Chinchilla, cambios de tokenizer o evaluaciones selladas. Resultados negativos completos conservados.
