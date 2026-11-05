from diagnose import *
from dense import loss
import tempfile

def main():
 # New dense objective: certify the actual interrupted update trajectory too.
 rows=datasets()['4'][:8]
 def step(m,o):
  o.zero_grad(set_to_none=True);total,*_=loss(m,rows);total.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1);o.step()
 m=h.model('B');o=h.optimizer(m)
 for _ in range(3):step(m,o)
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'c.pt';snapshot(p,m,o,3,rows)
  for _ in range(5):step(m,o)
  rng=torch.get_rng_state();prng=random.getstate();n,q,c=restore(p,rows)
  for _ in range(5):step(n,q)
  assert h.state_sha(m)==h.state_sha(n) and torch.equal(rng,torch.get_rng_state()) and prng==random.getstate()
  for a,b in zip(o.state.values(),q.state.values()):
   for k in a:assert torch.equal(a[k],b[k])
 # Validate original final treatment checkpoint with external objective identity.
 contract=json.loads((OUT/'dense-checkpoint-contract.json').read_text());assert contract['checkpoint_sha']==h.file_sha(OUT/'dense-final.pt');assert contract['dense_protocol_sha']==h.file_sha(ROOT/'DENSE_PROTOCOL.json');assert contract['script_sha']==h.file_sha(ROOT/'dense.py')
 n,q,c=restore(OUT/'dense-final.pt',datasets()['4']);expected=json.loads((OUT/'dense-result.json').read_text())['train'];got=stats(n,datasets()['4']);assert json.loads(json.dumps(got))==expected
 put('final-checks',{'passed':True,'dense_exact_resume_8_vs3plus5':True,'dense_optimizer_rng_parameters_exact':True,'dense_final_restore_matches_recorded_predictions':True,'dense_objective_identity_checked':True})
 result={}
 for level,rows in datasets().items():
  m,_,_=restore(OUT/f'level-{level}-final.pt',rows);cf=datasets()['3'];y=h.logits(m,cf).detach();result[level]={'counterfactual_four':stats(m,cf,f'level-{level}-four-cf'),'logit_query_change_max':float((y[0]-y[1]).abs().max()),'logit_fact_change_max':float((y[0]-y[2]).abs().max()),'cf_four_is_training':level in ['3','4'],'train_all_correct':all(r['pred']==r['answer'] for r in [])}
  result[level].pop('train_all_correct')
  if level=='4':result[level]['functional']={k:h.evaluate(m,v)[0] for k,v in h.data().items()}
 put('functional-final',result);print('FINAL CHECKS PASS')
if __name__=='__main__':main()
