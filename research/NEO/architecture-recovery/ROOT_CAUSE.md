# Causa localizada y límites de identificación

## Conclusión

**Hielo no es simplemente un bit que dice que algo ocurrió, pero tampoco contiene una asociación entidad–valor robusta y actualizable demostrada.** Contiene señales fuertes de presencia y residuos sensibles a valores; esos residuos son parcialmente decodificables y muy dependientes de estructura/posición. El lector original no los utiliza para seguir correcciones contrafactuales.

La evidencia no identifica un único parámetro o gate defectuosa. Sí descarta la justificación de pasar directamente a «arreglar solo el lector porque Hielo ya guarda el valor correcto». Se prioriza el contrato de asociación en escritura/conservación, sin otra arquitectura.

## Qué está medido

- Nueve modelos normales congelados, tres semillas, comparados con sus nueve inicializaciones. Seis políticas Delta previamente entrenadas completan los controles, sin repetir trayectorias.
- Probe lineal de presencia dev: histórico100%, Event100%, Delta98,44%; **también100% en inicializaciones**. Además, el borrado de ausencia ocurre localmente. Esto no demuestra aprendizaje de retención de presencia a larga distancia.
- Probe lineal de valor vigente (azar25%) dev con posiciones nuevas: histórico29,69±3,38%, Event32,60±2,01%, Delta29,38±3,01%. Estructural:28,12%,27,60%,24,79%. Inicializaciones Event51,67%/Delta37,92% en dev y43,44%/41,88% estructural: el entrenamiento previo no produce una mejora uniforme de decodificabilidad.
- En el suplemento de combinaciones nuevas de distractores manteniendo posiciones, valores: histórico30,42%, Event30,62%, Delta34,22%. No elimina por sí solo el problema ni es confirmación independiente. La inicialización Delta ya obtiene34,84% en ese suplemento.
- Los MLP32 pueden sobreajustar train, pero no rescatan robustez estructural. El control explícito obtiene100% en todos los objetivos dev; presencia sola25% en valores. Etiquetas train permutadas y métricas completas se conservan.
- Al intervenir con estados reales emparejados que difieren solo en valor vigente, la distancia relativa media de estado es6,20% histórico,7,89% Event,13,04% Delta. Distancia no equivale a binding correcto. **Los nueve modelos tienen0/120pares con original correcto e intervención siguiendo el nuevo valor**. Cambios de predicción:0/360 histórico,0/360 Event,17/360 Delta; estos últimos tampoco siguen correctamente el cambio válido. Las mismas familias se reutilizan entre semillas, no son360pruebas independientes.
- La intervención sham es exacta; los estados provienen del mismo modelo, entidad y contexto visible. El injerto reduce, pero no elimina, riesgos de incompatibilidad contextual. La sensibilidad a cambiar el obsoleto también persiste; no es correcto inferir fallo semántico solo por distancia/logits si la respuesta permanece correcta.

## Localización por etapas, semilla17 prefijada

El valor en su embedding se decodifica100%; hidden causal en el token oracular vigente:90% histórico,92,5% Event,60% Delta en dev. Por tanto la información del símbolo entra al backbone; no es un fallo de encode de NeoToken, que ni se utiliza en este fixture.

En el subconjunto de correcciones genuinas, probe lineal sobre resumen de escritura: histórico25,83%, Event65%, Delta70%; tras escribir Hielo:32,50%,43,33%,42,50%. Esto localiza dificultades de representación/mezcla en la ruta de memoria de los híbridos, pero **no demuestra pérdida irreversible de información**: probes diferentes, limitados y estructuras nuevas pueden fallar sobre códigos recuperables de otra forma. En estructural, los resúmenes ya caen a25%/30%/26,67%. No se puede atribuir todo a borrado/retención si la representación de entrada al filtro tampoco generaliza.

Los resultados mixtos de etapas incluyen retain/other, cuyo último evento no contiene el valor vigente. Por eso se conservan y se publica la desagregación genuina, sin usarlos como contraste de igual acceso. Las posiciones oraculares son acceso adicional para localizar y no un mecanismo aprendido de selección.

## Las cuatro posibilidades solicitadas

|Posibilidad|Estado de evidencia|
|---|---|
|1. Solo presencia/superficie|Presencia domina y generaliza mejor. «Solo» no está demostrado: hay sensibilidad y decodificación parcial de valores.|
|2. Asociaciones bien codificadas, mala actualización|Hay señales parciales, pero no un código robusto previamente demostrado. Borrado/regla delta como causa única sigue sin aislarse.|
|3. Valor vigente correcto, falla solo lectura|No sustentado como explicación suficiente: los probes del estado también fallan en generalización. La lectura original falla y un lector auxiliar mejora solo parcialmente.|
|4. Escritura/lectura funcionan bajo supervisión explícita, falla end-to-end|No demostrado. El control explícito certifica el decoder, no enseña ni certifica la escritura del modelo. Falta el único contraste auxiliar propuesto.|

## Qué no se concluye

No se prueba ausencia absoluta de valores ni imposibilidad de recuperar estos pesos. No se demuestra selección inteligente por diferencias de gate, causalidad exclusiva de una proyección ni ventaja lingüística. Los decoders condicionales y supervisados tienen acceso adicional que el modelo original no aprendió a usar; su exactitud no es una reparación de CryoCCM.

No se ejecuta piloto correctivo end-to-end: el diagnóstico no identifica aún una causa única suficientemente clara para adjudicar una mejora a un cambio particular. El próximo contraste se reduce a **una señal auxiliar de asociación en escritura**, no a otro ciclo de diseños; se especifica en NEXT_DECISION.md.
