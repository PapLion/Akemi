"""Sanitized post-destruction resource/billing receipt, no credentials."""
from pathlib import Path
import json,time,subprocess
R=Path(__file__).resolve().parent
def call(*args):return json.loads(subprocess.check_output(['vastai',*args,'--raw'],text=True))
instances=call('show','instances');volumes=call('show','volumes');u=call('show','user');p=json.loads((R/'results/rental-plan.json').read_text());receipt=json.loads((R/'results/rental-receipt.json').read_text());assert not any(r['id']==receipt['instance_id'] for r in instances)
r=dict(utc=time.time(),instance_absent=True,instances_remaining=[dict(id=i['id'],label=i.get('label')) for i in instances],volumes_remaining=volumes,credit_before=p['credit_before'],credit_after=u.get('credit'),observed_credit_decrease=p['credit_before']-u.get('credit',p['credit_before']),billing_pending_adjustments_possible=True,maximum_authorized_usd=5)
(R/'results/billing.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
# Current-instance charge receipt; never store entire account/user response.
try:
 invoices=call('show','invoices','--instance_label','neo-f2-gpu-training-v1','--only_charges')
 (R/'private/invoices.json').write_text(json.dumps(invoices,indent=2)+'\n')
except Exception as e:(R/'results/invoice-query.json').write_text(json.dumps(dict(error=type(e).__name__)))
