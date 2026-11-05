"""One additional write-policy control under the prior optional gate."""
import json,statistics,hashlib,datetime
from pathlib import Path
import torch
import panel,network,learn,diagnose
R=Path(__file__).resolve().parent
def main():
 arm=json.loads((R/'results/ablation-selection.json').read_text())['selected'];assert arm=='delta_fast','Only Delta random erase/control route certified here'
 differences=[]
 for seed in [17,29,43]:
  a=json.loads((R/f'results/extend/{arm}-normal-w16-{seed}.json').read_text());b=json.loads((R/f'results/ablations/{arm}-always-w16-{seed}.json').read_text());differences.append(a['metrics']['iid']['outside_accuracy']-b['metrics']['iid']['outside_accuracy'])
 allowed=statistics.mean(differences)>0 and sum(d>0 for d in differences)>=2
 cp=R/f'results/pilot/{arm}-normal-w16-17.pt';s=torch.load(cp,weights_only=True,map_location='cpu');m=network.build(arm,17,16);m.load_state_dict(s['model'],strict=True);m.eval();rr=diagnose.gate_rows()
 with torch.no_grad():_,tr=m(learn.batch(rr)[0],trace=True);budget=float(torch.cat([t['write'].flatten() for t in tr[:-1]]).mean())
 record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'arm':arm,'prior_optional_gate':allowed,'normal_minus_always_iid_outside':differences,'expected_additive_write_coefficient':budget,'calibration_checkpoint_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'calibration_ids':[r['id'] for r in rr],'interpretation':'Bernoulli per example/chunk broadcast across value features. Matches expected additive coefficient, not variance, retention/erase, state norm or skipped compute.','central_correction_failure_already_known':'All18primary models score0on genuine value-only correction twins; execute only this final targeted policy control, no additional architectures/recipe sweep.'}
 (R/'results/random-control-gate.json').write_text(json.dumps(record,indent=2))
 if not allowed:print('OMITTED random control: prior optional gate closed');return
 for seed in [17,29,43]:learn.train(arm,seed,'ablations',1000,16,'random',random_budget=budget)
if __name__=='__main__':main()
