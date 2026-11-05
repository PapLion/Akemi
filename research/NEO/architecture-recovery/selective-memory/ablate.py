"""Bounded, pilot-selected always-write training. Not an inference ablation."""
import json,statistics
from pathlib import Path
import learn
R=Path(__file__).resolve().parent
def main():
 selection=json.loads((R/'results/ablation-selection.json').read_text());arm=selection['selected'];diag=json.loads((R/'results/extend-diagnostics.json').read_text());assert len(diag)==18
 selected=[r for r in diag if r['config']['arm']==arm and r['config']['window']==16];assert len(selected)==3
 evidence=[]
 for r in selected:
  seed=int(Path(r['checkpoint']).stem.rsplit('-',1)[1]);base=json.loads((R/'results/extend'/f'{arm}-normal-w16-{seed}.json').read_text());control=json.loads((R/'results/extend'/f'no_ice-normal-w16-{seed}.json').read_text());reset=r['inference_interventions']['reset/outside']
  evidence.append({'seed':seed,'iid_outside_difference_vs_no_ice':base['metrics']['iid']['outside_accuracy']-control['metrics']['iid']['outside_accuracy'],'valid_counterfactual_both_correct':r['counterfactual_groups']['valid/outside/all']['both_correct'],'reset_accuracy_drop':reset['base_accuracy']-reset['accuracy']})
 # Operational prioritization, written before final diagnostics, not a test of
 # population superiority nor certification of learned selective filtering.
 allowed=statistics.mean(e['iid_outside_difference_vs_no_ice'] for e in evidence)>0 and all(e['valid_counterfactual_both_correct']>0 for e in evidence) and sum(e['reset_accuracy_drop']>0 for e in evidence)>=2
 (R/'results/ablation-execution-gate.json').write_text(json.dumps({'selected':arm,'evidence':evidence,'execute_always_write':allowed,'interpretation':'Exploratory prioritization of a causal control, not architecture selection or a preregistered superiority test.'},indent=2))
 if not allowed:print('OMITTED always-write: no sufficiently consistent functional-memory signal under operational gate');return
 for seed in [17,29,43]:learn.train(arm,seed,'ablations',1000,16,'always')
if __name__=='__main__':main()
