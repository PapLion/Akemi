"""Export only review code/reports/aggregates into the existing Akemi review branch.
Never copies source Git history, raw corpus, token arrays, credentials or checkpoints.
Does not push by itself; inspect/commit the export before pushing.
"""
from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parent;W=R.parent
source=Path('/PATH/TO/NEO_HOME/research/neo-publication-tools/export_reference.py').read_text()
source=source.replace("SRC=Path('/PATH/TO/NEO_HOME/research/neo-architecture-recovery/neo-corpus-recovery-f2-readiness-v1')",'SRC=Path('+repr(str(W))+')')
source=source.replace("'source_branch':'neo-corpus-recovery-f2-readiness-v1'","'source_branch':'neo-f2-gpu-training-v1'")
exec(compile(source,'existing_reference_exporter','exec'))
root=Path('/PATH/TO/NEO_HOME/research/akemi-neo-publication/research/NEO');p=root/'README.md';old=p.read_text();tail=old[old.index('## Cómo analizarlo con otro modelo'):]
s=json.loads((R/'results/F2-summary.json').read_text());bill=json.loads((R/'results/billing.json').read_text())
new=f'''# NEO — índice de investigación para revisión

Informes, código de referencia y métricas agregadas. Es una copia de consulta del trabajo local: corpus, pesos, tokens privados y conjuntos sellados quedan fuera.

## Estado más reciente: primer F2 GPU completado

- [Decisión del entrenamiento](architecture-recovery/neo-f2-gpu-training-v1/DECISION.md).
- [Resultados de entrenamiento](architecture-recovery/neo-f2-gpu-training-v1/TRAINING_RESULTS.md).
- [Comparación con Transformer](architecture-recovery/neo-f2-gpu-training-v1/BASELINE_COMPARISON.md).
- [Validación por idioma](architecture-recovery/neo-f2-gpu-training-v1/EVALUATION.md).
- [Generaciones completas, incluidas las repetitivas](architecture-recovery/neo-f2-gpu-training-v1/GENERATIONS.md).
- [Rendimiento y límites de medida](architecture-recovery/neo-f2-gpu-training-v1/GPU_PERFORMANCE.md).
- [Coste y cierre de Vast.ai](architecture-recovery/neo-f2-gpu-training-v1/COST_REPORT.md).
- [Configuración y alcance privado de los derechos](architecture-recovery/neo-f2-gpu-training-v1/TRAINING_CONFIG.md).

F2: {s['targets']:,} targets ES/EN; NLL dev {s['dev']['all']['nll']:.6f}; PPL {s['dev']['all']['ppl']:.3f}. Checkpoint final descargado y verificado localmente. GPU destruida y ausencia confirmada por API. Descenso de crédito observado USD {bill['observed_credit_decrease']:.6f}, sujeto a ajustes pendientes. Generaciones muy repetitivas; no demuestra capacidad conversacional. Hielo y Trapos OFF. Los límites documentales históricos del corpus se preservan; no hay aprobación general de publicación de pesos/corpus.

[Release histórico de datos](architecture-recovery/f2-corpus-release/DECISION.md): su clasificación CONDITIONAL no se sobrescribe. Esta ejecución documenta el uso privado concreto autorizado.

'''
p.write_text(new+tail)
mp=root/'PUBLICATION_MANIFEST.json';m=json.loads(mp.read_text())
for src in list((R/'results').glob('*-curve-100-updates.csv'))+[R/'results/learning-curves.svg']:
 dst=root/'architecture-recovery'/R.name/'results'/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy(src,dst)
 m['included_files'].append(dict(path=str(dst.relative_to(root)),source_path=str(src.relative_to(W)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
m['review_index_updated_for']='F2 GPU training; private checkpoints and corpus intentionally omitted'
mp.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print('Review export ready; no push executed')
