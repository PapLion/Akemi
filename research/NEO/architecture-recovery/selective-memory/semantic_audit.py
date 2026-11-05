"""Audit actual operations rather than infer semantics from task labels."""
import json
from pathlib import Path
import panel
R=Path(__file__).resolve().parent
def main():
 out={}
 for split in ['train','iid','compositional','structural','both']:
  rows=panel.load(split);tasks={}
  for task in ['replace','multiple','other','goal']:
   rr=[r for r in rows if r['task']==task];truechanges=0;otherchanges=0
   for r in rr:
    vals=[v for op,e,v in r['ops'] if e==r['entity'] and op in '=!'];truechanges+=len(set(vals))>1
    states={};changed=False
    for op,e,v in r['ops']:
     if op in '=!':
      if e!=r['entity'] and e in states and states[e]!=v:changed=True
      states[e]=v
     elif op=='-':states.pop(e,None)
    otherchanges+=changed
   tasks[task]={'n':len(rr),'distinct_accepted_target_values':truechanges,'has_changed_other_entity':otherchanges}
  out[split]=tasks
 (R/'results/semantic-operation-audit.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
