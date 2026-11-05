"""Regenerate nonsealed splits in memory and verify exact bytes; final untouched."""
import json,hashlib
from pathlib import Path
import panel
def main():
 root=Path(__file__).resolve().parent;manifest=json.loads((root/'data-v5/manifest.json').read_text());train=None;checked={}
 for split in ['train','iid','compositional','structural','both']:
  rows=panel.generate(split,4 if split=='train' else 2,train)
  if split=='train':train=rows
  data=''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows).encode();sha=hashlib.sha256(data).hexdigest()
  assert sha==manifest['splits'][split]['sha256']==hashlib.sha256((root/'data-v5'/f'{split}.jsonl').read_bytes()).hexdigest()
  checked[split]={'sha256':sha,'n':len(rows)}
 (root/'results/panel-reproduction.json').write_text(json.dumps({'nonsealed':checked,'sealed_opened':False},indent=2));print('PASS deterministic nonsealed regeneration')
if __name__=='__main__':main()
