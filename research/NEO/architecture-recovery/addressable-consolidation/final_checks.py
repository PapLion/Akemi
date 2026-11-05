"""Post-run integrity; does not evaluate the sealed confirmation family."""
import json,hashlib,collections,statistics
import torch
import torch.nn.functional as F
import runner_v11 as V
O=V.O;R=V.R;D=V.D;A=V.A

def verify_manifest(root):
 n=0
 for line in (root/'SHA256SUMS').read_text().splitlines():
  expected,name=line.split('  ',1);assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name;n+=1
 return n

def main():
 immutable=R.parent.parent/'cryo-addressable-memory-v1/addressable';n=verify_manifest(immutable)
 freeze=json.loads((O/'FREEZE.json').read_text())
 for rel,expected in freeze['files'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==expected,rel
 arch=hashlib.sha256((R.parent/'addressable/address_model.py').read_bytes()).hexdigest();assert arch==hashlib.sha256((immutable/'address_model.py').read_bytes()).hexdigest()
 reports={};exposures={};grads={};geometry={};source={}
 for seed in [17,29,43]:
  available=all((O/f'{arm}-{seed}.pt').exists() for arm in ['A','B'])
  if not available:continue
  aa=torch.load(O/f'A-{seed}-initial.pt',weights_only=True);bb=torch.load(O/f'B-{seed}-initial.pt',weights_only=True)
  assert A.I.equal(aa['model'],bb['model']) and A.I.equal(aa['decoder'],bb['decoder']) and A.I.equal(aa['optimizer'],bb['optimizer'])
  la=json.loads((O/f'A-{seed}-curve.json').read_text());lb=json.loads((O/f'B-{seed}-curve.json').read_text());assert [r['indices'] for r in la]==[r['indices'] for r in lb]
  reports[str(seed)]={arm:json.loads((O/f'{arm}-{seed}-metrics.json').read_text()) for arm in ['A','B']}
  for arm,logs in [('A',la),('B',lb)]:
   ctr=collections.Counter();ans=collections.Counter();affected=collections.Counter()
   for row in logs:
    for e in row['exposures']:
     ctr[e['kind']]+=1;ans[e['answer']]+=1
     if e['kind']=='correct':affected[e['affected']]+=1
   exposures[f'{arm}-{seed}']=dict(records=sum(ctr.values()),kinds=dict(ctr),answers=dict(ans),corrected_entities=dict(affected),answer_targets=2400,initial_aux_targets=4800,accepted_writes=2*2400+ctr['correct'])
   for key in ['core.address.weight','core.event_value.weight','core.address_out.weight']:
    vv=[r['gradients'].get(key,0.) for r in logs];grads[f'{arm}-{seed}:{key}']=dict(min=min(vv),max=max(vv),nonzero=sum(v>0 for v in vv),steps=len(vv))
   m,d,*_=V.restore(O/f'{arm}-{seed}.pt',D.control() if arm=='A' else D.treatment())
   with torch.no_grad():
    keys=F.normalize(m.core.address(m.core.emb(torch.tensor([ord(e) for e in 'ABCDE']))),dim=-1);gram=keys@keys.T;off=gram[~torch.eye(5,dtype=torch.bool)]
   geometry[f'{arm}-{seed}']=dict(gram=gram.tolist(),mean_abs_off_diagonal=float(off.abs().mean()),max_abs_off_diagonal=float(off.abs().max()))
  cp=R.parent.parent/f'cryo-selective-memory-study/selective-memory/results/extend/delta_fast-normal-w16-{seed}.pt';source[str(seed)]=dict(path=str(cp),sha256=hashlib.sha256(cp.read_bytes()).hexdigest())
 # Hash sealed bytes only, no parsing or model evaluation.
 sealed=R/'confirmatory/SEALED.jsonl';manifest=json.loads((O/'sealed-manifest.json').read_text());assert hashlib.sha256(sealed.read_bytes()).hexdigest()==manifest['sha256']
 V.dump('final-integrity.json',dict(previous_artifacts_verified=n,architecture_unchanged=True,frozen_code_unchanged=True,paired_initializations_and_orders_exact=True,seeds=list(reports),sealed_sha_unchanged=True,sealed_model_evaluations=0,warmstart_sources=source))
 V.dump('actual-exposure.json',exposures);V.dump('gradient-summary.json',grads);V.dump('key-geometry.json',geometry)
 # Small-seed descriptive paired differences, not population significance.
 stats={}
 for family in ['formation','novel_pairs','correction_fixed','correction_layout','correction_alternate','correction_distractor']:
  aa=[v['A'][family]['normal_accuracy'] for v in reports.values()];bb=[v['B'][family]['normal_accuracy'] for v in reports.values()];diff=[b-a for a,b in zip(aa,bb)]
  stats[family]=dict(A=aa,B=bb,paired_difference=diff,mean_difference=statistics.mean(diff),min_difference=min(diff),max_difference=max(diff),seeds=len(aa),interpretation='descriptive only; shared task generator and small seed count')
 V.dump('paired-summary.json',stats)
 print('Immutable history, frozen architecture, paired RNG orders and sealed hash PASS')
if __name__=='__main__':main()
