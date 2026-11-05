# Decisión científica

El piloto NO supera las compuertas. Se cierra Trapos V1; no se entrenaron semillas29/43 y no se rediseñó el filtro.

Compuertas incumplidas: ['advantage-A', 'contaminated_pair-joint', 'layout-joint', 'precision', 'surface-joint'].

| Brazo | Familia | Respuesta normal | Ambas consultas | Corregida | Preservada |
|---|---|---:|---:|---:|---:|
| A-17 | contaminated_pair | 100.00% | 79.69% | 100.00% | 100.00% |
| A-17 | layout | 100.00% | 81.77% | 100.00% | 100.00% |
| A-17 | surface | 100.00% | 79.69% | 100.00% | 100.00% |
| A-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |
| B-17 | contaminated_pair | 78.65% | 47.40% | 70.83% | 86.46% |
| B-17 | layout | 73.44% | 46.35% | 67.71% | 79.17% |
| B-17 | surface | 79.17% | 48.44% | 69.79% | 88.54% |
| B-17 | clean | 88.54% | 57.29% | 77.08% | 100.00% |
| C-17 | contaminated_pair | 100.00% | 76.56% | 100.00% | 100.00% |
| C-17 | layout | 100.00% | 75.00% | 100.00% | 100.00% |
| C-17 | surface | 100.00% | 76.56% | 100.00% | 100.00% |
| C-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | contaminated_pair | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | layout | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | surface | 100.00% | 100.00% | 100.00% | 100.00% |
| D-17 | clean | 100.00% | 100.00% | 100.00% | 100.00% |

La evidencia se refiere únicamente a selección en este DSL. Las escrituras sintácticas se extraen explícitamente; objetivos, confirmación y negación están codificados en registros. No demuestra comprensión libre, filtrado semántico general ni aislamiento térmico completo.

El contraste controla el diseño de Hielo/Delta/lector y datos por semilla. La pérdida adicional C cambia la señal de aprendizaje, declaradamente. Para atribuir beneficio a decisiones, revisar override-all del MISMO checkpoint; no basta comparar parámetros de C con A. D es límite asistido. El criterio decisivo exige selección Y respuestas funcionales frente a A y B, generalización, escenarios limpios y presupuesto de escritura comparable.

Si falla, conservar Addressable V1.2 como referencia válida. No iniciar búsqueda de lambda, head size, nuevas políticas ni arquitecturas. Los resultados delimitan el protocolo/receta; no prueban imposibilidad de filtración aprendida. Si pasa, preparar una transición posterior controlada hacia eventos expresados de otra forma, sin ejecutarla aquí. Ningún pretraining o gasto autorizado por este estudio.


## Alcance de las consultas emparejadas

El entrenamiento consulta siempre la primera entidad del encabezado de objetivo. La segunda consulta de evaluación conserva ese encabezado y cambia solo el token de consulta: introduce una composición consulta/posición de objetivo no entrenada. Por tanto, la exactitud conjunta combina conservación y generalización de lectura; sus fallos no aíslan interferencia ni selección. Se conserva este resultado y no se reentrena para corregirlo. La respuesta normal al 100% tampoco acredita ambas asociaciones.

## Conclusión del piloto cerrado

C no supera escritura permanente: ambos logran 100% en consulta principal; C alcanza 76,56% conjunto frente a 79,69% de A en el par retenido. B alcanza 78,65% normal y 47,40% conjunto; D oracular 100% en ambos. C supera B pero no el conjunto de requisitos. Su precisión de aceptación es 75%, recall 100%, y conserva una heurística equivalente al bit confirmado; no aprende el predicado completo de negación y objetivo.

Forzar todas las escrituras en el mismo checkpoint C reduce la respuesta normal de 100% a 61,98%: sus decisiones aportan beneficio parcial, sin demostrar superioridad del entrenamiento C frente a A ni filtrado completo. D demuestra realizabilidad asistida en esta distribución. No se concluye imposibilidad representacional ni se atribuye el resultado a una única compuerta.

Se cierra Trapos V1 con resultado negativo respecto al criterio prospectivo. Addressable V1.2 permanece intacto. No hay semillas adicionales ni búsqueda de hiperparámetros. Una continuación necesitaría autorización y un contrato que balancee también consulta frente a posición del objetivo y distinga explícitamente la heurística de confirmación; no se ejecuta aquí.
