"""Inventory local evidence without opening any sealed final evaluation."""
import argparse,hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import torch
R=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def eligible(p):
 return p.is_file() and p.name!='sealed-final.jsonl' and '__pycache__' not in p.parts and not p.name.endswith('.tmp') and p.name!='SHA256SUMS.json'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');a=parser.parse_args();target=R/'SHA256SUMS.json'
 if a.verify:
  records=json.loads(target.read_text())['files']
  for row in records:
   p=R/row['path'];assert eligible(p) and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
  print('PASS SHA256',len(records),'non-sealed files');return
 files=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if eligible(p)]
 target.write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'sealed_files_opened':False,'files':files},indent=2)+'\n');print('Inventoried',len(files),'non-sealed files')
if __name__=='__main__':main()
