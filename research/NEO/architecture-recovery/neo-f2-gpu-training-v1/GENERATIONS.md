# Generaciones congeladas, sin selección estética

Greedy, 64 tokens nuevos, contexto móvil128, controles256:512 inhibidos para salida textual. No hubo muestreo ni selección entre múltiples semillas. El checkpoint F2 descargado se cargó con V3 en CPU y reprodujo los primeros8IDs greedy de GPU (results/F2-local-tokenized-inference.json). Esto tampoco certifica formato de parada EOS.

## F2

Prompt: La historia de

```text
 la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la
```

TTR por palabras=0.0469; fracción trigramas repetidos=0.9516.

Prompt: The purpose of

```text
 the 1999, the 1999, the 1999, the first-s of the 1999, the 1999, the 1999, the first time of the first time of the first-s of the first-1
```

TTR por palabras=0.25; fracción trigramas repetidos=0.5.

Prompt: En matemáticas,

```text
 "S) y "S) y la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de
```

TTR por palabras=0.0862; fracción trigramas repetidos=0.875.

Prompt: A Python function

```text


Pa

Pa

Pa

Pa
Pa
Pa
Pa
Pa

Pa
Pa

Pa
Pa

Pa
Pa

Pa

Pa
Pa

Pa
```

TTR por palabras=0.0556; fracción trigramas repetidos=0.9375.

## Transformer

Prompt: La historia de

```text
 la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la ciudad de la
```

TTR por palabras=0.0469; fracción trigramas repetidos=0.9516.

Prompt: The purpose of

```text
 the "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The "The
```

TTR por palabras=0.0909; fracción trigramas repetidos=0.9.

Prompt: En matemáticas,

```text
 1999–1989, 1999, 1999, 1999, 1999, 1999.

In 1999, the 1999s, the 1999
```

TTR por palabras=0.5833; fracción trigramas repetidos=0.1.

Prompt: A Python function

```text
 (1999) is a number of the 1999-1900.

In 1999, the 1990s, the 1990s, the 1990s, the 1990s,
```

TTR por palabras=0.5882; fracción trigramas repetidos=0.2667.
