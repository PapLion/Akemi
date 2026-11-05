"""Resume only saved-weight diagnostics after undefined reporting rate in original evaluator."""
import json,hashlib,copy
import torch
import runner_v11 as V
import evaluation_guard as G
R=V.R;O=V.O;D=V.D;T=V.T

def main():
 assert (O/'primary-gate.json').exists()
 aa=D.control();bb=D.treatment()
 # Verify evaluator equivalence wherever the former statistic is defined.
 m,d,*_=V.restore(O/'B-17.pt',bb)
 ev1,st1=T.evaluate(m,d,aa[:8]);ev2,st2=G.evaluate(m,d,aa[:8]);assert ev1==ev2 and torch.equal(st1,st2)
 # Reproduce failure on queried-entity corrections, then assert guarded semantics.
 cell=next(iter(D.grid().values()));failed=False
 try:T.evaluate(m,d,cell)
 except ZeroDivisionError:failed=True
 assert failed
 fixed,states=G.evaluate(m,d,cell);assert fixed['metrics']['all']['unjustified_changes_A'] is None
 V.dump('reporting-guard.json',dict(original_undefined_rate_reproduced=True,defined_case_exact_equivalence=True,undefined_statistic=None,scope='reporting only; no architecture, objective, labels or tolerance changes'))
 T.evaluate=G.evaluate
 # Confirmation branches if main failed before finishing them: never duplicate completed runs.
 primary=json.loads((O/'primary-gate.json').read_text())
 if primary['passed']:
  for seed in [29,43]:
   for arm,rr in [('A',aa),('B',bb)]:
    if not (O/f'{arm}-{seed}.pt').exists():V.train(arm,seed,rr)
    if not (O/f'{arm}-{seed}-metrics.json').exists():V.evaluate_arm(arm,seed,rr)
 cells=D.grid();grid={}
 for arm in ['A','B']:
  m,d,*_=V.restore(O/f'{arm}-17.pt',aa if arm=='A' else bb);m.eval();grid[arm]={};predictions=[]
  with torch.no_grad():
   for name,rr in cells.items():
    ev,states=T.evaluate(m,d,rr);grid[arm][name]=V.summarize(ev,rr)
    predictions.extend(dict(cell=name,**p) for p in ev['predictions'])
  V.dump(arm+'-position-grid-predictions.json',predictions)
 V.dump('position-grid.json',grid)
 spread=max(x['normal_accuracy'] for x in grid['B'].values())-min(x['normal_accuracy'] for x in grid['B'].values())
 allowed=spread>=.1 or json.loads((O/'B-17-metrics.json').read_text())['correction_layout']['normal_accuracy']<=.9
 V.dump('position-eligibility.json',dict(allowed=allowed,spread=spread,criterion=V.PROTOCOL['position_arm']))
 if allowed:
  if not (O/'P-17.pt').exists():V.train('P',17,bb)
  V.evaluate_arm('P',17,bb)
  held=[D.move(r,(6,7),11) for r in bb if r['kind']=='correct']
  for arm in ['B','P']:
   m,d,*_=V.restore(O/f'{arm}-17.pt',bb);ev,met=V.evaluate(m,d,held,arm+'-position-heldout');V.dump(arm+'-position-heldout-metrics.json',met)
 print('Saved-weight diagnostics complete; sealed set untouched',flush=True)
if __name__=='__main__':main()
