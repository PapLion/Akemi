"""Verify local evidence using streaming SHA-256; no model/corpus mutation."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 m=json.loads((ROOT/'ARTIFACT_MANIFEST.json').read_text());errors=[]
 for entry in m['files']:
  p=ROOT/entry['path']
  if not p.exists() or p.stat().st_size!=entry['bytes'] or sha(p)!=entry['sha256']:errors.append(entry['path'])
 if errors:raise SystemExit('Mismatch: '+', '.join(errors))
 source=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
 for entry in source['files']:
  p=ROOT/entry['path'];assert sha(p)==entry['sha256'],str(p)
 print('Verified',len(m['files']),'local artifacts and',len(source['files']),'source/tokenizer hashes')
if __name__=='__main__':main()
