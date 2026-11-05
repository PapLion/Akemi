# Localización y límites

|Condición|Aux train|CE|Respuesta original|Aux layout nuevo|Respuesta layout|Segundos|
|---|---:|---:|---:|---:|---:|---:|
|A|45.59%|1.2182|99.22%|40.90%|67.50%|22.0|
|B|56.48%|1.0504|28.91%|51.21%|30.00%|22.0|
|C|54.26%|1.0540|41.09%|30.43%|25.62%|26.5|
|D|52.38%|1.0484|25.00%|38.28%|25.00%|24.8|

Contadores por etapa (inicial, después de evento, antes de consulta) son medidas semánticas del decoder, no distancias:
```json
{
  "A": {
    "(0, 'correct')": 496,
    "(0, 'total')": 1280,
    "(2, 'correct')": 671,
    "(2, 'total')": 1280,
    "('retained', 'correct')": 649,
    "('retained', 'total')": 1280
  },
  "B": {
    "(0, 'correct')": 780,
    "(0, 'total')": 1280,
    "(2, 'correct')": 666,
    "(2, 'total')": 1280,
    "('retained', 'correct')": 571,
    "('retained', 'total')": 1280
  },
  "C": {
    "(0, 'correct')": 712,
    "(0, 'total')": 1280,
    "(2, 'correct')": 677,
    "(2, 'total')": 1280,
    "('retained', 'correct')": 612,
    "('retained', 'total')": 1280
  },
  "D": {
    "(0, 'correct')": 714,
    "(0, 'total')": 1280,
    "(2, 'correct')": 627,
    "(2, 'total')": 1280,
    "('retained', 'correct')": 337,
    "('retained', 'total')": 1280
  }
}
```

La prueba exige representar dos valores desde el inicio. Un fallo ya en chunk0 no permite atribuir toda caída al borrado de la tercera escritura. Comparar etapa inicial y posterior separa parcialmente esas posibilidades, pero los pesos se entrenan conjuntamente: no demuestra una única causa interna.

El experimento previo simple/distractores duplicó targets; aquí permanecen iguales en los cuatro brazos. No hay contraste de número de targets aislado: no puede estimarse cuánto del fracaso anterior fue causado por ese aumento. También cambian diversidad de combinaciones y definición de supervisión; no comparar porcentajes como si fuera una sola intervención.
