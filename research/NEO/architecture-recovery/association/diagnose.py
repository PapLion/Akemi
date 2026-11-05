import json,torch
import run
m,d=run.setup();s=torch.load(run.R/'results/microfit.pt',weights_only=True);m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True)
rr=run.data_panel.generate('train');micro=[next(r for r in rr if r['entity']==e and r['present'] and r['current']==v and r['regime']==1) for e in 'ABCDE' for v in range(4)]
lm,a,acc=run.loss(m,d,micro);a.backward();g={n:{'norm':float(p.grad.norm()),'finite':bool(torch.isfinite(p.grad).all())} for n,p in m.named_parameters() if p.grad is not None};(run.R/'results/aux-gradients.json').write_text(json.dumps(g,indent=2));print('aux',float(a),acc,'finite',all(x['finite'] for x in g.values()))
