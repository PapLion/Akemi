"""Descriptive CPU costs and convergence, no inference of architecture superiority."""
import json,statistics,collections
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 rr=[json.loads(p.read_text()) for p in sorted((R/'results/extend').glob('*.json'))];perf=json.loads((R/'results/cpu-performance.json').read_text())
 lines=['# Rendimiento CPU','','Medición aislada posterior al aprendizaje: FP32,un thread,batch8,64IDs,8targets/update,4warmups+10mediciones. Inicializaciones desechables; mismas entradas. No hay profiler ni otros entrenadores simultáneos. AdamW incluye clipping; forward incluye preparación de máscaras. RAM es pico acumulado del proceso, no pico aislado del modelo.','','|Modelo|Ventana|Parámetros totales/activos|Forward ms|Backward ms|Clip+AdamW ms|Update ms ±SD|Targets/s|','|---|---:|---:|---:|---:|---:|---:|']
 for r in perf['results']:
  lines.append(f"|{r['arm']}|{r['window']}|{r['parameters']}/{r['active_parameters']}|{r['forward_ms']:.2f}|{r['backward_ms']:.2f}|{r['clip_adamw_ms']:.2f}|{r['update_ms']:.2f} ± {r['update_ms_sd']:.2f}|{r['targets_per_second']:.2f}|")
 lines+=['','Cada programa contiene64posiciones de entrada, pero UN target supervisado. Targets/s no equivale a throughput de un LM denso. El modelo calcula logits de todas las posiciones aunque la loss solo usa la última: coste común conservado para comparabilidad; no optimizado aquí. Atención en matrices densas con máscara local, no kernel disperso.','','Los FLOPs de linear registrados son una cota parcial de forward. Se añade por separado el head funcional atado; quedan fuera atención, normas, no linealidades, backward y AdamW. No se afirma comparación a igual cómputo. Los híbridos ejecutan8actualizaciones de memoria por programa, el histórico64; gates blandos no ahorran esas operaciones.','','## Coste real de las trayectorias primarias','','|Modelo/ventana|Semilla|Updates|Respuestas|Segundos de updates|Media ms/update|','|---|---:|---:|---:|---:|---:|']
 for r in rr:lines.append(f"|{r['arm']}/{r['window']}|{r['seed']}|{r['step']}|{sum(t['targets'] for t in r['updates'])}|{r['training_seconds']:.2f}|{1000*r['training_seconds']/r['step']:.2f}|")
 lines+=['',f"Suma de tiempo interno de updates primarios: {sum(r['training_seconds'] for r in rr):.2f}s. No incluye evaluaciones/checkpointing ni pilotos rechazados. Los tiempos aislados y los de trayectoria son mediciones diferentes; no sustituir unos por otros."]
 (R/'CPU_PERFORMANCE.md').write_text('\n'.join(lines)+'\n')
 lines=['# Curvas y trayectoria por semilla','','Curvas completas por update: results/curves.csv. Cortes comunes aquí; checkpoints finales prefijados, sin elegir el mejor dev.','','|Modelo/ventana|Semilla|Update|NLL IID|Exactitud IID|Fuera|Reciente|','|---|---:|---:|---:|---:|---:|---:|']
 for r in rr:
  for c in r['cuts']:
   if c['step'] in [0,100,300,1000]:
    m=c['metrics'];lines.append(f"|{r['arm']}/{r['window']}|{r['seed']}|{c['step']}|{m['nll']:.4f}|{100*m['accuracy']:.2f}|{100*m['outside_accuracy']:.2f}|{100*m['recent_accuracy']:.2f}|")
 (R/'CONVERGENCE.md').write_text('\n'.join(lines)+'\n')
 paired=json.loads((R/'results/paired-statistics.json').read_text());lines=['# Comparaciones exploratorias emparejadas','','Mismos programas y minibatches por semilla. Ganancias/pérdidas frente a histórico sin Hielo, solo IID fuera de ventana. Tres semillas originales; los120programas se reutilizan entre semillas y no son360muestras independientes. No se declaran p-values ni superioridad poblacional.','','|Brazo|Semilla|N programas|Gana|Pierde|Diferencia pp|','|---|---:|---:|---:|---:|---:|']
 for r in paired:lines.append(f"|{r['arm']}|{r['seed']}|{r['n']}|{r['wins']}|{r['losses']}|{100*r['paired_difference']:+.2f}|")
 lines+=['','La dispersión entre semillas aparece como desviación estándar muestral en RESULTS.md. El máximo de heurísticas por posición y la selección piloto entre híbridos son exploratorios; no constituyen evaluación final independiente. Una ventaja causal útil exige además contrafactuales correctos y degradación de exactitud al intervenir la memoria, no únicamente cambiar logits.']
 (R/'STATISTICS.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
