"""Validate frozen provenance and balanced controls without sealed data access."""
import json,hashlib,torch
from pathlib import Path
R=Path(__file__).resolve().parent

def main():
 torch.set_num_threads(1);out=[]
 for p in sorted((R/'results').glob('*-trained.pt'))+sorted((R/'results').glob('*-initial.pt')):
  s=torch.load(p,weights_only=True);cp=Path(s['checkpoint']);assert hashlib.sha256(cp.read_bytes()).hexdigest()==s['checkpoint_sha256']
  for split,f in s['features'].items():
   for k,v in f.items():assert torch.isfinite(v).all(),(p.name,split,k)
  out.append({'features':p.name,'checkpoint_sha256':s['checkpoint_sha256'],'original_unchanged':True,'finite':True})
 assert len(out)==24
 controls={name:json.loads((R/'results/probes'/f'{name}.json').read_text()) for name in ['explicit','presence_only']}
 for r in controls['explicit']['results']:assert r['splits']['dev']['accuracy']==1.
 r=next(r for r in controls['presence_only']['results'] if r['task']=='value');assert r['splits']['dev']['accuracy']==.25
 (R/'results/validation.json').write_text(json.dumps({'artifacts':out,'explicit_control_all_tasks_dev':1.,'presence_value_dev':.25,'sealed_evaluation_accessed':False},indent=2)+'\n');print('PASS',len(out),'frozen feature artifacts and positive/negative controls')
if __name__=='__main__':main()
