import sys,json,collections,itertools,random
from pathlib import Path
import torch
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'association'))
import run
run.R=R

def fixture(distractors):
 rr=[]
 for ei,e in enumerate('ABCDE'):
  for v,pos in itertools.product(range(4),[0,2]):
   ops=[['~',e,'0'] for _ in range(15)];ops[pos]=['=',e,str((v+1)%4)];ops[pos+4]=['!',e,str(v)]
   if distractors:
    other='ABCDE'[(ei+1)%5];ops[pos+1]=['=',other,str((v+2)%4)];ops[pos+5]=['!',other,str((v+3)%4)]
   rr.append(run.data_panel.panel.make_record(ops,e,'repair','train'))
 return rr

def targets(rr):
 out=[]
 for r in rr:
  for j in range(8):
   stop=min(j*2+2,15)
   for e in sorted({e for op,e,v in r['ops'][j*2:stop] if op in '=!'}):
    val=run.data_panel.panel.oracle(r['ops'][:stop],e)
    if val!=4:out.append((e,val,j, 'initial' if not any(ee==e and op in '=!' for op,ee,v in r['ops'][:j*2]) else 'correction'))
 return out

def certify(rr):
 t=targets(rr);counts=collections.Counter(t)
 for e,j,kind in set((e,j,k) for e,v,j,k in t):assert len({counts[e,v,j,kind] for v in range(4)})==1
 m,d=run.setup();x=torch.tensor([r['ids'] for r in rr[:2]]);xx=x.clone();xx[:,48:]=120
 y,tr=m(x,trace=True);yy,tt=m(xx,trace=True);assert torch.equal(y[:,:48],yy[:,:48]);assert torch.equal(tr[5]['memory'],tt[5]['memory'])
 a,b,acc=run.loss(m,d,rr[:8]);b.backward();g={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert any('memory_head.value' in n and v>0 for n,v in g.items());assert all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
 return {'frequencies':[{'entity':e,'value':v,'chunk':j,'kind':k,'count':n} for (e,v,j,k),n in sorted(counts.items())],'gradient_norms':g,'future_invariance':True}

def main():
 for mode in ['simple','distractors']:
  rr=fixture(mode=='distractors');(R/'results'/f'{mode}-fixture.json').write_text(json.dumps(rr));cert=certify(rr);(R/'results'/f'{mode}-certification.json').write_text(json.dumps(cert,indent=2))
  m,d,logs=run.train(mode,rr,150,.1)
  with torch.no_grad():lm,aux,acc=run.loss(m,d,rr)
  result={'accuracy':acc,'aux_ce':float(aux),'pass':acc>=.9 and float(aux)<.5};(R/'results'/f'{mode}-gate.json').write_text(json.dumps(result));print(mode,result,flush=True)
  if not result['pass']:return
 # Main training requires remaining document/reset/resume certification; never silently approve.
 (R/'results/main-blocked.json').write_text(json.dumps({'reason':'Document/reset and exact resumed trajectory certification not yet executed; main arms prohibited.'}))
if __name__=='__main__':main()
