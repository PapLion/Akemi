# Diagnóstico de gradientes

Cuatro tests nuevos PASS: identidad CE/media y gradientes de logits al cambiar etiquetas; datos/targets sin fuga y sensibilidad a hechos; causalidad, aislamiento y gradientes en ambas capas; repetición determinista y trayectoria exacta8 vs3+5 (modelo/AdamW/RNG/cursor/orden). Se conservan siete contratos históricos. final-checks.json certifica también la trayectoria interrumpida con objetivo denso y la restauración del checkpoint final.

Para cada respuesta, dL/dz=(softmax(z)−onehot(target))/batch. Todos los gradientes del logit correcto son negativos: descenso aumenta su logit directamente; no garantiza incremento tras un update de parámetros compartidos. Cambiar target modifica exactamente el gradiente esperado. No se diluye la pérdida entre posiciones no supervisadas.

Cabeza y embedding comparten pesos. Descomposición diagnóstica B final: gradiente directo de cabeza 0.510683, contribución encoder al embedding 1.981368, total compartido 2.132091. Gradiente de representaciones de consulta 0.266762, hechos 0.834909. No son parámetros independientes ni efectos causales de utilidad.

Gradientes finitos alcanzan Q/K/V, MLP, refinamiento y ambos bloques. En el último minibatch B, Q de capa2≈0,000909 frente a Q capa1≈0,157976; V capa2≈0,080515. Son normas, no evidencia de ausencia absoluta de señal.

Coseno de gradientes por ejemplo muestra competencia de targets y alineamiento por valor. Se guardan matrices initial/final; valores diagonales ligeramente superiores a1 (~4e-5) son redondeo FP32 en reducciones grandes, no correlaciones físicas mayores que1. No se infiere una causa única de esa competencia. Curvas registran gradientes antes de clipping y normas reales de actualización por tensor.
