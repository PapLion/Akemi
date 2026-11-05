"""Load downloaded final checkpoint on CPU; validate complete state and inference."""
from pathlib import Path
import sys,json,hashlib
import torch
R=Path(__file__).resolve().parent;B=R/'private/bundle';sys.path.insert(0,str(B));import f2
kind=sys.argv[1];out=R/'private/download/results'/kind;p=out/'final.pt';c=torch.load(p,map_location='cpu',weights_only=True)
assert all(k in c for k in ['model','optimizer','reader','update','config','torch_rng','python_rng','cuda_rng','dataset_manifest_sha','worker_sha'])
assert hashlib.sha256((B/'dataset.json').read_bytes()).hexdigest()==c['dataset_manifest_sha'];assert hashlib.sha256((B/'worker.py').read_bytes()).hexdigest()==c['worker_sha'];m=f2.make(kind);m.load_state_dict(c['model']);o=f2.opt(m);o.load_state_dict(c['optimizer'])
with torch.no_grad():y=m(torch.tensor([[257,65,66,67]]));assert torch.isfinite(y).all()
assert c['reader']['targets']==c['extra']['seen'];assert len(c['optimizer']['state'])==len(list(m.parameters()))
report=dict(status='PASS',kind=kind,checkpoint_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),parameters=sum(x.numel() for x in m.parameters()),targets=c['extra']['seen'],update=c['update'],optimizer_tensors=len(c['optimizer']['state']),rng_cpu=True,rng_cuda=len(c['cuda_rng']),reader=c['reader'],finite_inference=True,greedy_next_id=int(y[0,-1].argmax()))
(R/'results'/(kind+'-local-verification.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
