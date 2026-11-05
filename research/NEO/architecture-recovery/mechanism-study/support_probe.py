"""Post-audit diagnostic fixed +1 global semantic-value rotation. No training."""
import sys,json,copy,hashlib,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import make_model,batch,forward_answer
from tasks import load_tokenizer,oracle
from variants import build
from matched_head import build_matched
from capacity_control import build_control
from hybrid import build_hybrid
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'cryo-next-generation/results';torch.set_num_threads(1)
def panel():
 rows=[json.loads(s) for s in (OLD/'panel.jsonl').read_text().splitlines()];train=[r for r in rows if r['split']=='train'];out=[];tok=load_tokenizer()
 for r in rows:
  if r['split']!='dev':continue
  q=copy.deepcopy(r);q['semantics']=[(op,e,str((int(v)+1)%8)) for op,e,v in r['semantics']];lines=r['text'].splitlines(keepends=True);q['text']=''.join(line[:2]+str((int(line[2])+1)%8)+line[3:] for line in lines[:-1])+lines[-1];q['ids']=tok.encode(q['text']);q['answer']=oracle(q['semantics'],q['query'],q['entity']);q['label']=tok.encode(q['answer'])[0];q['id']='support-probe-'+r['id'];q['hash']=hashlib.sha256(q['text'].encode()).hexdigest()
  assert q['label']!=r['label'];assert any(t['entity']==q['entity'] and t['label']==q['label'] for t in train);assert q['hash'] not in {t['hash'] for t in train};assert len(q['ids'])==64;out.append(q)
 return out
@torch.no_grad()
def main():
 rows=panel();(R/'results/support-probe-panel.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));summ=[];pred=[]
 cases=[(arm,seed,OLD/f'learning-1000/{arm}-{seed}.pt',True) for arm in ['b0_local','b0_full','cryo_history','event','delta'] for seed in [17,29,43]]
 cases += [(p.stem.rsplit('-',1)[0],int(p.stem.rsplit('-',1)[1]),p,False) for p in (R/'results/ablations').glob('*.pt')]
 cases += [(p.stem.rsplit('-',1)[0],int(p.stem.rsplit('-',1)[1]),p,folder) for folder in ['matched','capacity','hybrid'] for p in (R/'results'/folder).glob('*.pt')]
 for arm,seed,p,old in cases:
  m=(make_model(arm,seed) if old is True else (build_matched(arm,seed) if old=='matched' else (build_control(seed) if old=='capacity' else (build_hybrid(arm,seed) if old=='hybrid' else build(arm,seed)))));m.load_state_dict(torch.load(p,weights_only=True)['model'],strict=True);m.eval();correct=0
  for start in range(0,len(rows),16):
   rr=rows[start:start+16];x,y=batch(rr);z,_=forward_answer(m,x);pp=z.argmax(-1);correct+=int((pp==y).sum())
   pred.extend({'arm':arm,'seed':seed,'old':old,'id':r['id'],'label':int(y[j]),'prediction':int(pp[j])} for j,r in enumerate(rr))
  summ.append({'arm':arm,'seed':seed,'original_model':old is True,'origin':('original' if old is True else (old or 'ablations')),'accuracy':correct/len(rows)})
 (R/'results/support-probe.json').write_text(json.dumps(summ,indent=2));(R/'results/support-probe-predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pred))
if __name__=='__main__':main()
