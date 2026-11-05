"""Fixed samples by hash, includes every arm/seed, no favorable selection."""
import json
from pathlib import Path
import panel
R=Path(__file__).resolve().parent
def main():
 rows=panel.load('iid');chosen=[min([r for r in rows if r['task']==task and r['outside_window']],key=lambda r:r['id']) for task in panel.TASKS];models=[]
 for p in sorted((R/'results/extend').glob('*.json')):
  meta=json.loads(p.read_text());base={r['id']:r for r in [json.loads(s) for s in p.with_name(p.stem+'-predictions.jsonl').read_text().splitlines()]};cf={(r['id'],r['kind']):r for r in [json.loads(s) for s in p.with_name(p.stem+'-counterfactuals.jsonl').read_text().splitlines()]};models.append((p.stem,base,cf))
 lines=['# Muestras fijas, sin selección favorable','','Un ejemplo IID fuera de ventana por tarea: menor hash de documento. Todas las semillas y brazos; no se eligen por resultados. Los64IDs completos son ASCII. Valores predichos0–4; otros IDs se muestran literalmente. Los registros completos restantes permanecen en JSONL.']
 def show(p):return str(p-48) if p in range(48,53) else f'ID{p}'
 for r in chosen:
  valid=panel.counterfactual(r,'valid');old=panel.counterfactual(r,'obsolete');lines+=['',f"## {r['task']} — {r['id'][:12]}",'','```text',''.join(chr(c) for c in r['ids']),'```',f"Oráculo: {r['answer']}; vigente modificado: {valid['answer']}; obsoleto modificado: {old['answer'] if old else 'no aplica'}.",'','|Modelo/semilla|Original|Obsoleto modificado|Vigente modificado|','|---|---:|---:|---:|']
  for name,base,cf in models:
   oo=cf.get((r['id'],'obsolete'));vv=cf[(r['id'],'valid')];lines.append(f"|{name}|{show(base[r['id']]['prediction'])}|{show(oo['changed_prediction']) if oo else '—'}|{show(vv['changed_prediction'])}|")
 (R/'SAMPLES.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
