# Alcance y omisiones explícitas

- No lenguaje natural, pretraining, SFT, GPU, BF16/AMP, servicios de pago ni consumo de Vast.ai.
- No se abre el nuevo final sellado ni evaluaciones históricas selladas. No hay confirmación independiente de un revisor humano.
- Foreground por bloques aislados de16IDs; no ventana deslizante ni kernel disperso. Longitud principal64IDs, no extrapolación a conversaciones o contextos extensos.
- El contrato de persistencia es entre fragmentos dentro del forward. No se certifica una API externa de streaming/carry entre invocaciones.
- Las familias estructurales varían operadores/relación con entidad consultada dentro de una gramática conocida; no representan generalización a operaciones completamente nuevas.
- La mitad reciente tiene la escritura vigente en una posición conocida; se conserva como control de aprendizaje mecánico. La conclusión sobre memoria exige el estrato fuera de ventana y contrafactuales.
- Hay priors entidad–soporte y un control de primer hecho pertinente no trivial. Sus métricas se publican; azar20% no es una prueba suficiente.
- Comparaciones primarias igualan ejemplos/updates y semillas, no FLOPs. Las cuentas de linear son cotas parciales; no se usa igualdad de parámetros como igualdad de cómputo.
- Microfit v3 acredita que los seis modelos pueden memorizar10registros. No demuestra recuperación fuera de ventana ni generalización v5.
- Tres semillas originales permiten contraste exploratorio. No bastan para declarar superioridad poblacional ni sustituyen confirmación independiente con semillas nuevas y protocolo congelado.
- Las compuertas blandas no evitan ejecución de escrituras/candidatos. Una sigmoide no acredita selección útil ni ahorro de cómputo.
- El nuevo final usa la misma implementación de generador con otras semillas/familias y dos oráculos algorítmicos; no un segundo generador independiente escrito por otra persona. El sellado es local operativo.
- El panel todavía admite53,33% con memoria de presencia sin valores. Por ello la certificación antiatajos/selección está BLOQUEADA aunque integridad y causalidad pasen. No se promueve ninguna arquitectura.
- No se entrenan más arquitecturas ni recetas después del control aleatorio opcional. Los probes de contenido de Hielo y un panel de valor presente/balanceado se proponen como siguiente diagnóstico, no se declaran ejecutados.
