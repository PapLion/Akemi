# Contratos ejecutados

Antes de los entrenamientos principales: datasets emparejados, balance y valores diferentes; causalidad train/eval por perturbación futura; aislamiento batch; target en siguiente posición causal; gradiente a consulta y prefijo; reanudación end-to-end continua8updates frente a3+5 en ambos datasets, con igualdad exacta de pesos, estado AdamW, RNG y cursor/orden verificados. Artefactos de ingeniería separados del entrenamiento principal.

Después: siete tests heredados V2 PASS, cinco tests nuevos PASS; checkpoints finales200updates/1600muestras,13 estados AdamW para13 tensores entrenables y parámetros finitos. El decoder es F.linear con embeddings compartidos; no hay cabeza nueva ni pérdida auxiliar. Modelo no_ice con fast intacto; rutas Hielo congeladas/no utilizadas. Mismo peso inicial certificado por hash real de state_dict, no solo hash del archivo fuente.

Checkpoints conservan configuración V2 del runner reutilizado, que incluye campos históricos no aplicables (p.ej.400updates primarios). El presupuesto REAL de este contraste está en PROTOCOL.json y cursor_updates=200; esta distinción es explícita, no se edita retroactivamente el checkpoint. Dataset/order/tokenizer/model_source se verifican al restaurar. PROTOCOL.json y todos los archivos se enlazan al checkpoint mediante manifest SHA de esta entrega. Ningún archivo previo se modifica.

Las pruebas nuevas pueden repetirse sin sobreescribir checkpoints: python binding-diagnostic/tests.py. El ejecutor principal rechaza resultados existentes, y reproduce.sh impide iniciar un segundo entrenamiento sobre ellos. No se abrieron confirmatorios sellados ni se realizaron entrenamientos adicionales de búsqueda.

La primera repetición de los tests heredados falló por dos fixtures JSON ignorados por git y ausentes en el worktree nuevo. Se conserva el log fallido; se copiaron desde V2 los fixtures existentes sin regenerarlos ni modificarlos y la repetición dio7/7PASS. No hubo fallo del modelo ni cambio de tests para ocultarlo.
