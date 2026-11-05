"""Change only an obsolete first fact; oracle's corrected final answer stays fixed."""
import sys,json,copy,torch,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import make_model,batch
from tasks import oracle,load_tokenizer
from gradient_audit import factory
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'cryo-next-generation/results';torch.set_num_threads(1)
@torch.no_grad()
def main():
 rows=[json.loads(s) for s in (OLD/'panel.jsonl').read_text().splitlines()];rows=[r for r in rows if r['split']=='dev' and r['task'] in ['correction','hypothesis']];changed=[];tok=load_tokenizer()
 for r in rows:
  q=copy.deepcopy(r);v=int(r['semantics'][0][2]);nv=str((v+1)%8)
  if nv==r['answer']:nv=str((v+2)%8)
  op,e,_=q['semantics'][0];q['semantics'][0]=(op,e,nv);q['text']=q['text'][:2]+nv+q['text'][3:];q['ids']=tok.encode(q['text']);assert oracle(q['semantics'],q['query'],q['entity'])==r['answer'];assert q['label']==r['label'];assert sum(a!=b for a,b in zip(q['ids'],r['ids']))==1;changed.append(q)
 (R/'results/stale-fact-panel.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in changed));out=[];details=[]
 cases=[('intact',seed,OLD/f'learning-1000/cryo_history-{seed}.pt') for seed in [17,29,43]]
 cases += [(p.stem.rsplit('-',1)[0],int(p.stem.rsplit('-',1)[1]),p) for folder in ['ablations','capacity','hybrid'] for p in (R/'results'/folder).glob('*.pt') if p.stem.rsplit('-',1)[0] in ['no_ice','capacity_transformer','event_fast','delta_fast']]
 for arm,seed,p in cases:
  m=make_model('cryo_history',seed) if arm=='intact' else factory(arm,seed);m.load_state_dict(torch.load(p,weights_only=True)['model'],strict=True);m.eval();records=[]
  for start in range(0,len(rows),16):
   rr=rows[start:start+16];cc=changed[start:start+16];x,y=batch(rr);xx,_=batch(cc);a=m(x)[:,-1].argmax(-1);b=m(xx)[:,-1].argmax(-1)
   for j,r in enumerate(rr):records.append({'arm':arm,'seed':seed,'id':r['id'],'task':r['task'],'prediction':int(a[j]),'counterfactual_prediction':int(b[j]),'label':int(y[j]),'prediction_changed':bool(a[j]!=b[j]),'correct':bool(a[j]==y[j]),'counterfactual_correct':bool(b[j]==y[j]),'follows_obsolete_value_in_both':bool(a[j]==tok.encode(r['semantics'][0][2])[0] and b[j]==tok.encode(cc[j]['semantics'][0][2])[0])})
  for t in ['correction','hypothesis']:
   sub=[r for r in records if r['task']==t];out.append({'arm':arm,'seed':seed,'task':t,**{key:statistics.mean(r[key] for r in sub) for key in ['prediction_changed','correct','counterfactual_correct','follows_obsolete_value_in_both']}})
  details+=records
 (R/'results/stale-fact-probe.json').write_text(json.dumps(out,indent=2));(R/'results/stale-fact-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in details))
if __name__=='__main__':main()
