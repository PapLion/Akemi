"""Conditional gate/state summaries, with paired regimes at fixed layout/value."""
import json,statistics,torch
from pathlib import Path
R=Path(__file__).resolve().parent

def main():
 torch.set_num_threads(1);rr=[json.loads(l) for l in (R/'data/dev.jsonl').read_text().splitlines()];n=torch.arange(len(rr));idx=torch.tensor([r['positions'][2]//2 for r in rr]);out=[]
 for p in sorted((R/'results').glob('*-trained.pt')):
  d=torch.load(p,weights_only=True);f=d['features']['dev'];gate=f['gates'][n,idx].mean(-1);state=f['states'][n,idx];before=f['states'][n,(idx-1).clamp_min(0)];delta=(state-before).norm(dim=-1)
  for regime,name in [(0,'propuesta rechazada'),(1,'actualizacion aceptada'),(2,'segunda actualizacion'),(3,'actualizacion otra entidad')]:
   use=torch.tensor([r['regime']==regime and r['present'] for r in rr]);out.append({'key':p.stem,'regime':regime,'description':name,'n':int(use.sum()),'gate_mean':float(gate[use].mean()),'gate_lt_05':float((gate[use]<.05).float().mean()),'state_delta_mean':float(delta[use].mean()),'gate_per_example':gate[use].tolist(),'known_limit':'chunk mean (historical: 8 token gates), slot/value averaged; no causal isolation of each gate dimension'})
 (R/'results/filter-summary.json').write_text(json.dumps(out,indent=2)+'\n')
 lines=['# Trapos: compuertas y actualización','','Regímenes balanceados por entidad/valores; mismo layout y posición. Presencia=1. El último fragmento que contiene la escritura también puede contener distractores. Para histórico se promedian ocho gates por token, para híbridos dimensiones/slots de la gate de chunk; no son escalas directamente equivalentes.','','|Estado|Evento|Gate media|Cambio Hielo|','|---|---|---:|---:|']
 for r in out:lines.append(f"|{r['key']}|{r['description']}|{r['gate_mean']:.5f}|{r['state_delta_mean']:.5f}|")
 lines+=['','Always/random son checkpoints entrenados previamente bajo esas políticas; no un cambio de inferencia. Random mantiene el presupuesto previo0.07153 de coeficiente aditivo esperado, no iguala borrado, norma o frecuencia de cambios. Se conserva la distinción entre política constante1 y gates soft. Todas las proyecciones se ejecutan: omisiones reales de cómputo=0.','','Una diferencia entre propuesta y actualización puede explicarse por operador/posición, no por saber qué VALOR debe conservarse. Pares de valor y de obsoleto en CAUSAL_INTERVENTIONS.md permiten contrastar efecto sobre estado/predicción, sin atribuirlo exclusivamente a la gate. No se ha intervenido cada gate de forma independiente ni entrenado otro filtro.']
 (R/'FILTER_DIAGNOSTICS.md').write_text('\n'.join(lines)+'\n');print('gate groups',len(out))
if __name__=='__main__':main()
