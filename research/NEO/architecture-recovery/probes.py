"""Fixed all-dev counterfactual and state interventions, no fitting."""
from pathlib import Path
import json,copy,torch,hashlib
import torch.nn.functional as F
from experiment import make_model,batch,forward_answer,ARMS
from tasks import load_tokenizer,oracle
R=Path(__file__).resolve().parent
torch.set_num_threads(1)
def counterfactual(r):
 rr=copy.deepcopy(r);ops={'?':['!','='],'>':['+'],'<':['$'],'/':['^']}[r['query']]
 at=max(i for i,(op,e,v) in enumerate(rr['semantics']) if e==r['entity'] and op in ops)
 value=str((int(r['answer'])+1)%8);rr['semantics'][at][2]=value
 lines=rr['text'].splitlines(keepends=True);lines[at]=lines[at][:2]+value+lines[at][3:];rr['text']=''.join(lines);rr['answer']=oracle(rr['semantics'],rr['query'],rr['entity']);assert rr['answer']==value
 tok=load_tokenizer();rr['label']=tok.encode(value)[0];rr['ids']=tok.encode(rr['text']);rr['id']+='-cf';rr['hash']=hashlib.sha256(rr['text'].encode()).hexdigest();assert len(rr['ids'])==64;return rr
@torch.no_grad()
def predict(m,rows,hard=False):
 preds=[];stats={'executed':0,'eligible':0}
 for i in range(0,len(rows),16):
  x,y=batch(rows[i:i+16])
  if hard:o=m(x,hard=True,answer_positions=torch.full((len(x),),63));logits=o.logits
  else:logits,o=forward_answer(m,x)
  pred=logits.argmax(-1)
  for j in range(len(x)):preds.append({'id':rows[i+j]['id'],'prediction':int(pred[j]),'label':int(y[j]),'correct':bool(pred[j]==y[j]),'nll':float(F.cross_entropy(logits[j:j+1],y[j:j+1]))})
  if o:stats['executed']+=o.stats.get('candidate_slots_executed',0);stats['eligible']+=o.stats.get('candidate_slots_eligible',0)
 return preds,stats
def main(stage="learning", output=""):
 source=R/"results"/stage;dest=R/"results"/output if output else R/"results";dest.mkdir(exist_ok=True)
 dev=[json.loads(s) for s in (R/'results/panel.jsonl').read_text().splitlines() if json.loads(s)['split']=='dev'];cf=[counterfactual(r) for r in dev]
 (dest/'counterfactual-panel.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in cf));summary=[];detail=[];interventions=[]
 for seed in [17,29,43]:
  for arm in ARMS:
   p=source/f'{arm}-{seed}.pt'
   if not p.exists():continue
   state=torch.load(p,map_location='cpu',weights_only=True);m=make_model(arm,seed);m.load_state_dict(state['model'],strict=True);m.eval()
   original=[json.loads(s) for s in (p.parent/f'{arm}-{seed}-predictions.jsonl').read_text().splitlines() if json.loads(s)['stage']=='final'];new,_=predict(m,cf)
   assert [x['id']+'-cf' for x in original]==[x['id'] for x in new]
   pairs=[{'id':a['id'],'arm':arm,'seed':seed,'original_prediction':a['prediction'],'new_prediction':b['prediction'],'original_label':a['label'],'new_label':b['label'],'both_correct':a['correct'] and b['correct'],'changed':a['prediction']!=b['prediction']} for a,b in zip(original,new)];detail.extend(pairs)
   summary.append({'arm':arm,'seed':seed,'pairs':len(pairs),'both_correct':sum(x['both_correct'] for x in pairs)/len(pairs),'prediction_changed':sum(x['changed'] for x in pairs)/len(pairs),'cf_accuracy':sum(x['correct'] for x in new)/len(new)})
   if arm=='event':
    for mode in ['soft','hard_0.5','no_persist_inference']:
     m.cfg.ablation='no_persist' if mode=='no_persist_inference' else 'none';m.cfg.hard_threshold=.5;pp,stats=predict(m,dev,hard=mode=='hard_0.5')
     interventions.append({'seed':seed,'mode':mode,'accuracy':sum(x['correct'] for x in pp)/len(pp),'nll':sum(x['nll'] for x in pp)/len(pp),'stats':stats,'predictions_different_from_soft':sum(x['prediction']!=y['prediction'] for x,y in zip(pp,original))/len(pp)})
 (dest/'counterfactual-results.json').write_text(json.dumps(summary,indent=2));(dest/'counterfactual-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in detail));(dest/'state-interventions.json').write_text(json.dumps(interventions,indent=2));print('Counterfactual arms/seeds',len(summary),'interventions',len(interventions))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--stage',default='learning');p.add_argument('--output',default='');a=p.parse_args();main(a.stage,a.output)
