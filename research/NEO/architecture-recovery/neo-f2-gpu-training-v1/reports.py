from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parent;D=R/'private/download/results';RES=R/'results'
def load(p):return json.loads(Path(p).read_text())
def put(n,s):(R/n).write_text(s.strip()+'\n')
summaries={k:load(D/k/'summary.json') for k in ['F2','Transformer'] if (D/k/'summary.json').exists()}
assert 'F2' in summaries
bill=load(RES/'billing.json');plan=load(RES/'rental-plan.json');pre=load(RES/'cuda-preflight.json')
for k,s in summaries.items():
 (RES/(k+'-summary.json')).write_text(json.dumps(s,indent=2)+'\n')
 # Curves are numerical optimization records, without corpus text.
 import shutil
 shutil.copy(D/k/'curve.jsonl',RES/(k+'-curve.jsonl'))
summary=summaries['F2'];dev=summary['dev'];total=sum(s['targets'] for s in summaries.values())
put('README.md','''# Primer entrenamiento lingüístico F2 en GPU

Ver TRAINING_RESULTS.md, EVALUATION.md, COST_REPORT.md y DECISION.md. No es una certificación de capacidad conversacional ni de Hielo/Trapos. Datos y pesos permanecen privados en private/; Git conserva código, métricas agregadas y hashes. Corpus original y experimentos históricos intactos.''')
put('GPU_ENVIRONMENT.md','''# Entorno GPU medido

'''+(RES/'gpu-environment.log').read_text()+'''
Imagen por digest en results/rental-plan.json. Una RTX3090, sin volúmenes extra. Hashes del paquete comprobados después de transferir; dos dependencias V3 fijadas regex2026.9.29/tokenizers0.23.3. SSH con primera clave fijada desde endpoint Vast autenticado y StrictHostKeyChecking=yes; la API execute rechazó consultas sobre instancia activa, así que no se obtuvo una huella independiente por ese canal. No se desactivó comprobación posterior de cambios de clave.

CUDA preflight PASS, con causalidad, padding, aislamiento, gradientes y AdamW; recuperación exacta4vs2+2 sobre corpus real. Primer preflight falló por map_location CUDA que desplazaba el contador escalar de AdamW: se preservó fallo y se reparó solamente el cargador. No se cambió el modelo ni las tolerancias. BF16 diagnóstico finito, máximo delta de logits '''+str(pre['bf16'].get('max_logit_abs_vs_fp32'))+'''; no certificado para entrenamiento BF16. Receta principal FP32. Tras completar F2 apareció una dependencia de empaquetado ausente en generación: packing.py. Se transfirió el original sin modificaciones, se conservaron el error y su SHA, y se completó evaluación/generación desde final.pt sin pasos de optimizador adicionales. El preflight inicial no había cubierto esa importación de generación; no se presenta como certificado previo de generación.''')
put('TRAINING_RESULTS.md',f'''# Entrenamiento F2 ejecutado

Checkpoint final fijo, sin selección por dev. **{summary['targets']:,} targets** en {summary['updates']:,} updates; una pasada, máximo5M no excedido. La diferencia frente a5M son77.556targets; no se rellenó repitiendo datos. Nueve artículos excluidos por marcadores explícitos de derechos, sin cambiar fuente ni tokenizer.

NLL online ponderada durante optimización: {summary['online_train_nll']:.6f}. NLL final de muestra train fija ({summary['final_train_sample_targets']}targets): {summary['final_train_fixed_sample_nll']:.6f}. Esas dos magnitudes no se confunden con NLL sobre todo train al checkpoint final. Curvas numéricas completas por update en private/download/results/F2/curve.jsonl y copia local results/F2-curve.jsonl (fuera de Git); CSV por grupos de100updates y SVG para revisión; checkpoints periódicos aproximadamente cada1Mtargets y final.

AdamW, RNG CPU/CUDA/Python, identidad y cursor/orden de datos presentes. NumPy se usa solo para lectura, sin RNG de NumPy en la trayectoria; numpy_rng=None no omite una fuente aleatoria utilizada. Checkpoints solamente en fronteras de update, sin acumulación parcial. Validación local de carga/inferencia y estados en results/F2-local-verification.json.

El checkpoint final conserva el mismo SHA antes y después de recuperar la evaluación/generación. No se modificaron dimensiones, capas, batch, LR, clipping ni objetivos durante entrenamiento. Gradientes finitos verificados en cada update. No se entrenó Hielo ni Trapos.''')
rows='\n'.join(f"| {k} | {s['dev']['all']['nll']:.6f} | {s['dev']['all']['ppl']:.3f} | {s['dev']['es']['nll']:.6f} | {s['dev']['en']['nll']:.6f} | {s['dev']['es']['ppl']:.3f} | {s['dev']['en']['ppl']:.3f} |" for k,s in summaries.items())
put('EVALUATION.md',f'''# Evaluación final completa

| Modelo | NLL dev | PPL dev | NLL ES | NLL EN | PPL ES | PPL EN |
|---|---:|---:|---:|---:|---:|---:|
{rows}

Dev completo212.105targets,70artículos: ES107.333/EN104.772. Dominio: enciclopedia; no existe aquí dev de código independiente suficiente para una conclusión técnica por dominio. NLL/PPL usan todos los siguientes tokens válidos, incluidos EOS, sin padding ni transiciones documentales. Cada target una vez con ventanas de128 y stride127. Posiciones se reinician por ventana como en el F2 preparado.

La NLL inicial F2 completa fue9,016434; comparar con el valor final demuestra ajuste estadístico fuera de train bajo este split. No demuestra comprensión, respuesta a instrucciones ni robustez de generalización semántica. Splits disjuntos por hash/familia/componente conocido; no se certifica recall perfecto de near-dedup ni ausencia de todas las paráfrasis/traducciones EN/ES. No se abrió confirmatorio sellado.

La selección es investigación privada bajo declaración CC BY-SA original-text, con licencia/atribución individual conservadas. La clasificación histórica CONDITIONAL y sus límites documentales no se borran ni se convierten en aprobación general de difusión de pesos. Cribado de excepciones explícitas no equivale a revisión legal manual exhaustiva. Publicar corpus/pesos exige resolver esa decisión separadamente.''')
gens={k:load(D/k/'generations.json') for k in summaries};text='# Generaciones congeladas, sin selección estética\n\nGreedy,64tokens nuevos, contexto móvil128, controles256:512 inhibidos para salida textual. No hubo muestreo ni selección entre múltiples semillas. El checkpoint F2 descargado se cargó con V3 en CPU y reprodujo los primeros8IDs greedy de GPU (results/F2-local-tokenized-inference.json). Esto tampoco certifica formato de parada EOS.\n\n'
for k,gs in gens.items():
 text+='## '+k+'\n\n'
 for g in gs:text+='Prompt: '+g['prompt']+'\n\n```text\n'+g['generated']+'\n```\n\nTTR por palabras='+str(round(g['word_type_token_ratio'],4))+'; fracción trigramas repetidos='+str(round(g['repeated_trigram_fraction'],4))+'.\n\n'
put('GENERATIONS.md',text)
perf='\n'.join(f"| {k} | {s['parameters']} | {s['targets_per_second']:.2f} | {s['update_seconds']:.2f} | {s['wall_seconds_this_process']:.2f} | {('no certificado' if k=='F2' else format(s['peak_gpu_allocated']/2**20,'.2f'))} |" for k,s in summaries.items())
put('GPU_PERFORMANCE.md',f'''# Rendimiento observado

| Modelo | Parámetros | Targets/s updates | Segundos updates | Wall reportado | Pico alloc entrenamiento MiB |
|---|---:|---:|---:|---:|---:|
{perf}

Targets/s de updates excluye tokenización, batch transfer, evaluación, checkpoint y arranque. Para baseline, wall del worker empieza tras evaluación inicial e incluye evaluaciones intermedias/final y generación. Para F2, wall se reconstruyó desde el nacimiento del log (precisión de un segundo), excluyendo la evaluación inicial e incluyendo la pausa de reparación y reevaluación. La memoria F2 del summary es de la finalización, no un pico certificado de entrenamiento; las muestras por update y nvidia-smi quedan conservadas. No se equiparan esos contadores entre modelos. Tiempo total de alquiler separado en COST_REPORT. Telemetría periódica nvidia-smi en results/*-monitor.jsonl, memoria del proceso en summaries. Bajo uso de GPU no se atribuye automáticamente a una causa; código eager, batch2 y bucle de posiciones existentes sin optimización en esta ejecución. No se presenta como rendimiento GPU óptimo. FLOPs densos6P orientativos: F2≈12,49M/target; baseline≈12,20M, excluyendo coste cuadrático de atención y distinciones lookup/proyección compartida.''')
if 'Transformer' in summaries:
 b=summaries['Transformer'];winner='F2' if dev['all']['nll']<b['dev']['all']['nll'] else 'Transformer'
 put('BASELINE_COMPARISON.md',f'''# Baseline ejecutado

Mismos{summary['targets']}targets, dataset, orden, semilla17, contexto128, batch2 y AdamW. F2{summary['parameters']}parámetros frente a baseline{b['parameters']}; diferencia49.408. F2 conserva su refinamiento rápido adicional; baseline norm final estándar. No es igualdad de FLOPs exacta.

Menor NLL dev:{winner}. Diferencia F2−baseline={dev['all']['nll']-b['dev']['all']['nll']:.6f}. Una semilla, un corpus enciclopédico y5Mtargets aproximadamente no establecen superioridad arquitectónica general. Baseline solo se lanzó tras exportar F2 y validar su checkpoint localmente.''')
put('COST_REPORT.md',f'''# Gasto y cierre

Instancia{load(RES/'rental-receipt.json')['instance_id']}; oferta{plan['offer_id']}; GPU quote{plan['hourly_gpu_quote']:.6f}USD/h, disco conservador{plan['disk_hour_conservative']:.6f}USD/h. Tarifa activa API reportó0,184074USD/h. Crédito antes{bill['credit_before']:.11f}, después{bill['credit_after']:.11f}; descenso observado**USD{bill['observed_credit_decrease']:.8f}**, bajo máximo5USD. No recarga ni segundo alquiler.

Coste observado total asignado a{total:,}targets entrenados entre modelos: USD{bill['observed_credit_decrease']/total*1e6:.6f}/Mtargets, incluyendo arranque/exportación; no es coste marginal puro de kernels. El intervalo de alquiler y deadline figuran en recibos, cierre en cleanup.json. Factura consultada queda privada; pueden aparecer ajustes de almacenamiento/tráfico o redondeo, por lo que no se declara liquidación definitiva.

API confirmó ausencia de instancia y listado de volúmenes al cierre: results/billing.json. Destrucción --yes, ausencia verificada; no se confunde estado detenido con recurso eliminado. Watchdog no necesitó dispararse; no se afirma garantía financiera absoluta.''')
put('DECISION.md',f'''# Primer checkpoint F2 lingüístico completado

Se entrenó F2 sobre{summary['targets']:,}targets reales ES/EN, sin repetición de relleno, HieloOFF/TraposOFF. Dev NLL{dev['all']['nll']:.6f}, PPL{dev['all']['ppl']:.3f}. Estado final y optimizador descargados, hashes cotejados y carga/inferencia CPU verificadas. La instancia fue destruida y la API confirmó ausencia. No se publicaron pesos ni corpus.

La reducción de NLL frente a inicialización muestra aprendizaje estadístico en ambos idiomas cuando así lo respaldan las métricas desglosadas; no se afirma comprensión. Generaciones completas congeladas en GENERATIONS.md permiten observar repetición y limitaciones sin escoger ejemplos bonitos. El dev es enciclopédico; no certifica otros dominios.

El siguiente escalón se justifica por curvas de aprendizaje, validación y comparación baseline, no por los microfits simbólicos. Antes de ampliarlo: revisar calidad/diversidad y obligaciones de publicación, replicación y presupuesto nuevo. No se inicia F8, Hielo lingüístico, Trapos, otra arquitectura ni entrenamiento adicional automáticamente. Los límites de derechos del release histórico siguen documentados: este uso privado concreto no es una aprobación general de distribución.''')
if 'Transformer' in summaries:
 b=summaries['Transformer'];p=R/'DECISION.md';p.write_text(p.read_text()+f'\nEn este contraste el Transformer obtiene menor NLL dev ({b["dev"]["all"]["nll"]:.6f} frente a {dev["all"]["nll"]:.6f}) y {b["targets_per_second"]/summary["targets_per_second"]-1:.2%} más targets/s de actualización. No hay evidencia aquí para preferir F2 al baseline. Antes de aumentar escala, usar el baseline como referencia y estudiar de forma aislada la contribución del refinamiento rápido o de la receta; no iniciar esa investigación automáticamente. Una semilla no establece superioridad general.\n')
# Hash every downloaded artifact, including periodic checkpoints, without placing payload in Git.
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'private/download').rglob('*') if p.is_file()}
(RES/'artifact-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
public={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and 'private' not in p.parts and '__pycache__' not in p.parts and p.name!='SHA256SUMS.json'}
(R/'SHA256SUMS.json').write_text(json.dumps(public,indent=2)+'\n')
print('reports generated')
