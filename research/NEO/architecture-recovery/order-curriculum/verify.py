import runpy
from pathlib import Path
globals().update({k:v for k,v in runpy.run_path(str(Path(__file__).with_name('run.py')),run_name='curriculum_module').items() if not k.startswith('__')})
checks={};diagnostics={}
for arm in P['arms']:
 r=json.loads((OUT/f'{arm}.json').read_text())
 for u in [0,300,700]:
  m,o,c=load(OUT/f'{arm}-{u}.pt');assert c['cursor']==u
  assert all(int(v['step'])==u for v in o.state.values())
  actual=f.evaluate(m,f.datasets()['C']['train']);assert json.loads(json.dumps(actual))==r['evaluations'][str(u)]['train']
  checks[f'{arm}-{u}']='exact evaluation after reload; AdamW counter verified'
 for u in [300,700]:
  cap=torch.load(OUT/f'{arm}-{u}-representations.pt',weights_only=True);assert set(cap)=={'blocks.0','blocks.1'}
  diagnostics[f'{arm}-{u}']={k:{'shape':list(v.shape),'norm':float(v.norm()),'finite':bool(torch.isfinite(v).all())} for k,v in cap.items()}
 # Query-pair representations and order differences are descriptive, not causal claims.
 a=torch.load(OUT/f'{arm}-300-representations.pt',weights_only=True);b=torch.load(OUT/f'{arm}-700-representations.pt',weights_only=True)
 diagnostics[arm+'-change']={k:float((b[k]-a[k]).norm()/a[k].norm()) for k in a}
 for path in OUT.glob(f'{arm}-[037]*-train.pt'):
  z=torch.load(path,weights_only=True);yy=z['logits'];pr=yy.softmax(-1)
  pp=[{'id':v['example_id'],'order':v['order'],'entity':v['query_entity'],'values':v['values'],'target':v['answer'],'prediction':int(yy[i].argmax()),'valid_value_probabilities':pr[i,v['choices']].tolist(),'p_correct':float(pr[i,v['answer']])} for i,v in enumerate(z['rows'])]
  put(path.with_suffix('.predictions.json'),pp)
assert checks
put(OUT/'reload-verification.json',checks);put(OUT/'representation-diagnostics.json',diagnostics)
print(json.dumps(checks,indent=2))
