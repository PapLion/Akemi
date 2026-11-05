"""Complete the authorized single-rental experiment; always destroy on exit."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback,shlex
import remote,lifecycle
R=Path(__file__).resolve().parent
PYTHON='/PATH/TO/NEO_HOME/evaluations/cryo-legacy-viability/.venv/bin/python'
def verify(kind):
 env=os.environ|{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
 p=subprocess.run([PYTHON,str(R/'verify_local.py'),kind],text=True,capture_output=True,env=env,timeout=120)
 (R/'results'/(kind+'-verify.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-300:]
def wait_finished(kind):
 while True:
  plan=json.loads((R/'results/rental-plan.json').read_text())
  if time.time()>plan['deadline_epoch']-300:raise RuntimeError('Export and destruction reserve reached')
  p=R/'results'/(kind+'-monitor.jsonl')
  if p.exists():
   lines=p.read_text().splitlines()
   if lines and json.loads(lines[-1]).get('complete'):return
  time.sleep(10)
try:
 wait_finished('F2');remote.collect('F2');verify('F2');print('F2 LOCALLY VERIFIED',flush=True)
 plan=json.loads((R/'results/rental-plan.json').read_text());summary=json.loads((R/'private/download/results/F2/summary.json').read_text())
 # Baseline only if at least the measured F2 wall time plus export reserve fits deadline.
 if time.time()+summary['wall_seconds_this_process']*1.25+300<plan['deadline_epoch']:
  code="import torch,f2,worker,json; torch.backends.cuda.matmul.allow_tf32=False; m=f2.make('Transformer').cuda();o=f2.opt(m);d=worker.Data('train');x,doc,v,*_=d.batch('cuda');y=m(x,doc,v);z=x.clone();z[:,64:]=42;assert torch.equal(y[:,:64],m(z,doc,v)[:,:64]);r=worker.update(m,o,d,'cuda');assert sum(p.numel() for p in m.parameters())==2032768;print(json.dumps(dict(status='PASS',causal=True,finite_backward_AdamW=True,loss=r['loss'])))"
  output=remote.ssh('cd /workspace/neo-f2 && CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=deps python -c '+shlex.quote(code),timeout=120)
  (R/'results/baseline-preflight.log').write_text(output);remote.launch('Transformer')
  log=(R/'results/Transformer-monitor.log').open('w');p=subprocess.Popen([sys.executable,str(R/'monitor.py'),'Transformer'],stdout=log,stderr=log)
  wait_finished('Transformer');remote.collect('Transformer');verify('Transformer');print('BASELINE LOCALLY VERIFIED',flush=True)
 else:(R/'results/baseline-omitted.json').write_text(json.dumps(dict(reason='insufficient deadline margin after F2 export'))+'\n')
except BaseException as e:
 (R/'results/pipeline-failure.log').write_text(traceback.format_exc());print('PIPELINE ERROR',str(e),flush=True)
 # Preserve whatever is available before mandatory destruction, bounded time.
 try:remote.collect('F2')
 except Exception:pass
finally:
 instance=json.loads((R/'results/rental-receipt.json').read_text())['instance_id'];result=lifecycle.cleanup(instance);(R/'results/cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
 if result['absent']:(R/'private/cleanup-complete').touch()
 print('CLEANUP',result,flush=True)
 if result['absent']:subprocess.run([sys.executable,str(R/'close_billing.py')],timeout=120)
