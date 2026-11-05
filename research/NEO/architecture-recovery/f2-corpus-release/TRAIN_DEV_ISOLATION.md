# Aislamiento train/dev

Siete tests adicionales PASS. Para candidatos, conjuntos de clave, SHA limpio, familia documental y componente de deduplicación son disjuntos. Ningún split test histórico se abrió. Se usa únicamente keep de 1B refinado, por lo que las 411 exclusiones posteriores no entran.

Se reutiliza el grafo de near-dedup histórico (Jaccard 0,85 y otros criterios de aquella ejecución), no se vuelve a auditar todo el corpus. Su recall no es exhaustivo: no certifica ausencia de traducciones, paráfrasis ni contaminación con todos los benchmarks públicos. EN/ES pueden compartir conceptos; no se afirma separación semántica total. Esta limitación mantiene deduplicación/splits en CONDITIONAL para el release candidato hasta revisión específica. Los cinco documentos aprobados conservan separación por repositorio y el chequeo previo de shingles sin coincidencias.

No se utilizaron conjuntos sellados para elegir documentos, modelos ni proporciones. Las claves de test se contabilizan como metadatos, sin leer sus textos.
