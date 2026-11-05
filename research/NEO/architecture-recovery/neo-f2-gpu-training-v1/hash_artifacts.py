"""Refresh SHA-256 receipts after final report/plot generation."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
for base,out in [(R/'private/download',R/'results/artifact-hashes.json'),(R,R/'SHA256SUMS.json')]:
 hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file() and p!=out and '__pycache__' not in p.parts and (base!=R or 'private' not in p.parts)}
 out.write_text(json.dumps(hashes,indent=2)+'\n')
print('SHA-256 receipts refreshed')
