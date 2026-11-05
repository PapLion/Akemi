# Extensión única tras el resultado del presupuesto inicial

El primer ensayo de 100 updates por brazo/semilla no demostró generalización: Event/Delta <1% dev y ~17–22% train; B0 completo/CryoTiny cerca del 12,5% de una elección uniforme entre ocho valores. No se descartan esos resultados.

Antes de ejecutar más updates se fija UNA extensión de todos los diez brazos, seeds17/29/43, hasta update1000. Se reanuda el último checkpoint de100, nunca el mejor checkpoint. No cambiar arquitectura, width32, L1, chunk8, lr0.003, AdamW, datos, splits ni orden relativo. El sampler de1000 debe conservar exactamente el prefijo de100. 900updates nuevos×8=7.200targets nuevos por brazo/semilla; 8.000targets totales, 448 documentos train distintos. No son8.000ejemplos únicos. No se emplea dev para elegir duración diferente por brazo ni se hará una tercera extensión automática.

Límite wall CPU1800s para esta invocación, un thread; detener en frontera de brazo y registrar pendientes. Con los tiempos medidos se esperan ~15min, sin GPU ni coste externo. Registrar cada100updates y checkpoints completos finales. Si hay NaN/Inf o fallo de identidad dataset/sampler, bloquear ese brazo. No cambiar tolerancias.

Esta extensión fue decidida tras ver resultados iniciales y es exploratoria. No debe presentarse como confirmación preregistrada desde antes del primer ensayo. La evaluación final sigue usando todo dev, todas las tareas/semillas, controles completos y ablaciones. Ningún resultado favorable se convertirá por sí solo en superioridad científica o capacidad lingüística.
