# Teoría y ecuaciones

Primer plano: foreground causal histórico. Hielo: matriz acotada H∈R^(8×32). Trapos: decisión aprendida que controla incorporación de propuestas, no memoria externa de PA/RAG ni fenómeno termodinámico literal.

Se conserva k=normalize(W_address embedding(entidad)), v=tanh(W_value fast_valor), lectura qᵀH, address_out/read y dos refinamientos rápidos normalizados. La única modificación es:

H' = H + a · k (v − kᵀH)ᵀ.

El predictor de aceptación es z=W₂ tanh(W₁ fast_fin_registro+b₁)+b₂, p=sigmoid(z), a_hard=1[p≥0,5]. Durante train se usa a=a_hard−stopgrad(p)+p: forward discreto, derivada sustituta sigmoide. **Estimador sesgado straight-through**, no gradiente exacto de una decisión discreta ni REINFORCE. Evaluación hard determinista. BCE auxiliar 0,1 supervisa aceptación con etiquetas de prefijo; la respuesta usa CE original.

La escritura solo ocurre tras cerrar un registro candidato y afecta tokens de chunks posteriores. El score utiliza el estado causal de fin de registro, nunca una agregación futura. Un rechazo a=0 deja H exactamente igual. El extractor aplica solo framing/opcode compartido; no comprueba verdad, negación, objetivo ni etiquetas.

La aceptación oracular significa afirmación confirmada, no negada, y entidad dentro del objetivo disponible antes del evento. Las repeticiones válidas son aceptables y deben preservar su valor; no se ha intentado aprender rechazo por redundancia. No hay cabezas separadas de sorpresa/contradicción/confianza.
