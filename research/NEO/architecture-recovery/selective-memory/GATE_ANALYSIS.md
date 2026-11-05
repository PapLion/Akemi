# Trapos: observaciones del filtro

32ejemplos IID estratificados (dos recientes y dos fuera por tarea) por checkpoint. Histórico:64actualizaciones por token; híbridos:8por fragmento. La última escritura híbrida ocurre después de la respuesta y se excluye de estos agregados; permanece en los registros crudos. Categorías superpuestas. Estadística descriptiva condicionada a tarea/posición, sin causalidad identificada de cada dimensión de gate. Todas las actualizaciones densas se ejecutan, independientemente de gate.

|Modelo|Semilla|Categoría de fragmento|N|Write medio|Erase medio|Delta Hielo|Fracción write<0.05|Fracción write>0.95|
|---|---:|---|---:|---:|---:|---:|---:|---:|
|delta_fast|17|todos|224|0.0827|0.6536|0.2851|0.5967|0.0004|
|delta_fast|17|escritura vigente|32|0.1231|0.6500|0.4296|0.5352|0.0010|
|delta_fast|17|actualización aceptada entidad|55|0.1354|0.6484|0.4644|0.5489|0.0017|
|delta_fast|17|propuesta rechazada entidad|64|0.0815|0.6502|0.2983|0.6006|0.0000|
|delta_fast|29|todos|224|0.2315|0.7549|0.6843|0.0622|0.0000|
|delta_fast|29|escritura vigente|32|0.2468|0.8066|1.0650|0.0771|0.0000|
|delta_fast|29|actualización aceptada entidad|55|0.2595|0.7958|1.0220|0.0602|0.0000|
|delta_fast|29|propuesta rechazada entidad|64|0.2266|0.7275|0.6241|0.0649|0.0000|
|delta_fast|43|todos|224|0.1331|0.9191|0.4746|0.2956|0.0000|
|delta_fast|43|escritura vigente|32|0.1535|0.9071|0.6176|0.2471|0.0000|
|delta_fast|43|actualización aceptada entidad|55|0.1478|0.9113|0.5569|0.2733|0.0000|
|delta_fast|43|propuesta rechazada entidad|64|0.1333|0.9239|0.4741|0.3027|0.0000|
|event_fast|17|todos|224|0.0893|0.6137|1.5191|0.6791|0.0054|
|event_fast|17|escritura vigente|32|0.1213|0.6143|1.7224|0.6248|0.0127|
|event_fast|17|actualización aceptada entidad|55|0.1308|0.5992|1.8468|0.6001|0.0151|
|event_fast|17|propuesta rechazada entidad|64|0.0883|0.6173|1.4432|0.6766|0.0000|
|event_fast|29|todos|224|0.3501|0.4816|3.0489|0.1627|0.0352|
|event_fast|29|escritura vigente|32|0.3658|0.5088|3.5764|0.1387|0.0425|
|event_fast|29|actualización aceptada entidad|55|0.3758|0.5129|3.5118|0.1277|0.0426|
|event_fast|29|propuesta rechazada entidad|64|0.3341|0.4839|2.9674|0.1936|0.0391|
|event_fast|43|todos|224|0.1894|0.7596|2.4054|0.4568|0.0203|
|event_fast|43|escritura vigente|32|0.2326|0.7134|2.7848|0.3760|0.0303|
|event_fast|43|actualización aceptada entidad|55|0.2221|0.7177|2.7479|0.4068|0.0267|
|event_fast|43|propuesta rechazada entidad|64|0.1868|0.7683|2.3734|0.4670|0.0209|
|intact|17|todos|2048|0.1259|no aplica|0.3494|0.6123|0.0001|
|intact|17|escritura vigente|128|0.1585|no aplica|0.5088|0.4849|0.0007|
|intact|17|actualización aceptada entidad|228|0.1648|no aplica|0.5362|0.5090|0.0012|
|intact|17|propuesta rechazada entidad|412|0.1174|no aplica|0.2861|0.6419|0.0000|
|intact|29|todos|2048|0.2702|no aplica|1.1989|0.0990|0.0023|
|intact|29|escritura vigente|128|0.3104|no aplica|1.4124|0.0889|0.0034|
|intact|29|actualización aceptada entidad|228|0.2811|no aplica|1.2463|0.0970|0.0023|
|intact|29|propuesta rechazada entidad|412|0.2692|no aplica|1.1761|0.1085|0.0042|
|intact|43|todos|2048|0.2616|no aplica|0.9593|0.1459|0.0003|
|intact|43|escritura vigente|128|0.3305|no aplica|1.2296|0.0947|0.0002|
|intact|43|actualización aceptada entidad|228|0.3003|no aplica|1.0957|0.1214|0.0001|
|intact|43|propuesta rechazada entidad|412|0.2404|no aplica|0.8597|0.1627|0.0006|
