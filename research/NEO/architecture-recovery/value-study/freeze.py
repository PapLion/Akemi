"""Hash this derived study, never traverse old evaluations or source checkpoints."""
import json,hashlib,platform,sys,subprocess,argparse
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args();dst=R/'SHA256SUMS.json'
 if a.verify:
  data=json.loads(dst.read_text())
  for r in data['files']:
   f=R/r['path'];assert f.stat().st_size==r['bytes'] and sha(f)==r['sha256'],r['path']
  print('PASS',len(data['files']),'artifact hashes');return
 import torch
 env={'utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'torch':torch.__version__,'platform':platform.platform(),'device':'cpu','threads':1,'source_commit':'198b681','branch':subprocess.check_output(['git','branch','--show-current'],cwd=R.parent,text=True).strip(),'paid_services':False,'language_model_updates':0,'auxiliary_decoders_trained':True,'sealed_evaluations_read':False,'independent_human_review':False}
 (R/'results/environment.json').write_text(json.dumps(env,indent=2)+'\n');records=[]
 for f in sorted(R.rglob('*')):
  if not f.is_file() or f.name in ['SHA256SUMS.json','.run.lock'] or '__pycache__' in f.parts:continue
  records.append({'path':str(f.relative_to(R)),'bytes':f.stat().st_size,'sha256':sha(f)})
 dst.write_text(json.dumps({'utc':env['utc'],'files':records},indent=2)+'\n');print('Hashed',len(records),'derived artifacts')
if __name__=='__main__':main()
