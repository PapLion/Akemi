"""Fine-grained real trace around writes; no architecture changes."""
import json,torch
from pathlib import Path
import extract,data_panel
R=Path(__file__).resolve().parent
@torch.no_grad()
def main():
 torch.set_num_threads(1);rr=[r for r in data_panel.generate('dev') if r['present'] and r['regime']==2 and r['old']!=r['current']][:24];x=torch.tensor([r['ids'] for r in rr]);out=[]
 for arm in ['intact','event_fast','delta_fast']:
  m,_=extract.load_model(arm,17);y,tr=m(x,trace=True)
  for b,r in enumerate(rr):
   n=1 if arm=='intact' else 8;events=[]
   for j,t in enumerate(tr):
    end=j if n==1 else j*8+7;state=t['slow'] if n==1 else t['memory'];prev=t['previous'] if n==1 else (torch.zeros_like(state) if j==0 else tr[j-1]['memory']);gate=t['gate'] if n==1 else t['write'];events.append({'end_token':end,'memory_before':prev[b].flatten().tolist(),'memory_after':state[b].flatten().tolist(),'gate':gate[b].flatten().tolist()})
   out.append({'arm':arm,'seed':17,'id':r['id'],'positions':r['positions'],'events':events,'prediction':int(y[b,-1].argmax())-48})
 (R/'results/timelines.json').write_text(json.dumps(out)+'\n');print('timelines',len(out))
if __name__=='__main__':main()
