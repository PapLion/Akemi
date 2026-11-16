# Investigación acumulativa de Neo LM — estado verificable

La referencia conservada es F8 con normalización antes de tanh, checkpoint de10M targets, y Transformer8 de10M. No se sobrescriben pesos ni históricos. Esta rama continúa `189b6ef`; no contiene un Neo LM V1 certificado.

## Frontera establecida

1. Un panel nuevo de320 consultas separa un hecho/dos hechos/correcciones, distancia, idioma y formato pregunta/continuación. F8 acierta79 y Transformer80, con0/96 grupos contrafactuales completos. El déficit aparece también con un solo hecho cercano y teacher forcing. Los cambios de scoring/EOS no lo resuelven.
2. Cuatro adaptaciones emparejadas, arquitectura×LR, completaron1000 updates sobre1024 respuestas nuevas y512 dev. Ningún brazo resuelve un cuarteto completo en train ni dev. LR conservador reduce el olvido respecto a0.003, pero ninguno cumple retención. No se atribuye la dificultad exclusivamente a CryoCCM: Transformer también falla.
3. La atención presenta concentración extrema en ambos modelos. Una intervención causal aislada de RMS Q/K por cabeza elimina esa concentración en la sonda fija, pero las cuatro trayectorias resultantes tampoco certifican binding ni retención. Se descarta adoptar esa modificación tardía; no se generaliza a un entrenamiento desde cero.
4. El diagnóstico secundario separa seleccionar algún valor presente de vincularlo con la entidad correcta. En el mejor conteo de presencia observado de la variante Q/K, Transformer selecciona un valor presente423/512, pero solo259/512 identifica la entidad correcta entre los dos presentes;1/128 cuartetos. Esa evaluación restringida es asistida y no reemplaza las cuatro opciones originales.
5. La CE de un diccionario que ignora hechos y consulta alcanza0.688822 por token supervisado.1024 de3066 targets únicos son EOS. La CE baja no demuestra por sí sola transporte de relaciones. No hay error demostrado de media sobre vocabulario: la máscara promedia correctamente posiciones supervisadas.
6. La generación se conserva completa en un panel separado de12 prompts bilingües con greedy y tres semillas. Los checkpoints preentrenados repiten; la adaptación suele emitir EOS inmediatamente fuera del formato entrenado. La caída de repetición por salidas vacías no es una mejora de coherencia. No hay votos humanos ni juez LLM.

## Causas demostradas y límites

Se han descartado en los contratos ejercitados fugas de futuro, mezcla entre filas, targets desplazados y pérdida de estados AdamW/RNG/cursor. Los gradientes alcanzan embeddings y Q/K/V/MLP/refinamiento; no se afirma que su magnitud garantice aprendizaje. El refinamiento rápido es por posición, no un estado recurrente temporal que aquí esté perdiendo hechos. Hielo y Trapos están OFF.

La concentración de atención es un fenómeno real compartido, pero corregirla aisladamente no bastó. El clipping frecuente es observacional: no se ha ejecutado una intervención que pruebe que causa el fallo. La hipótesis de señal poco discriminativa motiva únicamente el contraste preregistrado en `../neo-binding-objective-contrast-v1/`; su resultado se mantiene separado de las ocho trayectorias terminadas.

## Gates y continuidad

Siguen vigentes los criterios prospectivos por split/idioma/orden y retención, sin seleccionar LR o checkpoints por dev. Los cuatro holdouts distinguen combinaciones, entidades, valores y estructura factual; son datos sintéticos controlados, no lenguaje natural abierto. Las entidades nuevas lo son respecto a la adaptación, no necesariamente respecto al pretraining.

**NEO LM V1: NOT READY.** No hay base para certificar recuperación contrafactual ni generación condicionada generalizable, reabrir Hielo o aumentar escala por inercia. Los resultados negativos acotan intervenciones suficientes bajo esta receta, no una imposibilidad matemática de aprender lenguaje.

Los registros de cada ciclo, los hashes, predicciones y cierres API quedan junto al experimento correspondiente. `RESEARCH_REGISTER.json` identifica resultados completos frente a trabajo pendiente. No publicar pesos/corpus ni hacer push.

## Cierre del contraste de señal

La intervención CE + otro valor quedó bloqueada por dos fallos de infraestructura antes de SSH:0 targets científicos, ningún resultado CUDA.15 tests y contratos CPU pasan; no se trata como refutación de la hipótesis. API final cero recursos. El registro financiero y la distinción de resultados están en ../neo-binding-objective-contrast-v1/DECISION.md.

## Finalización autónoma y protección del alquiler — 2026-11-16

Se añade `../neo-training-operations/` como extensión del pipeline Vast/SSH existente, sin cambiar objetivos ni modelos. El supervisor systemd sobrevive al cierre de Codex; conserva un manifiesto privado, salida real del proceso, recuperación SCP con SHA-256, archivo privado en Drive con verificación por descarga, y cierre en `finally`. Un watchdog GitHub externo al equipo y a la GPU debe emitir un recibo autenticado antes de crear una instancia; un timer systemd persistente añade un segundo control de deadline. No se considera equivalente configurar el watchdog y tenerlo armado para un trabajo activo.

Comando único de lanzamiento, una vez preparado y autorizado el JSON específico: `python3 ../neo-training-operations/operations.py launch ../neo-training-operations/private/job.json`. `prepare.py` reutiliza el bundle contrastivo existente y crea un borrador sin autorización ni oferta; no alquila ni entrena. Los reinicios reconcilian el ID/label y no repiten automáticamente una creación o el entrenamiento. La falta de recibo de salida nunca cuenta como éxito.

Los tests cubren fallo/interrupción/timeout del proceso, subida fallida con reintentos acotados, corrupción, idempotencia, falta de credenciales, propiedad de la instancia y desconexión del lanzador. La prueba de integración real usa systemd y Drive, con proveedor destructivo simulado. Evidencia de instalación y prueba externa de solo lectura en `../neo-training-operations/results/`. No hay nuevos targets científicos ni certificación de binding. NEO LM V1 sigue **NOT READY**. Solo la automatización y manifiestos pequeños están autorizados para publicación en la rama de investigación; corpus y pesos permanecen privados.


## Handoff contrastivo — 2026-11-16 (bloqueado antes de entrenar)

Trabajo `neo-binding-20261116-203925`, autorizado por un máximo total de USD0.75 y una sola instancia sin sustitución. El watchdog GitHub emitió recibo autenticado antes del alquiler (run43976632281; deadline2026-11-17T00:23:32.879165Z). La instancia60986555 falló en la etapa de asociación SSH y fue destruida por el supervisor. API posterior: cero instancias y cero volúmenes. No se transfirió el bundle ni se entrenaron targets. El manifiesto operativo está archivado en Drive con SHA-256 verificado; no existe archivo de nuevos checkpoints científicos. El crédito observado sigue en USD8.336752810370001, sin atribuir a ese dato una factura definitiva.

Se reprodujo sin GPU una incompatibilidad del CLI instalado: `attach ssh --raw` imprime un diccionario Python y el helper histórico exige JSON. La respuesta original del proveedor no quedó registrada; esta reproducción no excluye un fallo adicional del proveedor. Se añadió un decoder específico seguro que exige éxito explícito, con tests de respuestas válidas, fallidas y malformadas.25 tests operativos PASS. Fuentes, objetivos y bundle congelado contrastivo intactos. No se creó otra instancia. La unidad finalizada se deshabilitó para evitar confusión; el guard local persiste y el watchdog externo conserva su deadline. Evidencia pequeña en `../neo-training-operations/results/active-job.json`. **Experimento contrastivo: BLOCKED, 0 targets; Neo LM V1: NOT READY.**
