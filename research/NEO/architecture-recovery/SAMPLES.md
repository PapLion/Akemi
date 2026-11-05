# Muestras deterministas, sin selección por acierto

Primer ID dev por tarea, brazos principales, todas las semillas, último update1000. No es generación libre: predicción de un token de respuesta con vocabulario completo. Los cuatro dígitos finales de cada registro son distractores. El corpus y el resto de predicciones están enresults.

## dev-goal-0000

```text
+G51663
!D70120
%A09595
#D19754
:E06835
%F37168
#C64339
>G06845
```

Respuesta del oráculo: `5`. Entidad consultada: `G`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'6'` | 54 | False |
| b0_local | 29 | `'2'` | 50 | False |
| b0_local | 43 | `'2'` | 50 | False |
| b0_full | 17 | `'0'` | 48 | False |
| b0_full | 29 | `'2'` | 50 | False |
| b0_full | 43 | `'2'` | 50 | False |
| cryo_history | 17 | `'5'` | 53 | True |
| cryo_history | 29 | `'5'` | 53 | True |
| cryo_history | 43 | `'5'` | 53 | True |
| event | 17 | `'6'` | 54 | False |
| event | 29 | `'7'` | 55 | False |
| event | 43 | `'7'` | 55 | False |
| delta | 17 | `'7'` | 55 | False |
| delta | 29 | `'2'` | 50 | False |
| delta | 43 | `'3'` | 51 | False |

## dev-retention-0000

```text
!H08926
;B17253
!A54773
#F56531
%D31446
%F45697
%A64472
?H04706
```

Respuesta del oráculo: `0`. Entidad consultada: `H`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'1'` | 49 | False |
| b0_local | 29 | `'1'` | 49 | False |
| b0_local | 43 | `'1'` | 49 | False |
| b0_full | 17 | `'3'` | 51 | False |
| b0_full | 29 | `'1'` | 49 | False |
| b0_full | 43 | `'6'` | 54 | False |
| cryo_history | 17 | `'0'` | 48 | True |
| cryo_history | 29 | `'0'` | 48 | True |
| cryo_history | 43 | `'0'` | 48 | True |
| event | 17 | `'3'` | 51 | False |
| event | 29 | `'1'` | 49 | False |
| event | 43 | `'1'` | 49 | False |
| delta | 17 | `'1'` | 49 | False |
| delta | 29 | `'2'` | 50 | False |
| delta | 43 | `'2'` | 50 | False |

## dev-correction-0000

```text
!D54116
;E10095
=D41625
#H56893
;H11011
#A52617
;H27912
?D07982
```

Respuesta del oráculo: `4`. Entidad consultada: `D`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'2'` | 50 | False |
| b0_local | 29 | `'6'` | 54 | False |
| b0_local | 43 | `'3'` | 51 | False |
| b0_full | 17 | `'6'` | 54 | False |
| b0_full | 29 | `'5'` | 53 | False |
| b0_full | 43 | `'6'` | 54 | False |
| cryo_history | 17 | `'2'` | 50 | False |
| cryo_history | 29 | `'5'` | 53 | False |
| cryo_history | 43 | `'4'` | 52 | True |
| event | 17 | `'1'` | 49 | False |
| event | 29 | `'5'` | 53 | False |
| event | 43 | `'7'` | 55 | False |
| delta | 17 | `'2'` | 50 | False |
| delta | 29 | `'5'` | 53 | False |
| delta | 43 | `'6'` | 54 | False |

## dev-irrelevance-0000

```text
!H05793
#F60630
%F66700
#C47418
~H50142
:G41287
%D25361
?H04867
```

Respuesta del oráculo: `0`. Entidad consultada: `H`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'1'` | 49 | False |
| b0_local | 29 | `'1'` | 49 | False |
| b0_local | 43 | `'7'` | 55 | False |
| b0_full | 17 | `'3'` | 51 | False |
| b0_full | 29 | `'3'` | 51 | False |
| b0_full | 43 | `'5'` | 53 | False |
| cryo_history | 17 | `'0'` | 48 | True |
| cryo_history | 29 | `'0'` | 48 | True |
| cryo_history | 43 | `'0'` | 48 | True |
| event | 17 | `'1'` | 49 | False |
| event | 29 | `'1'` | 49 | False |
| event | 43 | `'7'` | 55 | False |
| delta | 17 | `'1'` | 49 | False |
| delta | 29 | `'1'` | 49 | False |
| delta | 43 | `'3'` | 51 | False |

## dev-constraint-0000

```text
$H49611
:B25828
#F79614
%F72946
#D29986
!C67297
#F44103
<H09437
```

Respuesta del oráculo: `4`. Entidad consultada: `H`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'6'` | 54 | False |
| b0_local | 29 | `'3'` | 51 | False |
| b0_local | 43 | `'3'` | 51 | False |
| b0_full | 17 | `'3'` | 51 | False |
| b0_full | 29 | `'1'` | 49 | False |
| b0_full | 43 | `'7'` | 55 | False |
| cryo_history | 17 | `'4'` | 52 | True |
| cryo_history | 29 | `'0'` | 48 | False |
| cryo_history | 43 | `'4'` | 52 | True |
| event | 17 | `'7'` | 55 | False |
| event | 29 | `'6'` | 54 | False |
| event | 43 | `'3'` | 51 | False |
| delta | 17 | `'7'` | 55 | False |
| delta | 29 | `'3'` | 51 | False |
| delta | 43 | `'3'` | 51 | False |

## dev-entities-0000

```text
!A37913
#G48496
!D01092
!E22410
!D12433
!D24567
!B34717
?A02662
```

Respuesta del oráculo: `3`. Entidad consultada: `A`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'0'` | 48 | False |
| b0_local | 29 | `'0'` | 48 | False |
| b0_local | 43 | `'5'` | 53 | False |
| b0_full | 17 | `'0'` | 48 | False |
| b0_full | 29 | `'0'` | 48 | False |
| b0_full | 43 | `'2'` | 50 | False |
| cryo_history | 17 | `'6'` | 54 | False |
| cryo_history | 29 | `'3'` | 51 | True |
| cryo_history | 43 | `'3'` | 51 | True |
| event | 17 | `'0'` | 48 | False |
| event | 29 | `'0'` | 48 | False |
| event | 43 | `'2'` | 50 | False |
| delta | 17 | `'0'` | 48 | False |
| delta | 29 | `'5'` | 53 | False |
| delta | 43 | `'6'` | 54 | False |

## dev-hypothesis-0000

```text
^D24806
:B45645
;A10757
!C77007
-D22319
^D03062
#B52848
/D04341
```

Respuesta del oráculo: `0`. Entidad consultada: `D`.

| Brazo | Semilla | Predicción | ID | Correcta |
|---|---:|---|---:|---|
| b0_local | 17 | `'1'` | 49 | False |
| b0_local | 29 | `'6'` | 54 | False |
| b0_local | 43 | `'3'` | 51 | False |
| b0_full | 17 | `'1'` | 49 | False |
| b0_full | 29 | `'1'` | 49 | False |
| b0_full | 43 | `'7'` | 55 | False |
| cryo_history | 17 | `'2'` | 50 | False |
| cryo_history | 29 | `'5'` | 53 | False |
| cryo_history | 43 | `'2'` | 50 | False |
| event | 17 | `'2'` | 50 | False |
| event | 29 | `'3'` | 51 | False |
| event | 43 | `'3'` | 51 | False |
| delta | 17 | `'6'` | 54 | False |
| delta | 29 | `'2'` | 50 | False |
| delta | 43 | `'7'` | 55 | False |
