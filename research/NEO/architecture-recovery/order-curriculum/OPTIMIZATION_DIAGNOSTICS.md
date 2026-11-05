# Optimización

- direct: 21.037s updates, 266.20 targets/s; clipping 6.71%; RSS proceso acumulado 713.4 MiB. Norma preclip media etapas: 0.60260, 0.01956.
- curriculum: 21.070s updates, 265.78 targets/s; clipping 15.86%; RSS proceso acumulado 713.4 MiB. Norma preclip media etapas: 1.14752, 2.53731.

Normas por tensor por update y curvas por orden cada50 en los JSON de cada brazo. Se preserva AdamW300 sin reset. Tiempos sin profiler, CPU local; RSS high-water del proceso compartido, no memoria exclusiva de cada brazo. Capturas reales de outputs de ambos bloques en checkpoints0/300/700 permiten inspeccionar contextualización. No son evidencia de binding funcional ni atribución causal de interferencia de gradientes.

direct:

| Update | Orden 0 | Orden 1 | CE |
|---:|---:|---:|---:|
| 50 | 50.00% | 50.00% | 0.793933 |
| 100 | 50.00% | 50.00% | 0.694802 |
| 150 | 50.00% | 50.00% | 0.693900 |
| 200 | 50.00% | 50.00% | 0.693413 |
| 250 | 50.00% | 50.00% | 0.693228 |
| 300 | 50.00% | 50.00% | 0.693175 |
| 350 | 50.00% | 50.00% | 0.693165 |
| 400 | 50.00% | 50.00% | 0.693158 |
| 450 | 50.00% | 50.00% | 0.693156 |
| 500 | 50.00% | 50.00% | 0.693156 |
| 550 | 50.00% | 50.00% | 0.693154 |
| 600 | 50.00% | 50.00% | 0.693153 |
| 650 | 50.00% | 50.00% | 0.693149 |
| 700 | 50.00% | 50.00% | 0.693149 |

curriculum:

| Update | Orden 0 | Orden 1 | CE |
|---:|---:|---:|---:|
| 50 | 50.00% | 50.00% | 0.794605 |
| 100 | 50.00% | 50.00% | 0.694804 |
| 150 | 100.00% | 0.00% | 2.626123 |
| 200 | 100.00% | 0.00% | 3.687149 |
| 250 | 100.00% | 0.00% | 4.274994 |
| 300 | 100.00% | 0.00% | 4.959621 |
| 350 | 100.00% | 50.00% | 0.612413 |
| 400 | 100.00% | 100.00% | 0.002918 |
| 450 | 100.00% | 100.00% | 0.000393 |
| 500 | 100.00% | 100.00% | 0.000128 |
| 550 | 100.00% | 100.00% | 0.000048 |
| 600 | 100.00% | 100.00% | 0.000017 |
| 650 | 100.00% | 100.00% | 0.000005 |
| 700 | 100.00% | 100.00% | 0.000001 |

El currículo conserva el orden original al introducir el inverso: update350 original100%/inverso50%; update400 ambos100%. El descenso de CE mixta de4,9596 a0,002918 acompaña esa adaptación, sin olvido observable en estos checkpoints. El directo mantiene CE≈ln2 y probabilidades cercanas a1/2: su argmax constante no implica confianza alta. La trayectoria ayuda a evitar esta solución en el fixture, pero no demuestra interferencia de gradientes como causa.

Capturas de ambos bloques finitas; cambio relativo de norma de outputs entre300 y700 (currículo): bloque0=1,58784, bloque1=4,86737. Son desplazamientos descriptivos sobre los mismos ocho inputs, no una prueba causal de representación composicional. No se ajustaron probes ni se añadieron pérdidas.
