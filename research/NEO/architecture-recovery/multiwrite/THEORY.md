# Ecuaciones reales y adaptación

Sea X_j la representación causal del foreground en el chunk j, y M_j∈R^{8×32} la memoria previa. El lector original normaliza q=W_read X_j y recupera q M_j, proyecta y aplica gate recover. El refinamiento rápido histórico aplica dos veces `LN(fast + tanh(W_fast[fast,X_j,retrieved]))`. Sus salidas se forman ANTES de escribir memoria: la escritura actual solo afecta a chunks posteriores.

Referencia: α=softmax(q_summary · fast/√32), z=Σ_t α_t fast_t. k=normalize(W_k z,eps1e-6), v=tanh(W_v z), [c_a,c_e,c_w]=sigmoid(W_ctrl z). a=.9+.09c_a, e=c_e, w=c_w.

`Δ(M;k,v,a,e,w) = a [M − e k(kᵀM)] + k(wv)ᵀ`.

El resumen completo es legítimo para escribir al final del chunk; sería fuga si influyera en el principio del mismo chunk. M es inicializado a cero por documento y se propaga diferenciablemente entre chunks dentro del forward. No es memoria externa permanente.

MultiWrite usa dos consultas aprendidas q_0,q_1 sobre fast ANTES de su reducción global. Cada consulta tiene su propia softmax y produce z_i; comparte W_k,W_v,W_ctrl. No se usan entidades ni valores del oráculo en forward; solo IDs,doc,valid. Consultas iniciales distintas (primera histórica, segunda histórica+ruido seed404,std.2), sin pérdida de ortogonalidad.

Se aplican i=0 y después i=1:
`a_i' = sqrt(a_i)`, `e_i' = 1−sqrt(1−e_i)`, `w_i'=w_i/2`,
`M^(i+1) = Δ(M^i;k_i,v_i,a_i',e_i',w_i')`.

Orden fijo; el segundo borrado consulta M actualizado por el primero. No equivale a una suma conjunta de rango2. Retención total sqrt(a_0 a_1) permanece en [.9,.99]; presupuesto aditivo Σ w_i/2≤1. Con controles idénticos se conserva producto de retención; la raíz del complemento de erase conserva el borrado combinado sobre una misma dirección ignorando escrituras intercaladas. Valores/keys distintos y efectos cruzados hacen que NO haya equivalencia completa con una escritura original, ni igual magnitud final de memoria garantizada. Esto es parte explícita de la intervención.

K1 delega al forward original; la función de transición K1 también pasa equivalencia de valor y gradiente independiente. No se afirma que dos escrituras permitan almacenar dos hechos automáticamente ni que la regla original lo haga matemáticamente imposible.
