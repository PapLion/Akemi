from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
items=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name in ['SHA256SUMS.json','SHA256SUMS.json.tmp'] or p.suffix in ['-journal','-wal','-shm']:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 items.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':h.hexdigest(),'local_only':p.suffix in ['.pt','.sqlite']})
(ROOT/'SHA256SUMS.json').write_text(json.dumps(items,indent=2)+'\n');print(len(items),'artifacts hashed; local databases/checkpoints excluded Git')
