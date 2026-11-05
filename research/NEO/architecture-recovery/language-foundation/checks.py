import runpy
from pathlib import Path
globals().update({k:v for k,v in runpy.run_path(str(Path(__file__).with_name('pilot.py')),run_name='foundation_module').items() if not k.startswith('__')})
docs=json.loads((OUT/'data.json').read_text());ww=windows(docs,'train');results={}
for kind in P['arms']:
 m=make(kind);o=h.optimizer(m);before={n:p.detach().clone() for n,p in m.named_parameters() if p.requires_grad};r=update(m,o,kind,ww,0)
 for n,p in m.named_parameters():
  if p.requires_grad:assert p.grad is not None and torch.isfinite(p.grad).all() and p.grad.norm()>0 and not torch.equal(before[n],p)
 x,v=batch([{'ids':[257,10,11,258]},{'ids':[257,13]}]);y=logits(m,kind,x);mask=v[:,:-1]&v[:,1:];assert int(mask.sum())==4
 z=x.clone();z[~v]=999;assert torch.equal(logits(m,kind,z)[v],y[v])
 result={'all_active_parameters_have_finite_nonzero_gradient_and_update':True,'padding_no_effect_on_valid_outputs':True,'masked_target_count':4}
 results[kind]=result
put('additional-tests',results)
put('reproducibility',{'torch':torch.__version__,'python':sys.version,'platform':sys.platform,'threads':torch.get_num_threads(),'sources':{**h.sources(),'language-foundation/pilot.py':sha(__file__.replace('checks.py','pilot.py'))},'sampling':'shuffle fixed with local random.Random(17); cursor*2 modulo windows; no workers or NumPy RNG','data_sha':h.digest(docs),'batches_sha':h.digest([[r['id']+':'+str(r['offset']) for r in sequence(ww,u)] for u in range(128)]),'historical_commit':'eb2ee86','training_used_cuda':False,'paid_calls':0})
print('all parameter and padding tests PASS')
