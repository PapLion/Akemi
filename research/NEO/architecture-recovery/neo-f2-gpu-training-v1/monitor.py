from pathlib import Path
import time,json,sys,shlex
import remote
R=Path(__file__).resolve().parent;kind=sys.argv[1];log=R/'results'/(kind+'-monitor.jsonl')
while True:
 try:
  cmd="cd /workspace/neo-f2; tail -1 results/"+kind+"/curve.jsonl 2>/dev/null; test ! -f results/"+kind+"/summary.json || echo FINISHED; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; true"
  output=remote.ssh(cmd);lines=output.strip().splitlines();row=next((json.loads(x) for x in lines if x.startswith('{')),{});row['utc']=time.time();row['telemetry']=lines[-1] if lines else '';row['complete']='FINISHED' in lines
  with log.open('a') as f:f.write(json.dumps(row)+'\n')
  print(kind,row.get('targets_seen'),row.get('targets_per_second'),row.get('loss'),row['telemetry'], 'DONE' if row['complete'] else '',flush=True)
  if row['complete']:break
  if time.time()>json.loads((R/'results/rental-plan.json').read_text())['deadline_epoch']-120:print('SAFETY DEADLINE',flush=True);break
 except Exception as e:print(type(e).__name__,str(e)[-150:],flush=True)
 time.sleep(30)
