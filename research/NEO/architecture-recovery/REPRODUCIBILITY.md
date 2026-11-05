# Reproducción

Repositorio de investigación aislado en la rama `cryo-next-generation-v1`; no se modifica ni se hace merge del código histórico. Versiones/hashes en SOURCE_MANIFEST.json y ARTIFACT_MANIFEST.json. El tokenizer se reutiliza solo en lectura desde `../neotoken-v3/`. El snapshot histórico y el usado al empezar el aprendizaje están en vendor/.

```bash
cd /PATH/TO/NEO_HOME/research/neo-architecture-recovery/cryo-next-generation
export NEO_PYTHON=/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python
./run_checks.sh
# En un directorio de salida nuevo si se quieren preservar estas evidencias:
"$NEO_PYTHON" tasks.py
"$NEO_PYTHON" experiment.py preflight
"$NEO_PYTHON" experiment.py learn --max-seconds 2400
"$NEO_PYTHON" extend_learning.py
"$NEO_PYTHON" performance.py bench
"$NEO_PYTHON" performance.py profile
"$NEO_PYTHON" probes.py
"$NEO_PYTHON" probes.py --stage learning-1000 --output learning-1000-probes
"$NEO_PYTHON" analyze_controls.py
"$NEO_PYTHON" summarize.py
"$NEO_PYTHON" samples.py
"$NEO_PYTHON" report_probes.py
"$NEO_PYTHON" future_cuda.py
```

`learn` y `extend_learning` reutilizan resultados ya presentes. Para repetir mediciones desde cero, copiar este experimento a otro directorio y mantener las dependencias relativas de tokenizer/referencia, o elegir una copia dentro del mismo padre. No borrar evidencias originales. Los scripts no tienen lock multiinstancia: **ejecutar secuencialmente**, sin otro entrenamiento/benchmark concurrente. Preflight y tasks escriben sus artefactos enresults, por lo que hay que preservar la versión anterior al repetirlos.

Checkpoints locales PyTorch solo con tensores/tipos básicos y lectura `weights_only=True`, sin pickle genérico. No son pesos históricos ni modelos oficiales. Los `.pt` y las trazas grandes se conservan localmente y se excluyen deGit. ManifestSHA permite identificarlos sin redistribuirlos.

Los tiempos dependen de carga del sistema. Un threadCPU, FP32, dropout0; las fases de throughput y profiling se ejecutaron sin aprendizaje concurrente. Los tests adicionales de ingeniería sí se ejecutaron durante la extensión y pueden afectar ligeramente sus tiempos. No usar tiempos de extensión como benchmark aislado de rendimiento.

Para congelar el conjunto completo terminado: `"$NEO_PYTHON" build_manifest.py` y `"$NEO_PYTHON" verify_artifacts.py`. El primer comando exige las30trayectorias completas en ambos cortes y sus checkpoints; no se debe regenerar el manifiesto sobre resultados alterados y presentarlos como el mismo experimento.
