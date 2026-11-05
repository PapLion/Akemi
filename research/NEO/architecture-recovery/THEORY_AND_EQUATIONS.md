# Aislamiento computacional, no termodinámica literal

El testimonio del propietario inspira dos planos: foco activo y antecedentes latentes. Trapos regula incorporación, conservación, borrado y recuperación; Hielo es un estado acotado por secuencia. No representa conciencia, un almacén de conversaciones ni una alternativa al RAG externo de PA. Los conocimientos persistentes entre sesiones siguen en pesos/RAG; las activaciones aquí se descartan al reiniciar la sesión.

## Núcleo activo compartido

Embeddings atados con LM head, posición sinusoidal relativa al fragmento, bloques pre-RMSNorm, SDPA causal de cuatro cabezas y FFN SwiGLU. FFN interno2d, sin dropout en estos experimentos. Para documento d y fragmento j, X_j = Backbone(ids_j), sin acceso a ningún fragmento posterior. El backbone y los resúmenes de todos los fragmentos pueden calcularse en paralelo como batch independiente; la memoria se lee antes de escribir.

Y_j = RMSNorm(X_j + sigmoid(W_r X_j) · W_o Read(H_{j-1}, X_j)).

Las predicciones del fragmento j usan exclusivamente H_{j-1}. El resumen Z_j de j solo escribe H_j, disponible para j+1. La posición final de j predice el primer token de j+1 usando su representación activa causal; no obtiene retroactivamente H_j. Las máscaras LM excluyen padding y transiciones entre documentos. La pérdida sintética supervisa únicamente la siguiente respuesta, sobre los8192IDs, no clasificación restringida a ocho valores.

## CryoCCM-Event

H tiene S slots de dimensión d. Z = softmax(Q_slots Xᵀ / sqrt(d), máscara válida) X. Consultas de slots aprendidas, no un archivo de tokens. Señales:

[e,w] = sigmoid(W_f [Z,H,Z-H] + b_f), C=tanh(W_c Z+b_c).

H' = (1-w)(1-e)H + wC.

La retención es (1-w)(1-e); e puede borrar sin escribir y w incorpora el candidato. Con H inicial0 y C∈[-1,1], la suma de coeficientes es≤1: cada componente permanece en[-1,1]. La lectura usa atención de consultas activas sobre los slots latentes y una compuerta de recuperación por token.

Z-H es una característica redundante para una proyección lineal: **no es un detector demostrado de novedad/contradicción**. Las compuertas son señales aprendibles de edición y lectura, no seis facultades semánticas certificadas. Quedan por estudiar características no lineales de coincidencia/conflicto, competencia entre slots y pérdidas de interferencia, únicamente en nuevos experimentos controlados. No se añadieron después de ver dev para mejorar retrospectivamente este ensayo.

La actualización puede conservar selectivamente por canal, pero una sigmoid suave no ahorra cómputo. Modo hard de inferencia: si mean(w_slot)<umbral, se omite realmente la proyección C de ese slot y se conserva el estado. Se evalúan selección barata y número ejecutado. **Este modo cambia la función**: no es equivalente al entrenamiento soft y no se recomienda sin evaluación. El filtro/score, resumen y backbone siguen costando.

## CryoCCM-Delta

Estado H∈R^(k×d). Resumen Z independiente de H, k=normalize(W_kZ), v=tanh(W_vZ), a=0,9+0,09sigmoid(g_aZ), e=sigmoid(g_eZ), w=sigmoid(g_wZ) por canal de valor.

A=a(I-e kkᵀ), B=k(w⊙v)ᵀ; H'=AH+B.

Read(H,X)=normalize(W_qX)ᵀH, después W_o y compuerta de recuperación. a retiene globalmente, e borra en la dirección de la clave, w escribe valores por canal. Esta adaptación propia usa borrado escalar, no el borrado por canal de Gated DeltaNet-2. Tampoco incorpora sus convoluciones, WY, kernels ni backward especializado.

Si ||k||=1 y e∈[0,1], las singularidades de I-e kkᵀ están≤1; ||A||₂≤a<0,99. B está acotado, por lo que hay una cota geométrica de estado, aunque sus elementos no tienen la cota[-1,1] de Event. Esto demuestra estabilidad del operador, no conservación semántica.

Edición mecánica: para una clave unitaria y a=e=w=1, H'=H-k(kᵀH)+kv_newᵀ: su lectura por k se reemplaza por v_new. Nuestra retención aprendida a<0,99 decae también otras direcciones; no garantiza conservación perfecta. La tarea de corrección comprueba aprendizaje, por separado de esta identidad.

Composición ordenada (A₂,B₂)∘(A₁,B₁)=(A₂A₁,A₂B₁+B₂) es asociativa por asociatividad/distributividad de matrices. `affine_scan` implementa prefijos por doblado, incluidos resets con A=0. Tests FP64 verifican valores y gradientes, y FP32 compara logits/gradientes del modelo completo. **No** se aplica esta prueba a Event: sus gates dependen de H. El scan de referencia usa matrices densas y cuesta más trabajo O(N log N·k³) que la actualización rank1 ideal O(Nkd); no es una afirmación de eficiencia de kernels.

## Persistencia, fronteras y responsabilidad

BPTT no tiene detach implícito. El estado devuelto conserva el grafo si el contexto de PyTorch lo conserva. En inferencia usar no_grad y transportar estado solo dentro de la sesión. Continuación externa exige identidad explícita y única de sesión por fila, orden de batch igual y corte en fragmentos completos. Se rechazan sesiones ajenas/reordenadas y continuación de fragmentos incompletos. Un nuevo documento reinicia H; padding/gaps no transportan información.

La planificación agrupa fragmentos por documento, con padding entre rondas, por lo que packed/unpacked no cambia sus límites. Hay planificación Python y conversiones CPU de metadatos: limitación importante antes de CUDA. No existen KV cache streaming token a token, endpoint de generación de lenguaje ni certificado BF16 en esta versión.

## Tamaño del estado y memoria de entrenamiento

En las instancias width32/S4/k8, Hielo ocupa512bytes Event o1.024bytes Delta por fila enFP32, más metadatos. Ese tamaño acotado describe el estado de inferencia, no la RAM total: parámetros, logits de8192IDs, activaciones y grafos BPTT ocupan mucho más. Guardar trazas/autograd entre fragmentos crece con su número; no se certifica memoria constante durante entrenamiento. Los modos sin persistencia y sin Hielo congelan explícitamente parámetros de memoria que no tienen trayectoria útil hacia la pérdida.
