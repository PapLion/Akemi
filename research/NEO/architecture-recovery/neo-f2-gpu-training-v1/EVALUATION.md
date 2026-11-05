# Evaluación final completa

| Modelo | NLL dev | PPL dev | NLL ES | NLL EN | PPL ES | PPL EN |
|---|---:|---:|---:|---:|---:|---:|
| F2 | 5.559083 | 259.585 | 5.302330 | 5.822112 | 200.804 | 337.684 |
| Transformer | 5.287873 | 197.922 | 5.018696 | 5.563630 | 151.214 | 260.768 |

Dev completo: 212.105 targets, 70 artículos: ES107.333/EN104.772. Dominio: enciclopedia; no existe aquí dev de código independiente suficiente para una conclusión técnica por dominio. NLL/PPL usan todos los siguientes tokens válidos, incluidos EOS, sin padding ni transiciones documentales. Cada target una vez con ventanas de 128 y stride127. Posiciones se reinician por ventana como en el F2 preparado.

La NLL inicial F2 completa fue 9,016434; comparar con el valor final demuestra ajuste estadístico fuera de train bajo este split. No demuestra comprensión, respuesta a instrucciones ni robustez de generalización semántica. Splits disjuntos por hash/familia/componente conocido; no se certifica recall perfecto de near-dedup ni ausencia de todas las paráfrasis/traducciones EN/ES. No se abrió confirmatorio sellado.

La selección es investigación privada bajo declaración CC BY-SA original-text, con licencia/atribución individual conservadas. La clasificación histórica CONDITIONAL y sus límites documentales no se borran ni se convierten en aprobación general de difusión de pesos. Cribado de excepciones explícitas no equivale a revisión legal manual exhaustiva. Publicar corpus/pesos exige resolver esa decisión separadamente.
