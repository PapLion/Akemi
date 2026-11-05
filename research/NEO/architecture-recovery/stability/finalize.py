import json,collections,hashlib,datetime,os,shutil
from pathlib import Path
import study as S
O=S.O;R=S.ROOT
balance={};confusions={}
for p in sorted(O.glob('[BC]-??-frequencies.json')):
 d=json.loads(p.read_text());byrole=collections.defaultdict(collections.Counter)
 for r in d['conditional_targets']:byrole[r['role']][r['value']]+=r['n']
 balance[p.stem]={'targets_by_role_value':{k:dict(v) for k,v in byrole.items()},'finite_random_sampling_not_exact_cell_balance':True}
for p in sorted(O.glob('[BC]-??-predictions.json')):
 dd=json.loads(p.read_text());fam={}
 for name,rr in dd.items():
  cc=collections.defaultdict(lambda:[[0]*4 for _ in range(4)])
  for r in rr:
   if 48<=r['prediction']<=51:cc[r['q']][r['label']-48][r['prediction']-48]+=1
   else:cc[r['q']+'-outside-vocab-response'][0][0]+=1
  fam[name]=dict(cc)
 confusions[p.stem]=fam
S.dump('finite-balance',balance);S.dump('confusions',confusions)
S.dump('eval-frequencies',{name:S.frequencies(rr) for name,rr in S.evaluation().items()})
# Independent source worktree is checked only for named original artifacts, never sealed files.
source=R.parent.parent/'cryo-addressable-consolidation-v1/addressable-consolidation'
historical={}
expected=dict((line.split('  ',1)[1],line.split('  ',1)[0]) for line in (source/'SHA256SUMS').read_text().splitlines())
for p in sorted(source.glob('results/[AB]-??.pt')):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 assert expected[str(p.relative_to(source))]==h.hexdigest()
 historical[str(p)]=h.hexdigest()
S.dump('historical-checkpoint-fingerprints',historical)
# Loss curves as a standalone SVG, no additional dependencies.
paths=[];colors=['#1f77b4','#d62728','#2ca02c','#9467bd','#8c564b','#17becf']
for color,p in zip(colors,sorted(O.glob('[BC]-??-curves.json'))):
 import math
 rr=json.loads(p.read_text());points=' '.join(f'{50+i*2:.1f},{40+(5-max(-5,min(5,math.log10(max(r["ce"],1e-6)))))*25:.1f}' for i,r in enumerate(rr))
 paths.append(f'<polyline fill="none" stroke="{color}" points="{points}"/><text x="665" y="{40+len(paths)*22}" fill="{color}">{p.stem}</text>')
(R/'loss-curves.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="350"><rect width="100%" height="100%" fill="white"/><text x="40" y="20">Response CE: log10 scale, updates 1–300; final checkpoint only</text>'+''.join(paths)+'</svg>')
mem={k:v.strip() for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k in ['MemTotal','MemAvailable']};usage=shutil.disk_usage(R)
S.dump('final-resources',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_disk_bytes':usage.free,'memory_snapshot':mem,'artifact_bytes':sum(p.stat().st_size for p in R.rglob('*') if p.is_file()),'main_training_updates':sum(json.loads(p.read_text())['updates'] for p in O.glob('[BC]-??-cost.json')),'main_arms':len(list(O.glob('[BC]-??-cost.json'))),'gpu':False,'money_spent':0})
(R/'.gitignore').write_text('__pycache__/\n')
print('Final resource and confusion artifacts saved')
