"""Add explicit timing, optimization and artifact locations from executed receipts."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;O=R/'results'
def load(name):return json.loads((O/name).read_text())
f=load('F2-summary.json');b=load('Transformer-summary.json');bill=load('billing.json');timing=load('lifecycle-timing.json');diag=load('runtime-diagnostics.json')
(R/'README.md').write_text(f'''# NEO — primer entrenamiento F2 en GPU

F2 y Transformer comparable completaron **{f['targets']:,} targets cada uno**, semilla 17, CPU de referencia y entrenamiento CUDA FP32 en una RTX 3090. Hielo y Trapos permanecieron OFF.

| Modelo | Parámetros | NLL dev | PPL dev | Targets/s de updates |
|---|---:|---:|---:|---:|
| F2 | {f['parameters']:,} | {f['dev']['all']['nll']:.6f} | {f['dev']['all']['ppl']:.3f} | {f['targets_per_second']:.2f} |
| Transformer | {b['parameters']:,} | {b['dev']['all']['nll']:.6f} | {b['dev']['all']['ppl']:.3f} | {b['targets_per_second']:.2f} |

El baseline obtuvo mejor validación y rendimiento en este único ensayo. Las generaciones F2 son muy repetitivas; completar el entrenamiento no demuestra competencia conversacional.

- [Decisión](DECISION.md), [validación por idioma](EVALUATION.md), [generaciones sin selección estética](GENERATIONS.md).
- [Configuración y uso privado de datos](TRAINING_CONFIG.md), [entorno y reparaciones operativas](GPU_ENVIRONMENT.md).
- [Rendimiento](GPU_PERFORMANCE.md), [comparación](BASELINE_COMPARISON.md), [coste y cierre](COST_REPORT.md).
- [Curvas](results/learning-curves.svg); CSV por grupos de 100 updates en results/. Curvas completas fuera de Git.

Checkpoints completos locales: `private/download/results/F2/final.pt` y `private/download/results/Transformer/final.pt`. Cada carpeta contiene también checkpoints periódicos, latest.pt, curvas y generaciones. Cargas CPU, inferencia y SHA-256 verificados. `results/artifact-hashes.json` conserva los hashes de todos los artefactos descargados; `SHA256SUMS.json`, los del código e informes.

GPU destruida y ausencia de instancias/volúmenes confirmada. Descenso de crédito observado: USD {bill['observed_credit_decrease']:.8f}; pueden existir ajustes pendientes. No se publican corpus ni pesos. La clasificación histórica CONDITIONAL se preserva; el uso privado específico y sus límites están documentados, sin aprobación general de redistribución.
''')
p=R/'GPU_PERFORMANCE.md';s=p.read_text();s+='\n## Diagnósticos observados de optimización\n\n| Modelo | Norma gradiente mediana | Máxima registrada | Updates con clipping | RAM pico del proceso reportado MiB |\n|---|---:|---:|---:|---:|\n'
for kind,x in [('F2',f),('Transformer',b)]:
 d=diag[kind];s+=f"| {kind} | {d['gradient_norm_median']:.4f} | {d['gradient_norm_max']:.4f} | {d['clipping_fraction']:.2%} | {x['peak_rss_MiB']:.2f} |\n"
s+='\nLa RAM F2 es del proceso de finalización, no un pico recuperado del proceso original de entrenamiento. F2 alcanzó 530 MiB y baseline 528 MiB en muestras nvidia-smi; son muestras del dispositivo, no picos certificados del allocator. Las medias de utilización incluyen evaluaciones y pausas de exportación/reparación; no representan utilización sostenida de kernels. Los gradientes se comprobaron finitos en cada update. El clipping frecuente y la diferencia de normas motivan revisar la receta de forma aislada en un estudio posterior, pero no prueban por sí solos la causa de la diferencia de NLL. No se alteró la receta aquí.\n'
p.write_text(s)
p=R/'COST_REPORT.md';p.write_text(p.read_text()+f"\nIntervalo de alquiler hasta ausencia API: {timing['created_utc']} → {timing['destroyed_confirmed_utc']}; {timing['rental_seconds_until_absence']/60:.2f} minutos. El tiempo incluye arranque de imagen, preflight, dos entrenamientos, reparación de generación, exportación y destrucción. Ver results/lifecycle-timing.json.\n")
# Readability fixes only; never modifies numerical results or original evidence.
for p in R.glob('*.md'):
 s=p.read_text()
 for a,z in [('completo212.105targets,70artículos','completo: 212.105 targets, 70 artículos'),('sobre4,922,444targets','sobre 4.922.444 targets'),('HieloOFF/TraposOFF','Hielo OFF / Trapos OFF'),('NLL5.559083','NLL 5.559083'),('PPL259.585','PPL 259.585'),('máximo5M','máximo 5M'),('frente a5M','frente a 5M'),('son77.556targets','son 77.556 targets'),('cada1Mtargets','cada 1M targets'),('de100updates','de 100 updates'),('por grupos de100updates','por grupos de 100 updates'),('semilla17','semilla 17'),('batch2','batch 2'),('greedy,64tokens','greedy, 64 tokens'),('Greedy,64tokens','Greedy, 64 tokens'),('fue9,016434','fue 9,016434'),('de128','de 128')]:s=s.replace(a,z)
 p.write_text(s)
print('Reports finalized with observed diagnostics')
