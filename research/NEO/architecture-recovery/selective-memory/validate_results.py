"""Verify final artifacts without opening any sealed file."""
import json,hashlib,math,collections
from pathlib import Path
import torch
import panel,network
R=Path(__file__).resolve().parent
def main():
 expected={(a,w,s) for s in [17,29,43] for a,w in [(a,16) for a in network.ARMS]+[('transformer',0)]}
 rows=[];orders={};datahash=hashlib.sha256(json.dumps(panel.load('train'),sort_keys=True).encode()).hexdigest()
 for p in sorted((R/'results/extend').glob('*.pt')):
  s=torch.load(p,weights_only=True,map_location='cpu');cfg=s['config'];seed=int(p.stem.rsplit('-',1)[1]);key=(cfg['arm'],cfg['window'],seed);assert key in expected;expected.remove(key)
  assert s['step']==1000 and s['cursor']==8000 and s['dataset_sha256']==datahash
  assert len(s['updates'])==1000 and [u['step'] for u in s['updates']]==list(range(1,1001))
  assert all(math.isfinite(u['loss']) and math.isfinite(u['gradient_norm']) for u in s['updates'])
  order=[u['indices'] for u in s['updates']]
  if seed in orders:assert order==orders[seed]
  else:orders[seed]=order
  m=network.build(cfg['arm'],seed,cfg['window'],cfg['mode']);m.load_state_dict(s['model'],strict=True);o=network.optimizer(m);o.load_state_dict(s['optimizer'])
  params=[p for p in m.parameters() if p.requires_grad];assert len(o.state)==len(params)
  assert all(torch.isfinite(t).all() for t in s['model'].values())
  assert all(int(v['step'])==1000 for v in o.state.values())
  assert all(torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in o.state.values())
  meta=json.loads(p.with_suffix('.json').read_text());assert meta['step']==1000 and meta['dataset_sha256']==datahash
  predictions=[json.loads(l) for l in p.with_name(p.stem+'-predictions.jsonl').read_text().splitlines()]
  assert len(predictions)==1280 and len({r['id'] for r in predictions})==1280
  allgrad=[t for cut in meta['gradients'] for t in cut['tensors']];assert all(t['finite'] for t in allgrad)
  rows.append({'checkpoint':p.name,'updates':s['step'],'examples':s['cursor'],'optimizer_tensors':len(o.state),'finite':True,'strict_load':True,'zero_grad_snapshots':sum(t['norm']==0 for t in allgrad),'order_sha256':hashlib.sha256(json.dumps(order).encode()).hexdigest()})
 assert not expected,expected
 exposure={}
 for seed,order in orders.items():
  counts=collections.Counter(i for batch in order for i in batch)
  exposure[seed]={'examples':sum(counts.values()),'unique_train_programs':len(counts),'minimum_exposures':min(counts.values()),'maximum_exposures':max(counts.values()),'counts_by_train_index':dict(counts)}
 (R/'results/artifact-validation.json').write_text(json.dumps({'validated':rows,'exposure_by_seed':exposure,'dataset_serialization_sha256':datahash,'sealed_read':False},indent=2))
 print('PASS',len(rows),'trajectories; matched sample orders; finite states; strict reload')
if __name__=='__main__':main()
