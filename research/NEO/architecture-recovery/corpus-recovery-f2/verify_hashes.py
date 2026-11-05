from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
for r in json.loads((root/'SHA256SUMS.json').read_text()):
 p=root/r['path'];assert p.stat().st_size==r['bytes'],str(p)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 assert h.hexdigest()==r['sha256'],str(p)
print('All recorded local artifact SHA-256 verified')
