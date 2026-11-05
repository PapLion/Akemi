# Tareas, oráculos y acceso a información

Cinco entidades A–E, valores0–3 y ausencia4. Entradas:15registros de cuatro IDs ASCII más consulta de cuatro IDs;64IDs y un target de respuesta desde la última posición. Los8192IDs de salida compiten en cross-entropy; no se restringe argmax a cinco respuestas. Es un fixture simbólico atómico independiente de los merges BPE, no evidencia lingüística ni una modificación de NeoTokenV3.

`=` y `!` establecen hechos aceptados; `~`/`x` son propuestas sin aceptar; `-` borra; `>` cambia objetivo. `?` consulta entidad explícita; `*` consulta el último objetivo declarado. El oráculo hacia delante mantiene un diccionario/objetivo; el independiente hacia atrás busca objetivo y última operación aceptada pertinente. Tests con casos literales y todos los registros generados concuerdan. No son revisión humana independiente.

Tareas: retener un hecho sin corregir, reemplazarlo, varias correcciones sucesivas, corregir otra entidad, distractores de entidad similar, propuestas irrelevantes, borrar y a veces restablecer, cambiar objetivo. Para respuestas de ausencia, las variantes incluyen borrado y conservación de estado vacío. Los programas no prueban razonamiento lingüístico; exigen aplicar una pequeña máquina de estados.

## Antiatajos y límites deliberados

El primer hecho no ocupa una posición fija. La actualización aceptada que determina la respuesta está antes del registro10 (fuera de ventana) o en12 (control reciente), mitad de cada celda. Registro13 actualiza otra entidad;14 contiene propuesta rechazada de la consultada, con valor independiente;15consulta. La recencia superficial no basta. Los valores por posición del último bloque no determinan sistemáticamente el target fuera de ventana.

El control reciente conserva un atajo de posición explícito: en ese estrato el valor vigente está en12. No se usa su éxito para atribuir utilidad a Hielo. La prueba principal exige exactitud fuera de ventana y contrafactuales. No afirmamos ausencia de todo atajo imaginable. La recuperación de la última escritura ACEPTADA de la entidad, tras resolver objetivo, es el algoritmo oráculo y resuelve100%; es la capacidad algorítmica deseada. Distinguir aceptación y entidad no es un atajo espurio. Elegir primer/último hecho o último registro de entidad sin filtrar aceptación ronda20%: mediciones completas en `results/panel-v5-audit.json`.

## Splits factoriales v5

480train,240IID,160composicional,240estructural,160ambos. Clases exactamente balanceadas en cada split; cuotas por tarea/entidad/valor permitido y recencia. Soporte excluido `(index_entidad+respuesta)%5 in (3,4)`, separado de estructura. Tres valores por entidad quedan en train y dos en composición. El prior condicionado a entidad/soporte es33,33%/50%, respectivamente, frente a20% marginal. Mejorar20% no basta para demostrar memoria.

Familia: hash de secuencia de operadores/relación entidad-consultada frente a otra y tipo de consulta; ignora valores y nombres. IID/composición instancian familias presentes en train con nuevos documentos. Estructural/ambos usan buckets6/7 excluidos de train0–5. Son estructuras nuevas dentro de la misma gramática, no operaciones totalmente nuevas ni longitudes mayores. Evitar afirmar extrapolación más fuerte. Se comprueba ausencia de hashes de documento compartidos y separación de familias donde corresponde.

Nuevo final400registros de buckets8/9, semilla independiente, balanceado. Oráculos y hashes se verificaron durante construcción; ningún modelo ni análisis de selección accede al contenido final. Archivo permisos000, excluido de Git y rechazado por `panel.load('final')`. Esto es sellado operativo local, no custodia criptográfica por un tercero. No se abrió ninguna evaluación sellada anterior.

Versiones1/2/3/4 y sus fallos quedan separadas de v5. Solo v5 se usa en los resultados actuales, todos exploratorios; trainv3/v4 idénticos porSHA, trainv5 nuevo. El piloto v4 y una ampliación interrumpida se conservan como exploratorios invalidados por el atajo de soporte composicional. Los microfits anteriores acreditan mecánica, no son resultados de generalización. No convertir silenciosamente un split anterior en una evaluación nueva.

## Control adicional: primer hecho pertinente

`shortcut_audit.py` mide además el primer hecho aceptado de la entidad consultada, resolviendo el objetivo desde el prefijo completo. Obtiene40% en train y estructural;49,58% IID global y52,5% IID fuera de ventana. Por tanto el panel NO permite interpretar una exactitud cercana a50% fuera de ventana como actualización correcta: la retención legítima y algunas correcciones que no cambian el primer valor ofrecen una base fuerte. Es un control con lectura de todo el programa, no un modelo con ventana equivalente. Los resultados centrales incluyen correcciones genuinas (valor inicial distinto del vigente), perturbaciones de valor obsoleto y vigente, y comparación con controles locales.

El contrafactual vigente rota el valor entre0–3; en borrados convierte la operación en escritura0. Esto puede mover el par entidad–valor al soporte composicional excluido de train. El diagnóstico conserva el total y separa cambios de VALOR sin cambio de operación, con par visto/excluido. Un fallo en la versión excluida no identifica por sí solo incapacidad de actualizar memoria. Los contrafactuales obsoletos mantienen el oráculo original; los vigentes deben cambiar la respuesta, no solo producir logits sensibles.

Los nombres de tarea no garantizan cambios semánticos efectivos en cada registro: la ausencia y la reinstanciación pueden dejar valores iguales. La auditoría de operaciones registra en IID19/30replace y28/30multiple con dos valores aceptados distintos de la entidad;25/30other contienen un cambio real en otra entidad. No se reclasifican silenciosamente ni se regeneran tras ver modelos. La prueba crítica usa solo correcciones cuyo valor inicial difiere del vigente; las tablas por etiqueta de tarea incluyen sus variantes y no deben interpretarse como tasas puras de cambio. Esto limita la certificación del panel, sin cambiar su oráculo exacto.

## Confusión adicional medida: presencia sin valores

El control `presence_only_train_prior` guarda cinco booleanos de entidad definida y el objetivo actual, sin leer valores. Aprende frecuencias de respuestas solo de train para cada entidad/presencia. Obtiene53,33% tanto en IID como en estructural, también fuera de ventana. Los híbridos no superan de forma clara este control. La interpretación correcta es que el panel admite una solución parcial fuerte sin binding de valores; no se certifica que haya eliminado todo atajo. El control usa acceso algorítmico al programa completo y memoria booleana explícita, no atención local equivalente.

El diagnóstico separado `VALUE_BINDING.md` exige42correcciones genuinas de valor fuera de ventana,24con valor nuevo aún en el soporte de train. En los18modelos primarios, ninguna trayectoria acierta las dos versiones de corrección de valor; las métricas positivas mixtas incluían cambios de operación borrado→escritura. Se preservan esas métricas y se publica la desagregación posterior, sin presentarla como una confirmación independiente previamente sellada.
