# Investigación dirigida, fuentes primarias

Consulta2026-10-31UTC. Resultados externos reportados por sus autores, no reproducidos aquí. No se copió software de terceros ni se adoptaron pesos. Licencias de artículos y código son distintas; las implementaciones de esta rama derivan del código experimental local y ecuaciones explícitas.

- [HRM,v3](https://arxiv.org/html/2506.21734v3): dos ritmos de recurrencia, aproximación de gradientes, supervisión profunda y ACT en tareas de puzzles. CryoTiny no replica ese entrenamiento: dos refinamientos MLP por token y BPTT temporal no equivalen a los ciclos y objetivos del paper. Su resultado no puede llamarse victoria de HRM.
- [HRM-Text,v1](https://arxiv.org/html/2605.20613v1): MagicNorm combina bloques PreNorm con normalización al salir del módulo; el horizonte de gradiente aumenta de2a5 pasos. Emplea task-completion y PrefixLM con prefijo bidireccional. Motiva separar estabilización y crédito temporal, pero no autoriza introducir esa máscara en un LM estrictamente causal. Su escala y objetivo difieren de este experimento.
- [TRM,v1](https://arxiv.org/html/2510.04871v1): refinamiento de respuesta y latente con una red compartida, supervisión profunda y ablaciones sobre recurrencia. Sus resultados en puzzles no establecen ventajas generales en lenguaje. Aquí conviene probar un refinamiento rápido antes de copiar una organización jerárquica completa.
- [What Limits Recursive Reasoning Models,v1](https://arxiv.org/html/2609.39967v1): estudia control de actualizaciones, horizonte de gradiente, batch físico y jerarquía. La colocación del gradiente importa además de su longitud. Reporta limitaciones y un resultado negativo de entrenamiento conjunto; algunas secciones son de una semilla. Motiva nuestra ablación detach como receta separada y futuras comparaciones de horizontes intermedios; no prueba que truncar siempre mejore.
- [Gated DeltaNet,v3](https://arxiv.org/abs/2412.06464v3): combina olvido y edición delta con algoritmos paralelos de entrenamiento. [Gated DeltaNet-2,v1](https://arxiv.org/html/2605.22791v1) separa borrado/escritura y desarrolla formulación chunkwise/backward dependiente de gates. Nuestra Delta pequeña es una adaptación afín limitada, no una reproducción de esas arquitecturas ni kernels. Un resultado0% no refuta sus papers. El código GDN2 identificado anteriormente tiene licencia NVIDIA Source Code License-NC; no se importa.
- [Nested Learning/HOPE](https://abehrouz.github.io/files/NL.pdf): memorias y procesos de optimización a varios ritmos; útil como descomposición conceptual, no justifica añadir optimizadores internos al prototipo. Nuestro Hielo es una activación por secuencia, no aprendizaje persistente de parámetros durante inferencia.

## Decisiones que se pueden probar aquí

1. Estabilización: conservar las RMSNorm históricas y cambiar solo profundidad rápida.
2. Crédito temporal: comparar detach con mismo forward; separar de eliminar memoria.
3. Backbone: injertar Event/Delta sin cambiar RoPE,FFN,embeddings ni salida históricos.
4. Coste: medir escritura por pares antes de diseñar un kernel o scan nuevo. La recurrencia histórica depende no linealmente del estado y no admite automáticamente scan afín.

Ninguno de estos textos identifica el mecanismo causal de NEO: esa atribución requiere las ablaciones locales. No se verificó reproducción independiente de los grandes resultados publicados ni equivalencia de presupuestos con nuestro panel.
