"""Readable deterministic samples: first ID per task, every seed and main arm."""
from pathlib import Path
import json
from tasks import load_tokenizer,TASKS
R=Path(__file__).resolve().parent
def main():
 tok=load_tokenizer();panel=[json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines()];lines=['# Muestras deterministas, sin selección por acierto','','Primer ID dev por tarea, brazos principales, todas las semillas, último update1000. No es generación libre: predicción de un token de respuesta con vocabulario completo. Los cuatro dígitos finales de cada registro son distractores. El corpus y el resto de predicciones están enresults.','']
 for task in TASKS:
  r=sorted([x for x in panel if x['split']=='dev' and x['task']==task],key=lambda x:x['id'])[0];lines+=['## '+r['id'],'','```text',r['text'].rstrip(),'```','',f"Respuesta del oráculo: `{r['answer']}`. Entidad consultada: `{r['entity']}`.",'','| Brazo | Semilla | Predicción | ID | Correcta |','|---|---:|---|---:|---|']
  for arm in ['b0_local','b0_full','cryo_history','event','delta']:
   for seed in [17,29,43]:
    path=R/f'results/learning-1000/{arm}-{seed}-predictions.jsonl'
    if not path.exists():continue
    pred=next(x for line in path.read_text().splitlines() if (x:=json.loads(line))['id']==r['id'] and x['stage']=='final')
    try:value=repr(tok.decode([pred['prediction']]))
    except (ValueError,UnicodeError):value='<control o byte incompleto>'
    value=value.replace('|','/').replace('\n',' ');lines.append(f"| {arm} | {seed} | `{value}` | {pred['prediction']} | {pred['correct']} |")
  lines+=['']
 (R/'SAMPLES.md').write_text('\n'.join(lines).rstrip()+'\n')
if __name__=='__main__':main()
