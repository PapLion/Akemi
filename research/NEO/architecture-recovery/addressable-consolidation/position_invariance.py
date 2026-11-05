"""Weight-frozen controlled shifts. All queried facts stay outside visible window."""
import torch
import runner_v11 as V
D=V.D;O=V.O

def main():
 report={};rr=[r for r in D.treatment() if r['kind']=='correct' and r['variant']==1][::4]
 for arm in ['A','B','P']:
  if not (O/f'{arm}-17.pt').exists():continue
  m,d,*_=V.restore(O/f'{arm}-17.pt',D.control() if arm=='A' else D.treatment());m.eval();out={}
  for name,initial,corr in [('reference',(0,1),4),('shift16IDs',(4,5),8),('shift8IDs',(2,3),6)]:
   rows=[D.move(r,initial,corr) for r in rr]
   with torch.no_grad():y,tr=m(torch.tensor([r['ids'] for r in rows]),trace=True)
   out[name]=dict(logits=y[:,-1].clone(),memory=tr[-1]['memory'].clone(),prediction=y[:,-1].argmax(-1).clone())
  base=out['reference'];report[arm]={}
  for name,values in out.items():
   report[arm][name]=dict(logits_max_abs=float((values['logits']-base['logits']).abs().max()),memory_max_abs=float((values['memory']-base['memory']).abs().max()),prediction_change=float((values['prediction']!=base['prediction']).float().mean()),n=len(rr))
  torch.save(out,O/f'{arm}-shift-tensors.pt')
 V.dump('position-shift-invariance.json',report);print(report)
if __name__=='__main__':main()
