# Contrato del adaptador

`model.py`: embeddings E8192×32 compartidos con LM head; Block histórico causal (GQA/RoPE local); refinamiento rápido de dos pasos; matriz Hielo H8×32 inicialmente cero. Trapos OFF. Cada documento comienza en cero. EOS258, BOS257, PAD256. Una conversación fuente completa es un documento; sus roles se conservan en texto, sin máscara SFT.

Para cada chunk de hasta16 tokens:

1. x = Block(E(tokens), máscara causal). RoPE reinicia posiciones0…15; no embeddings absolutos nuevos.
2. q_t = normalize(address(E(token_t))). r_t = read(address_out(q_t H_previo)).
3. f = x; repetir dos veces f = RMSNorm(f + tanh(fast([f,x,r]))).
4. logits_t = Eᵀ RMSNorm(f_t + r_t).
5. Solo tras un chunk completo: k=q_último; v=tanh(event_value(f_último)); H_nuevo=H+k⊗(v−kᵀH).

La matriz, dimensiones, Delta, proyecciones y refinamiento se conservan. **Cambian el calendario de escritura y la construcción de consultas**: el original usa entidad y valor en posiciones sintácticas distintas, y difunde claves de entidad dentro de cada registro; el puente usa el token final y consultas por token. El contraste A/B prueba este adaptador, no demuestra equivalencia con el comportamiento aprendido por el DSL. Son cambios inevitables y declarados de interfaz, no pesos migrados ni extracción semántica.

H_nuevo jamás se utiliza para los logits de su propio chunk. No se escribe un fragmento parcial. No hay labels, entidades del oráculo, decoder auxiliar ni aceptación aprendida en el forward. Usar el último token puede producir direcciones de puntuación repetidas y sobrescritura; no está resuelto el direccionamiento lingüístico.

En entrenamiento, gradientes atraviesan H entre chunks de una ventana128; se truncan al reiniciar cada ventana. Documentos fuente se guardan completos, pero las ventanas128/stride127 son unidades de optimización con offsets, no documentos nuevos: un token solapado permite cubrir cada target una sola vez en el recorrido completo. No se mezcla texto de documentos diferentes. El packing admite segmentos y reinicia H en cada frontera.

Session guarda H, pending (0…15 IDs), session_id y chunks completados. Cada token recalcula el prefijo local pendiente: correcto pero no KV-cache eficiente. Al terminar el chunk, descarta sus tokens crudos y persiste únicamente H; un session_id distinto exige reset explícito. La generación incluye todos los tokens de texto y EOS, enmascara PAD/BOS/roles/reservados; bytes generados pueden ser UTF8 inválido y se guardan exactamente antes de una visualización con reemplazo. El decodificador estricto no se altera.
