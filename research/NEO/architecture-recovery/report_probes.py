"""Regenerate contextual evidence table from saved complete measurements."""
import json,statistics
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 rr=json.loads((R/'results/learning-1000-probes/counterfactual-results.json').read_text());ss=json.loads((R/'results/learning-1000-probes/state-interventions.json').read_text())
 lines=['# Contrafactuales e intervención del estado','','Evaluación exploratoria posterior al primer ensayo; BENCHMARK_PROTOCOL.md.224pares por brazo/semilla. La edición mueve la combinación consultada al soporte train: su exactitud aislada no mide generalización composicional independiente. Se exige acertar ambos miembros.','','| Brazo | Ambos correctos % | Predicción cambia % | Exactitud editado % |','|---|---:|---:|---:|']
 for arm in dict.fromkeys(x['arm'] for x in rr):
  a=[x for x in rr if x['arm']==arm];lines.append('| '+arm+' | '+' | '.join(f"{100*statistics.mean(x[k] for x in a):.2f}" for k in ['both_correct','prediction_changed','cf_accuracy'])+' |')
 lines+=['','## Event: intervenciones de inferencia','','| Modo | Exactitud % | NLL | Cambio frente a soft % | Slots ejecutados/elegibles |','|---|---:|---:|---:|---|']
 for mode in ['soft','hard_0.5','no_persist_inference']:
  a=[x for x in ss if x['mode']==mode];lines.append(f"| {mode} | {100*statistics.mean(x['accuracy'] for x in a):.2f} | {statistics.mean(x['nll'] for x in a):.3f} | {100*statistics.mean(x['predictions_different_from_soft'] for x in a):.2f} | {sum(x['stats']['executed'] for x in a)}/{sum(x['stats']['eligible'] for x in a)} |")
 lines+=['','Una intervención de inferencia no sustituye la ablación entrenada. Ningún modoEvent resuelve este dev. Hard omite candidatos reales pero cambia la función; no acredita selección o ahorro aprendido. Velocidad del salto: PERFORMANCE.md.','','## Compuertas descriptivas','','| Modelo | Relevantes: write medio | Otros: write medio |','|---|---:|---:|']
 gates=json.loads((R/'results/gate-summary.json').read_text())
 for arm in ['event','delta']:
  a=[x for x in gates if x['stage']=='learning-1000' and x['arm']==arm];lines.append(f"| {arm} | {statistics.mean(x['mean_write'] for x in a if x['relevant']):.4f} | {statistics.mean(x['mean_write'] for x in a if not x['relevant']):.4f} |")
 lines+=['','Descripciones por semilla; no inferencia causal de relevancia. La clasificación de fragmentos relevantes usa el oráculoDSL, no un anotador humano ni supervisión adicional de gates. Su valor no demuestra que almacenen el hecho correcto.']
 (R/'CONTEXTUAL_PROBES.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
