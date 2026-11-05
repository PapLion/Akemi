"""Read-only re-evaluation of the original experiment, no updates."""
import sys,json,torch,statistics,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiment import make_model,batch,forward_answer
from tasks import oracle,load_tokenizer
OUT=Path(__file__).parent/'results';OLD=ROOT.parent/'cryo-next-generation/results';torch.set_num_threads(1)
def main():
 rows=[json.loads(s) for s in (OLD/'panel.jsonl').read_text().splitlines()];train=[r for r in rows if r['split']=='train'];dev=[r for r in rows if r['split']=='dev'];report=[];detail=[]
 assert all(oracle(r['semantics'],r['query'],r['entity'])==r['answer'] for r in rows)
 assert not ({r['hash'] for r in train}&{r['hash'] for r in dev})
 assert not ({r['family'] for r in train}&{r['family'] for r in dev})
 for arm in ['b0_local','b0_full','cryo_history','event','delta']:
  for seed in [17,29,43]:
   ck=torch.load(OLD/f'learning-1000/{arm}-{seed}.pt',weights_only=True,map_location='cpu');m=make_model(arm,seed);m.load_state_dict(ck['model'],strict=True);m.eval();predictions=[]
   recorded={r['id']:r for s in (OLD/f'learning-1000/{arm}-{seed}-predictions.jsonl').read_text().splitlines() if (r:=json.loads(s))['stage']=='final'}
   with torch.no_grad():
    for i in range(0,len(dev),16):
     sub=dev[i:i+16];x,y=batch(sub);logits,_=forward_answer(m,x)
     # Answer shortcut equals actual last-position full forward, not a different head.
     full=m(x);full=full.logits if hasattr(full,'logits') else full
     torch.testing.assert_close(logits,full[:,-1],rtol=2e-4,atol=2e-5)
     pred=logits.argmax(-1);prob=logits.softmax(-1);rank=(logits>logits.gather(1,y[:,None])).sum(-1)+1
     for j,r in enumerate(sub):
      assert int(pred[j])==recorded[r['id']]['prediction'];p=int(pred[j]);label=int(y[j]);predictions.append(p==label)
      choices=[load_tokenizer().encode(str(v))[0] for v in range(8)];top=logits[j].topk(8)
      detail.append({'arm':arm,'seed':seed,'id':r['id'],'entity':r['entity'],'answer':r['answer'],'prediction':p,'label':label,'label_rank':int(rank[j]),'label_probability':float(prob[j,label]),'top8_ids':top.indices.tolist(),'top8_logits':top.values.tolist(),'predicted_valid_answer':p in choices,'predicted_pair_in_train':any(t['entity']==r['entity'] and t['label']==p for t in train)})
   part=detail[-len(dev):];report.append({'arm':arm,'seed':seed,'dev_accuracy':statistics.mean(predictions),'matches_saved_predictions':True,'answer_position_parity':True,'mean_label_rank':statistics.mean(x['label_rank'] for x in part),'valid_answer_prediction_rate':statistics.mean(x['predicted_valid_answer'] for x in part),'predicted_pair_train_support':statistics.mean(x['predicted_pair_in_train'] for x in part),'cursor':ck['cursor'],'update':ck['update'],'parameters':sum(p.numel() for p in m.parameters())});print(arm,seed,report[-1]['dev_accuracy'],flush=True)
 (OUT/'original-audit.json').write_text(json.dumps(report,indent=2));(OUT/'original-logits.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in detail))
 (OUT/'audit-contracts.json').write_text(json.dumps({'panel_sha256':hashlib.sha256((OLD/'panel.jsonl').read_bytes()).hexdigest(),'oracle_all_correct':True,'hash_family_disjoint':True,'same_target_indices':63,'target_visible_as_teacher_forced_answer':False,'objective':'single next-token answer, full8192vocab, not dense LM or free generation','known_confounders':['foreground attention local/full','RoPE vs sinusoidal','FFN4d vs2d','projection initialization std.02 vs.05','additional fast depth and output normalization','same targets but different FLOPs','held-out queried entity/value support','hypothesis deletion not identifiable']},indent=2))
if __name__=='__main__':main()
