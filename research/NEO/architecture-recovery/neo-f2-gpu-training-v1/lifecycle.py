"""One authorized rental, sanitized receipts, independent deadline destruction."""
from pathlib import Path
import subprocess,json,time,sys,os,hashlib
R=Path(__file__).resolve().parent;P=R/'private';RESULT=R/'results'
def cli(*args):
 p=subprocess.run(['vastai',*map(str,args),'--raw'],text=True,capture_output=True,timeout=60)
 if p.returncode:raise RuntimeError('Vast CLI failure: '+args[0]+' status '+str(p.returncode))
 try:return json.loads(p.stdout)
 except ValueError:raise RuntimeError('Vast CLI did not return JSON for '+args[0])
def ids():return cli('show','instances')
def cleanup(instance):
 for attempt in range(5):
  try:
   subprocess.run(['vastai','destroy','instance',str(instance),'--yes','--raw'],capture_output=True,timeout=50)
   rows=ids()
   if not any(r['id']==instance for r in rows):return dict(absent=True,attempts=attempt+1,utc=time.time())
  except Exception:pass
  time.sleep(5)
 return dict(absent=False,utc=time.time())
def watch():
 plan=json.loads((RESULT/'rental-plan.json').read_text());deadline=plan['deadline_epoch']
 while time.time()<deadline:
  if (P/'cleanup-complete').exists():return
  time.sleep(min(20,max(0,deadline-time.time())))
 receipt=RESULT/'rental-receipt.json'
 if receipt.exists():instance=json.loads(receipt.read_text())['instance_id'];report=cleanup(instance)
 else:
  matching=[r for r in ids() if r.get('label')==plan['label']];report={'reconciled':[]}
  for r in matching:report['reconciled'].append(cleanup(r['id']))
 (RESULT/'watchdog-result.json').write_text(json.dumps(report,indent=2)+'\n')
def rent():
 assert not (RESULT/'rental-plan.json').exists(),'Never create a second rental from this execution'
 assert ids()==[] and cli('show','volumes')==[]
 user=cli('show','user');credit=user.get('credit',0);assert credit>=5
 offers=cli('search','offers','gpu_name=RTX_3090 num_gpus=1 rentable=true rented=false reliability>0.98 disk_space>=20 cuda_vers>=12.6','--order','dph_total','--limit','5')
 offer=next(o for o in offers if o['dph_total']+20*o['storage_cost']/730<=.3 and max(o['inet_up_cost'],o['inet_down_cost'])<=.05)
 plan=dict(label='neo-f2-gpu-training-v1',offer_id=offer['id'],hourly_gpu_quote=offer['dph_total'],disk_GB=20,disk_hour_conservative=20*offer['storage_cost']/730,inet_up=offer['inet_up_cost'],inet_down=offer['inet_down_cost'],max_total_usd=5,operational_reserve_usd=2.6,credit_before=credit,created_epoch=time.time(),deadline_epoch=time.time()+7200,image='pytorch/pytorch@sha256:a77983eb7a3042ccf41a94da547a7f54a47fb70da15c36d67a8e8a329ebaa098',offer={k:offer.get(k) for k in ['id','gpu_name','reliability','verification','cuda_max_good']})
 (RESULT/'rental-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 log=(P/'watchdog.log').open('w');p=subprocess.Popen([sys.executable,__file__,'watch'],stdout=log,stderr=log,start_new_session=True);assert p.poll() is None
 response=cli('create','instance',offer['id'],'--disk','20','--image',plan['image'],'--ssh','--direct','--cancel-unavail','--label',plan['label'])
 instance=response.get('new_contract');assert instance and response.get('success'), 'Ambiguous create: inspect API, never retry create'
 (RESULT/'rental-receipt.json').write_text(json.dumps(dict(instance_id=instance,offer_id=offer['id'],created_epoch=time.time(),deadline_epoch=plan['deadline_epoch'],watchdog_pid=p.pid),indent=2)+'\n');print('RENTED',instance,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='watch':watch()
 elif sys.argv[1]=='rent':rent()
 elif sys.argv[1]=='cleanup':
  instance=json.loads((RESULT/'rental-receipt.json').read_text())['instance_id'];r=cleanup(instance);(RESULT/'cleanup.json').write_text(json.dumps(r,indent=2)+'\n');assert r['absent'];(P/'cleanup-complete').touch();print(r)
