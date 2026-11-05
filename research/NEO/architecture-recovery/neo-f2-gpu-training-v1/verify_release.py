"""Verify final downloaded artifacts and accounting; never rents or trains."""
from pathlib import Path
import json,hashlib,math,subprocess
R=Path(__file__).resolve().parent;O=R/'results';D=R/'private/download/results'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'billing.json');assert b['instance_absent'] and b['instances_remaining']==[] and b['volumes_remaining']==[];assert 0<=b['observed_credit_decrease']<5
assert load(O/'cleanup.json')['absent'];assert load(O/'cuda-preflight.json')['status']=='PASS'
summaries={k:load(D/k/'summary.json') for k in ['F2','Transformer'] if (D/k/'summary.json').exists()}
for kind,s in summaries.items():
 a=[json.loads(x) for x in (D/kind/'curve.jsonl').read_text().splitlines()]
 assert len(a)==s['updates'] and a[-1]['targets_seen']==s['targets']==4922444
 assert s['checkpoint_sha']==sha(D/kind/'final.pt')==load(O/(kind+'-local-verification.json'))['checkpoint_sha256']
 assert all(math.isfinite(r['loss']) and math.isfinite(r['gradient_norm']) for r in a)
 assert s['dev']['all']['targets']==212105 and s['dev']['es']['targets']==107333 and s['dev']['en']['targets']==104772
 assert abs(math.log(s['dev']['all']['ppl'])-s['dev']['all']['nll'])<1e-12
 assert len(load(D/kind/'generations.json'))==4
if 'Transformer' in summaries:
 assert summaries['F2']['dataset_sha']==summaries['Transformer']['dataset_sha']
 assert summaries['F2']['config']==summaries['Transformer']['config']
 a=load(O/'F2-local-verification.json')['reader'];c=load(O/'Transformer-local-verification.json')['reader'];assert a==c
for p,h in load(O/'artifact-hashes.json').items():assert sha(R/p)==h
for p,h in load(R/'SHA256SUMS.json').items():assert sha(R/p)==h
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).splitlines();assert all(x.startswith(R.name+'/') for x in changed)
report=dict(status='PASS',models=list(summaries),same_data_order_and_recipe='Transformer' in summaries,all_downloaded_artifact_hashes=True,finite_all_logged_losses_and_norms=True,exact_target_budget=True,dev_count_and_ppl=True,local_checkpoint_load_receipts=True,cleanup_and_credit_receipts=True,historical_tracked_files_unchanged=True)
(O/'final-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
