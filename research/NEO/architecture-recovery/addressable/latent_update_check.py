import torch
import run_addressable as R
from analyze_addressable import correction_panel
A=R.A;O=R.O;m,d,*_=A.restore(O/'main.pt',R.C.data('same'));maxerr=0.;n=0
with torch.no_grad():
 for row in correction_panel('same'):
  _,tr=m(torch.tensor([row['ids']]),trace=True);t=tr[4];w=t['writes'][0]
  assert w['accepted'].all() and not t['writes'][1]['accepted'].any()
  maxerr=max(maxerr,float(((w['key'][:,None]@t['memory'])[:,0]-w['value']).abs().max()));n+=1
R.dump('latent-update-check.json',dict(n=n,max_latent_value_reread_error=maxerr,scope='Retrieves the written latent vector, not proof it encodes the correct symbolic value.'))
print(n,maxerr)
