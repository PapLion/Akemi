"""Read-only manifest verification, including locally retained .pt artifacts."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
rows=(R/'SHA256SUMS').read_text().splitlines()
for row in rows:
 sha,name=row.split('  ',1);assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
assert json.loads((R/'results/final-integrity.json').read_text())['passed']
assert not json.loads((R/'results/gate-17.json').read_text())['passed']
assert not list((R/'results').glob('*-29.pt')) and not list((R/'results').glob('*-43.pt'))
print(f'{len(rows)} SHA256 verified; pilot FAIL preserved, no confirmations.')
