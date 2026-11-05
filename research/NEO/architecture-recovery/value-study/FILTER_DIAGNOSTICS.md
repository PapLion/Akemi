# Trapos: compuertas y actualización

Regímenes balanceados por entidad/valores; mismo layout y posición. Presencia=1. El último fragmento que contiene la escritura también puede contener distractores. Para histórico se promedian ocho gates por token, para híbridos dimensiones/slots de la gate de chunk; no son escalas directamente equivalentes.

|Estado|Evento|Gate media|Cambio Hielo|
|---|---|---:|---:|
|delta_fast-17-always-trained|propuesta rechazada|1.00000|0.57176|
|delta_fast-17-always-trained|actualizacion aceptada|1.00000|0.57176|
|delta_fast-17-always-trained|segunda actualizacion|1.00000|0.57176|
|delta_fast-17-always-trained|actualizacion otra entidad|1.00000|0.57176|
|delta_fast-17-normal-trained|propuesta rechazada|0.18839|0.14901|
|delta_fast-17-normal-trained|actualizacion aceptada|0.18839|0.14901|
|delta_fast-17-normal-trained|segunda actualizacion|0.18839|0.14901|
|delta_fast-17-normal-trained|actualizacion otra entidad|0.18839|0.14901|
|delta_fast-17-random-trained|propuesta rechazada|0.00000|0.00083|
|delta_fast-17-random-trained|actualizacion aceptada|0.00000|0.00083|
|delta_fast-17-random-trained|segunda actualizacion|0.00000|0.00083|
|delta_fast-17-random-trained|actualizacion otra entidad|0.00000|0.00083|
|delta_fast-29-always-trained|propuesta rechazada|1.00000|0.20389|
|delta_fast-29-always-trained|actualizacion aceptada|1.00000|0.20389|
|delta_fast-29-always-trained|segunda actualizacion|1.00000|0.20389|
|delta_fast-29-always-trained|actualizacion otra entidad|1.00000|0.20389|
|delta_fast-29-normal-trained|propuesta rechazada|0.22364|0.41618|
|delta_fast-29-normal-trained|actualizacion aceptada|0.22364|0.41618|
|delta_fast-29-normal-trained|segunda actualizacion|0.22364|0.41618|
|delta_fast-29-normal-trained|actualizacion otra entidad|0.22364|0.41618|
|delta_fast-29-random-trained|propuesta rechazada|0.00000|0.00152|
|delta_fast-29-random-trained|actualizacion aceptada|0.00000|0.00152|
|delta_fast-29-random-trained|segunda actualizacion|0.00000|0.00152|
|delta_fast-29-random-trained|actualizacion otra entidad|0.00000|0.00152|
|delta_fast-43-always-trained|propuesta rechazada|1.00000|0.87414|
|delta_fast-43-always-trained|actualizacion aceptada|1.00000|0.87414|
|delta_fast-43-always-trained|segunda actualizacion|1.00000|0.87414|
|delta_fast-43-always-trained|actualizacion otra entidad|1.00000|0.87414|
|delta_fast-43-normal-trained|propuesta rechazada|0.15611|0.12083|
|delta_fast-43-normal-trained|actualizacion aceptada|0.15611|0.12083|
|delta_fast-43-normal-trained|segunda actualizacion|0.15611|0.12083|
|delta_fast-43-normal-trained|actualizacion otra entidad|0.15611|0.12083|
|delta_fast-43-random-trained|propuesta rechazada|0.00000|0.00179|
|delta_fast-43-random-trained|actualizacion aceptada|0.00000|0.00179|
|delta_fast-43-random-trained|segunda actualizacion|0.00000|0.00179|
|delta_fast-43-random-trained|actualizacion otra entidad|0.00000|0.00179|
|event_fast-17-normal-trained|propuesta rechazada|0.16043|1.75685|
|event_fast-17-normal-trained|actualizacion aceptada|0.16043|1.75685|
|event_fast-17-normal-trained|segunda actualizacion|0.16043|1.75685|
|event_fast-17-normal-trained|actualizacion otra entidad|0.16043|1.75685|
|event_fast-29-normal-trained|propuesta rechazada|0.27613|0.86147|
|event_fast-29-normal-trained|actualizacion aceptada|0.27613|0.86147|
|event_fast-29-normal-trained|segunda actualizacion|0.27613|0.86147|
|event_fast-29-normal-trained|actualizacion otra entidad|0.27613|0.86147|
|event_fast-43-normal-trained|propuesta rechazada|0.20463|1.39704|
|event_fast-43-normal-trained|actualizacion aceptada|0.20463|1.39704|
|event_fast-43-normal-trained|segunda actualizacion|0.20463|1.39704|
|event_fast-43-normal-trained|actualizacion otra entidad|0.20463|1.39704|
|intact-17-normal-trained|propuesta rechazada|0.12004|0.55378|
|intact-17-normal-trained|actualizacion aceptada|0.12004|0.55378|
|intact-17-normal-trained|segunda actualizacion|0.12004|0.55378|
|intact-17-normal-trained|actualizacion otra entidad|0.12004|0.55378|
|intact-29-normal-trained|propuesta rechazada|0.21120|0.89965|
|intact-29-normal-trained|actualizacion aceptada|0.21120|0.89965|
|intact-29-normal-trained|segunda actualizacion|0.21120|0.89965|
|intact-29-normal-trained|actualizacion otra entidad|0.21120|0.89965|
|intact-43-normal-trained|propuesta rechazada|0.25616|1.31879|
|intact-43-normal-trained|actualizacion aceptada|0.25616|1.31879|
|intact-43-normal-trained|segunda actualizacion|0.25616|1.31879|
|intact-43-normal-trained|actualizacion otra entidad|0.25616|1.31879|

Always/random son checkpoints entrenados previamente bajo esas políticas; no un cambio de inferencia. Random mantiene el presupuesto previo0.07153 de coeficiente aditivo esperado, no iguala borrado, norma o frecuencia de cambios. Se conserva la distinción entre política constante1 y gates soft. Todas las proyecciones se ejecutan: omisiones reales de cómputo=0.

Una diferencia entre propuesta y actualización puede explicarse por operador/posición, no por saber qué VALOR debe conservarse. Pares de valor y de obsoleto en CAUSAL_INTERVENTIONS.md permiten contrastar efecto sobre estado/predicción, sin atribuirlo exclusivamente a la gate. No se ha intervenido cada gate de forma independiente ni entrenado otro filtro.
