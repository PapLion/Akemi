import copy,json,torch
import repair
from repair import run,R
rr=repair.fixture(True)
def setup():
 m,d=run.setup();o=torch.optim.AdamW([p for p in list(m.parameters())+list(d.parameters()) if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False);return m,d,o
def step(m,d,o):
 o.zero_grad();a,b,c=run.loss(m,d,rr[:8]);(a+.1*b).backward();torch.nn.utils.clip_grad_norm_(list(m.parameters())+list(d.parameters()),1);o.step()
m,d,o=setup();step(m,d,o);step(m,d,o);s=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict()));step(m,d,o)
n,e,p=setup();n.load_state_dict(s[0],strict=True);e.load_state_dict(s[1],strict=True);p.load_state_dict(s[2]);step(n,e,p)
assert all(torch.equal(v,n.state_dict()[k]) for k,v in m.state_dict().items());assert all(torch.equal(v,e.state_dict()[k]) for k,v in d.state_dict().items())
x=torch.tensor([r['ids'] for r in rr[:2]])
with torch.no_grad():
 a=m(x);b=m(x.flip(0)).flip(0);assert torch.allclose(a,b,atol=1e-6,rtol=1e-5)
 joined=torch.cat([x[:1],x[1:]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:])],1);out=m(joined,doc=doc);assert torch.allclose(out[:,64:],a[1:],atol=1e-5,rtol=1e-5)
params=[v for v in list(m.parameters())+list(d.parameters()) if v.requires_grad];assert len({id(v) for g in o.param_groups for v in g['params']})==len(params)
(R/'results/contracts.json').write_text(json.dumps({'resume_three_updates_exact':True,'batch_independence':True,'document_reset':True,'optimizer_unique_coverage':True,'scope':'CPU FP32, dropout0, deterministic fixed batches; no AMP/CUDA'}));print('PASS contracts')
