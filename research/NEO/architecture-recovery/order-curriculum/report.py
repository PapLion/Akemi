import runpy
from pathlib import Path
globals().update({k:v for k,v in runpy.run_path(str(Path(__file__).with_name("run.py")),run_name="curriculum_module").items() if not k.startswith("__")})
def main():
 comp=json.loads((OUT/'comparison.json').read_text());audit={};exposure={}; cached=f.datasets()
 for arm,old in [('direct','C'),('curriculum','A')]:
  a=torch.load(OUT/f'{arm}-300.pt',weights_only=True);b=torch.load(BASE/f'distribution-scaling/results/{old}-300.pt',weights_only=True)
  audit[arm]={'historical_300_model_exact':equal(a['model'],b['model']),'historical_300_adamw_exact':equal(a['optimizer'],b['optimizer']),'historical_300_torch_rng_exact':equal(a['torch_rng'],b['torch_rng'])}
  assert all(audit[arm].values())
  used=[];ids=[]
  for u in range(700):
   rr=cached[P['arms'][arm][int(u>=300)]]['train'];idx=h.order(rr,17);batch=[rr[idx[(u*8+j)%len(rr)]] for j in range(8)];used+=batch
   if u>=300:ids.append([r['example_id'] for r in batch])
  exposure[arm]={'frequencies':f.frequencies(used),'stage2_order_sha':h.digest(ids),'total_targets':len(used)}
 assert exposure['direct']['stage2_order_sha']==exposure['curriculum']['stage2_order_sha']
 put(OUT/'audit.json',audit);put(OUT/'exposure.json',exposure)
 lines=['| Brazo | Update | Orden original | Inverso | Conjunta mixta | CE | Swaps estrictos |','|---|---:|---:|---:|---:|---:|---:|']
 for arm,r in comp.items():
  for u in ['300','700']:
   v=r['evaluations'][u];e=v['train'];sw=e['strict_swaps'];lines.append(f"| {arm} | {u} | {v['order-0']['accuracy']:.2%} | {v['order-1']['accuracy']:.2%} | {e['joint_accuracy']:.2%} | {e['ce']:.6f} | {sw['correct']}/{sw['n']} |")
 table='\n'.join(lines)
 dev=[]
 for arm,r in comp.items():
  for split in ['dev-layouts','dev-new-entity-pair']:
   e=r['evaluations']['700'][split];dev.append(f"- {arm}, {split}: respuesta {e['accuracy']:.2%}, conjunta {e['joint_accuracy']:.2%}, swaps {e['strict_swaps']['accuracy']:.2%}.")
 passed=comp['curriculum']['generalization_gate']
 decision=('El currículo supera las compuertas de generalización; corresponde confirmación preregistrada.' if passed else 'El currículo no supera las compuertas de generalización. No se habilitan semillas 29/43. Se cierra este currículo sin buscar variantes, aumentar capacidad ni retomar Hielo.')
 docs={
 'README.md':f"# Foreground Order Curriculum V1\n\nContraste CPU ejecutado: dos brazos, 700 updates, semilla 17.\n\n{table}\n\n{decision}\n\nReproducir en un worktree limpio con Python CPU existente: ejecutar primero `distribution-scaling/tests.py`, después `order-curriculum/run.py` y `order-curriculum/report.py`. Los scripts rechazan sobrescribir resultados. Protocolo congelado en PROTOCOL.json; checkpoints seguros `weights_only=True`.\n",
 'PROTOCOL.md':f"# Protocolo congelado\n\nVer PROTOCOL.json, escrito antes del entrenamiento. Directo C700 frente A300→C400. Arquitectura B histórica, 299520 parámetros asignados / 296160 entrenables, dos bloques width32; Hielo/Trapos OFF. CPU FP32, un thread, AdamW .003, betas .9/.95, wd .01, clip1, batch8. CE original de respuesta sobre 8192 IDs. Sin pérdida auxiliar. Checkpoint final fijo, sin selección por dev.\n\nEl optimizador no se recrea entre etapas. Snapshots completos 0/300/700 contienen parámetros, AdamW, RNG Python/Torch, cursor global, etapa siguiente, hashes de datos/tokenizer/código.\n\nCompuertas train: ocho respuestas, historias y swaps 100%, ambos órdenes. Generalización: conjunta y swaps ≥90% en ambos devs; sin dependencia exclusiva de posición. Solo entonces semillas29/43.\n",
 'DATA_CONTRACTS.md':"# Datos y contratos\n\nSe reutilizan literalmente A (4 respuestas) y C (8 respuestas / 4 historias) del factorial histórico. Nora/Iris, rojo/blanco según IDs originales; las dos consultas de cada historia están balanceadas, valores distintos. Targets solo fuera del forward. Cada minibatch C contiene exactamente los ocho ejemplos; A repite sus cuatro dos veces.\n\nAmbos brazos reciben 5600 respuestas. Directo: 2800 por orden. Currículo: 4000 orden original, 1600 inverso; esta diferencia de exposición es deliberada. Últimos 400 batches idénticos, comprobados por SHA en exposure.json. No igualdad de datos en los primeros300.\n\nLos devs heredados son layout verbal nuevo y par Nora/Mira (incluye una entidad nueva, no solo recombinación). No existe una reserva composicional interna adicional en el fixture exhaustivo de dos valores. No se abrió ningún conjunto sellado. Frecuencias y dataset completos en results.\n\nTests históricos: tres PASS (datos, causalidad/máscaras/target/AdamW/gradientes, reanudación). Nuevos contratos: estados reales AdamW300, continuación 300→304 idéntica con interrupción/restauración302 en ambos brazos; parámetros, optimizer, RNG y cursor exactos. Esto certifica la frontera, no una comparación independiente completa de 700 updates interrumpidos.\n",
 'CURRICULUM_RESULTS.md':f"# Resultados\n\n{table}\n\nResultados completos y logits8192 en results, curvas cada50 updates. A300 y C300 reproducen exactamente pesos, AdamW y RNG Torch de los checkpoints históricos correspondientes (audit.json). La diferencia posterior corresponde a trayectorias previas distintas bajo batches finales idénticos. Una semilla no establece superioridad poblacional.\n",
 'ORDER_GENERALIZATION.md':'# Generalización\n\n'+'\n'.join(dev)+"\n\nLa exactitud del fixture se informa separada de estos devs. El orden inverso es parte de train C, no generalización externa. Los layouts y el par nuevo no se usan para seleccionar checkpoints.\n",
 'COUNTERFACTUALS.md':f"# Contrafactuales\n\nCada swap requiere cuatro respuestas correctas: ambas consultas del relato original y ambas del relato con valores intercambiados. Dos pares estrictos en C, uno por orden. No basta cambiar arbitrariamente la predicción.\n\n{table}\n\nLogits completos, probabilidades y etiquetas/inputs originales guardados para cada panel en updates0/300/700. El campo same_answer_stories registra colapso entre consultas. No se declara éxito a partir de diferencias de atención o representaciones.\n",
 'DECISION.md':f"# Decisión\n\n{decision}\n\n{table}\n\nLa comparación no demuestra una causa exclusiva de dificultad ni incapacidad matemática del foreground. Distingue ajuste, generalización y trayectoria con presupuesto fijo. No se ejecutan nuevos currículos, hiperparámetros ni experimentos de memoria. La siguiente investigación debe tratar aprendizaje lingüístico más amplio y señal de entrenamiento, con protocolo separado; este resultado no justifica rediseñar Hielo.\n"
 }
 diag=[]
 for arm in comp:
  r=json.loads((OUT/f'{arm}.json').read_text());cur=r['curves'];diag.append(f"- {arm}: {r['seconds_updates']:.3f}s updates, {r['targets_s']:.2f} targets/s; clipping {r['clipping_frequency']:.2%}; RSS proceso acumulado {r['peak_process_rss_mib']:.1f} MiB. Norma preclip media etapas: {sum(v['preclip_norm'] for v in cur[:300])/300:.5f}, {sum(v['preclip_norm'] for v in cur[300:])/400:.5f}.")
 docs['OPTIMIZATION_DIAGNOSTICS.md']='# Optimización\n\n'+'\n'.join(diag)+'\n\nNormas por tensor por update y curvas por orden cada50 en los JSON de cada brazo. Se preserva AdamW300 sin reset. Tiempos sin profiler, CPU local; RSS high-water del proceso compartido, no memoria exclusiva de cada brazo. Capturas reales de outputs de ambos bloques en checkpoints0/300/700 permiten inspeccionar contextualización. No son evidencia de binding funcional ni atribución causal de interferencia de gradientes.\n'
 for name,body in docs.items():puttext=ROOT/name;assert not puttext.exists();puttext.write_text(body)
 assert not passed,'Confirmation required by protocol: do not claim closure yet'
if __name__=='__main__':main()
