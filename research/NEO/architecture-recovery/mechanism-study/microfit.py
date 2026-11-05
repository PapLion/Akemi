"""Fixed, balanced tiny memorization diagnostic; no dev optimization."""
import sys,json,time,torch,random,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiment import make_model,optimizer,batch,forward_answer
R=Path(__file__).parent;torch.set_num_threads(1)
def main():
 assert (R/'results/original-audit.json').exists()
 rows=[json.loads(s) for s in (ROOT/'results/panel.jsonl').read_text().splitlines() if json.loads(s)['split']=='train'];small=[r for value in '01234567' for r in [x for x in rows if x['answer']==value][:2]];x,y=batch(small)
 (R/'results/microfit-panel.json').write_text(json.dumps(small,indent=2));results=[]
 for arm in ['b0_local','b0_full','event','delta','cryo_history']:
  m=make_model(arm,17);op=optimizer(m);log=[];start=time.monotonic()
  for step in range(200):
   m.train();op.zero_grad();z,_=forward_answer(m,x);loss=torch.nn.functional.cross_entropy(z,y);assert torch.isfinite(loss);loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);op.step()
   log.append({'update':step+1,'loss':float(loss.detach()),'pre_update_accuracy':float((z.argmax(-1)==y).float().mean())})
  m.eval()
  with torch.no_grad():z,_=forward_answer(m,x);acc=float((z.argmax(-1)==y).float().mean());nll=float(torch.nn.functional.cross_entropy(z,y))
  result={'arm':arm,'seed':17,'updates':200,'records':16,'targets_consumed':3200,'accuracy':acc,'nll':nll,'seconds':time.monotonic()-start,'logs':log,'prediction_ids':z.argmax(-1).tolist(),'label_ids':y.tolist()};results.append(result);(R/'results/microfit.json').write_text(json.dumps(results,indent=2));print(arm,acc,nll,flush=True)
if __name__=='__main__':main()
