# Siguiente experimento mínimo, todavía no ejecutado

No aumentar semillas/updates ni crear otra arquitectura sobre el panel actual. Antes de un benchmark CUDA o entrenamiento lingüístico, resolver dos incertidumbres diferentes.

## 1. Probe del contenido ya aprendido

Sobre checkpoints existentes, congelar todos los pesos. Extraer Hielo justo antes de la consulta; separar programas por familia. Entrenar probes pequeños y comparar estado inicial aleatorio, entrenado, reseteado e intercambiado. Medir separadamente presencia por entidad y clasificación de sus cuatro valores **solo cuando el hecho existe**. Igualar ejemplos/regularización y contrastar contra prior condicionado por entidad. No usar el final sellado ni confundir decodificabilidad lineal con uso causal del contenido.

Si el estado no permite recuperar valores, investigar escritura/representación. Si permite recuperarlos pero el modelo falla al contestar, investigar lectura y señal de entrenamiento. Una intervención de valor sobre el estado/probe requiere validar que no altera indiscriminadamente otras entidades; no adjudicar causalidad por correlación del probe.

## 2. Panel de binding con control identificable

Mantener backbone, salida, receta y presupuesto; cambiar **solo el panel**. Todos los hechos consultados presentes, cuatro valores equiprobables **por entidad y operación**, todos los pares entidad–valor admitidos en train. Reservar composiciones de varios bindings y estructuras, no un valor único o un prior diferente por entidad. Contrafactuales original/obsoleto/vigente agrupados en el mismo split/familia, cambios genuinos sin cambiar operador. Distractores aceptados de otra entidad y propuestas rechazadas al final impiden usar simplemente el último valor.

Congelar antes de entrenar: pruebas de balance condicionado, heurísticas primero/último/presencia, tamaños y hashes; positividad del soporte de valores y twin fuera de ventana exactamente idéntico en el foreground. Dos oráculos. Generación/custodia independiente del final cuando sea posible. Balancear globalmente no basta; publicar máximos de controles y sus intervalos sin ajustar umbrales sobre final.

Primera compuerta: microfit de16–32programas con corrección genuina y al menos dos valores por entidad; todos los brazos deben poder memorizar original y twins. Después, piloto de una semilla con los modelos ya existentes y presupuesto limitado, evaluación composicional/estructural por tarea y tiempo. Solo ampliar si alguno supera de forma repetible los controles de valor y responde correctamente a ambos cambios contrafactuales.

Si ninguno aprende, variar un único factor: supervisión causal auxiliar del binding frente a respuesta final solamente. No presentar esa modificación como demostración de selección espontánea. Registrar gradientes/horizonte/saturación antes y después. El entrenamiento del filtro por separado y su utilidad final son preguntas distintas.

No se autorizan automáticamente GPU, Vast.ai, corpus Chinchilla ni pretraining por este plan. El resultado negativo actual queda intacto.
