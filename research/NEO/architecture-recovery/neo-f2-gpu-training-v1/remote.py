"""SSH orchestration; pinned first-use host key, no agent forwarding."""
from pathlib import Path
import subprocess,json,time,sys,hashlib,os
R=Path(__file__).resolve().parent;P=R/'private';RES=R/'results'
def api():return json.loads(subprocess.check_output(['vastai','show','instances','--raw'],text=True))
def connect():
 instance=json.loads((RES/'rental-receipt.json').read_text())['instance_id'];start=time.time()
 while time.time()-start<900:
  rows=[r for r in api() if r['id']==instance];assert rows
  r=rows[0]
  if r.get('actual_status')=='running':
   ports=r.get('ports') or {};direct=ports.get('22/tcp') or []
   host=r['public_ipaddr'] if direct else r['ssh_host'];port=int(direct[0]['HostPort']) if direct else int(r['ssh_port'])
   p=subprocess.run(['ssh-keyscan','-T','10','-p',str(port),'-t','ed25519',host],text=True,capture_output=True)
   lines=[l for l in p.stdout.splitlines() if 'ssh-ed25519' in l]
   if lines:
    (P/'known_hosts').write_text('\n'.join(lines)+'\n');endpoint=dict(instance=instance,host=host,port=port,host_key_policy='first-use pin from authenticated provider endpoint; execute unavailable on running instances; not an independently authenticated host fingerprint')
    (P/'endpoint.json').write_text(json.dumps(endpoint));return endpoint
  print('BOOT',r.get('actual_status'),str(r.get('status_msg',''))[-90:],flush=True);time.sleep(20)
 raise RuntimeError('Boot timeout')
def endpoint():return json.loads((P/'endpoint.json').read_text())
def ssh(cmd,timeout=120):
 e=endpoint();args=['ssh','-i',str(P/'ssh_key'),'-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-o','ConnectTimeout=15','-p',str(e['port']),'root@'+e['host'],cmd]
 p=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError('SSH '+str(p.returncode)+': '+p.stderr[-600:]+' '+p.stdout[-600:])
 return p.stdout
def scp(src,dest,download=False,timeout=180):
 e=endpoint();remote='root@'+e['host']+':'+(src if download else dest)
 args=['scp','-i',str(P/'ssh_key'),'-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-P',str(e['port'])]
 args+= [remote,str(dest)] if download else [str(src),remote]
 p=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError('SCP failed '+p.stderr[-500:])
def setup():
 e=connect();print('SSH endpoint ready',e['instance'],flush=True)
 print(ssh("mkdir -p /workspace/neo-f2 && python -c 'import torch,sys;print(sys.version);print(torch.__version__,torch.cuda.is_available())' && nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader"),flush=True)
 scp(P/'bundle.tar.gz','/workspace/neo-f2/bundle.tar.gz')
 digest=json.loads((RES/'bundle-summary.json').read_text())['sha256'];output=ssh('sha256sum /workspace/neo-f2/bundle.tar.gz');assert digest in output
 ssh('cd /workspace/neo-f2 && tar xzf bundle.tar.gz && python -m pip install --target deps --no-deps regex==2026.9.29 tokenizers==0.23.3',timeout=180)
 code="import json,hashlib,pathlib; r=pathlib.Path('.'); m=json.loads((r/'MANIFEST.json').read_text()); assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in m.items());print('ALL HASHES PASS')"
 print(ssh('cd /workspace/neo-f2 && python -c '+__import__('shlex').quote(code)),flush=True)
 hardware="import torch,sys,json,platform;print(json.dumps(dict(python=sys.version,torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(),vram=torch.cuda.get_device_properties(0).total_memory,bf16=torch.cuda.is_bf16_supported(),platform=platform.platform())))"
 text=ssh('python -c '+__import__('shlex').quote(hardware));(RES/'gpu-environment.log').write_text(text)
 print(ssh('cd /workspace/neo-f2 && CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=deps python worker.py --preflight > preflight.log 2>&1 && cat results/F2/preflight.json',timeout=180),flush=True)
 scp('/workspace/neo-f2/results/F2/preflight.json',RES/'cuda-preflight.json',download=True)
 print('CUDA PREFLIGHT PASS',flush=True)
def launch(kind):
 cmd='cd /workspace/neo-f2; nohup env CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=deps python worker.py --kind '+kind+' > '+kind+'.log 2>&1 < /dev/null & echo $!'
 print(ssh(cmd),flush=True);print('LAUNCHED',kind,flush=True)
def collect(kind):
 ssh('cd /workspace/neo-f2 && tar czf '+kind+'-results.tar.gz results/'+kind+' '+kind+'.log')
 expected=ssh('sha256sum /workspace/neo-f2/'+kind+'-results.tar.gz').split()[0]
 scp('/workspace/neo-f2/'+kind+'-results.tar.gz',P/(kind+'-results.tar.gz'),download=True)
 actual=hashlib.sha256((P/(kind+'-results.tar.gz')).read_bytes()).hexdigest();assert actual==expected
 (RES/(kind+'-export.json')).write_text(json.dumps(dict(archive_sha256=actual,utc=time.time()),indent=2)+'\n')
 import tarfile
 with tarfile.open(P/(kind+'-results.tar.gz')) as tar:
  assert all(not m.name.startswith('/') and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in tar.getmembers());tar.extractall(P/'download')
 print('EXPORTED',kind,actual,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='launch':launch(sys.argv[2])
 elif sys.argv[1]=='collect':collect(sys.argv[2])
 elif sys.argv[1]=='status':
  print(ssh("tail -3 /workspace/neo-f2/F2.log 2>/dev/null; tail -3 /workspace/neo-f2/Transformer.log 2>/dev/null; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; true"))
