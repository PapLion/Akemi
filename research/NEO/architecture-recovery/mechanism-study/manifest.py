"""Hash all local evidence (including ignored derived weights) without following external data."""
import json,hashlib,datetime,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='ARTIFACT_MANIFEST.json':continue
 files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
x={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'parent':'78373cc','files':files,'bytes':sum(f['bytes'] for f in files)}
(R/'ARTIFACT_MANIFEST.json').write_text(json.dumps(x,indent=2));print(len(files),x['bytes'])
