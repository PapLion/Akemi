"""Freeze finished evidence; refuses an incomplete fixed training matrix."""
from pathlib import Path
import json,hashlib,datetime
from verify_artifacts import sha
from experiment import ARMS
R=Path(__file__).resolve().parent

def main():
 for stage in ['learning','learning-1000']:
  for arm in ARMS:
   for seed in [17,29,43]:
    p=R/f'results/{stage}/{arm}-{seed}.json';r=json.loads(p.read_text());assert len(r['updates'])==(100 if stage=='learning' else 1000)
    assert p.with_suffix('.pt').is_file(),str(p.with_suffix('.pt'))
 source=json.loads((R/'SOURCE_MANIFEST.json').read_text())
 for e in source['files']:assert sha(R/e['path'])==e['sha256'],e['path']
 files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.name=='ARTIFACT_MANIFEST.json' or p.name=='artifact-verification.log':continue
  files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
 (R/'ARTIFACT_MANIFEST.json').write_text(json.dumps({'version':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'scope':'local evidence; tensor checkpoints and CPU traces included even when excluded from Git'},indent=2))
 print('Frozen',len(files),'files;',sum(e['bytes'] for e in files),'bytes')
if __name__=='__main__':main()
