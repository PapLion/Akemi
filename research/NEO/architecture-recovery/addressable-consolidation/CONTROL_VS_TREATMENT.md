# Control frente a tratamiento

|Semilla|Brazo|Corrección: lector pares nuevos|Binding corregido (aux)|Binding no modificado (aux)|Lector layout alternativo|Conjunta pares nuevos (formación)|
|---|---|---:|---:|---:|---:|---:|
|17|A|79.17%|75.00%|83.33%|87.50%|90.00%|
|17|B|98.23%|100.00%|95.42%|100.00%|99.58%|
|29|A|78.65%|74.06%|86.67%|81.46%|90.83%|
|29|B|89.79%|100.00%|86.67%|100.00%|92.92%|
|43|A|65.42%|35.21%|97.71%|80.52%|99.58%|
|43|B|91.25%|100.00%|82.50%|96.25%|90.00%|

|Semilla|Brazo|Lector: entidad corregida|Lector: entidad no modificada|
|---|---|---:|---:|
|17|A|75.00%|83.33%|
|17|B|100.00%|96.46%|
|29|A|74.79%|82.50%|
|29|B|100.00%|79.58%|
|43|A|33.54%|97.29%|
|43|B|100.00%|82.50%|

Cada subgrupo funcional contiene480consultas; las columnas de binding de la primera tabla son del decoder auxiliar y no sustituyen al lector normal. El gate prospectivo usó esos bindings y la respuesta normal agregada; el desglose funcional se reporta además sin redefinir el triaje.

El efecto de añadir correcciones es positivo en la respuesta normal de las tres semillas en pares nuevos, pero falla el requisito de conservación en confirmaciones29y43. Ver summary.csv,predicciones y confusiones por entidad/valor en cada familia. `correction_fit` es ajuste, no prueba de generalización.

Diferencias emparejadas y rangos descriptivos en paired-summary.json. Solo tres semillas; las960variantes por familia reutilizan combinaciones y no son960pruebas independientes. No afirmar robustez poblacional ni inteligencia. El aumento de gradientes por exposición es parte de la intervención de datos, no una modificación del objetivo.
