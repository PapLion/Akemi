# Ecuaciones y procedencia

Hielo: M en R^(8×32), cero por documento. Foreground causal histórico y refinamiento rápido normalizado de dos pasos conservados. No KV cache ni contexto completo oculto.

Para un registro observado de cuatro IDs `op entidad valor ;`, se extrae la clave de la representación de embedding de la entidad: k=normalize(Wk E[token_entidad]). Es una rama causal del input del foreground, deliberadamente independiente de contexto. No se usa la entidad como índice de fila de M ni se suministran valores del oráculo. Los cinco caracteres tienen embeddings aprendidos ordinarios, igual que cualquier token. La clave de consulta comparte exactamente E y Wk.

El valor v=tanh(Wv f_pos_valor+bv) procede del foreground refinado real, causal. Tras emitir los logits del chunk, cada acontecimiento observado `=` o `!` completo aplica, en orden textual:

M' = M + k (v - k^T M)^T.

Con ||k||=1, k^T M'=v^T salvo redondeo. Para otra clave q, la interferencia es proporcional a q^T k; no se garantiza conservación de asociaciones arbitrarias. No se han aumentado dimensiones ni usado slots de entidad del oráculo. Es Delta de beta=1, retención global=1; no equivale a los gates aprendidos anteriores.

La lectura r=q^T M entra por Wout, el módulo read histórico y la misma actualización fast, normalización final y head atado. En una consulta, desde la posición de entidad se reutiliza su clave hasta el final del registro; antes de verla solo se usa el token actual. El estado escrito al final de chunk nunca alimenta sus propios logits.

**Intervención de sistema completo:** direccionamiento compartido, valores por acontecimiento, gramática explícita, escritura determinista y nuevo readout. No permite atribuir causalmente la diferencia solo a escritura, solo a claves ni a parámetros adicionales. La regla anterior escribía incluso chunks de ruido; aquí el rechazo `~` no escribe. Esta ventaja de estructura está declarada y no es selección aprendida.

Referencias primarias: [Miller et al., Key-Value Memory Networks (2016)](https://arxiv.org/abs/1606.03126), distinción clave/valor; [Yang et al., DeltaNet (2024)](https://arxiv.org/abs/2406.06484), memoria matricial editable. Implementación propia de las ecuaciones, sin copiar kernels. [FLASH-LINEAR-ATTENTION LICENSE](https://github.com/fla-org/flash-linear-attention/blob/main/LICENSE) verificada MIT el 31-10-2026; no se importa esa biblioteca. No se presenta este módulo como reproducción de Gated DeltaNet ni se heredan sus garantías/benchmarks. El repositorio local no contiene LICENSE raíz: no se declara resuelta su redistribución.
