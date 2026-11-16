"""Real local service / private Drive integration; provider is strictly a fake, no GPU API calls."""
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import operations as o

class NoCloudGPU:
    def instances(self):return []
    def destroy(self,instance):raise AssertionError('Self-test must never destroy any actual instance')

if __name__=='__main__':
    job='neo-selftest-'+time.strftime('%Y%m%d-%H%M%S',time.gmtime())
    root=o.PRIVATE/job;root.mkdir(parents=True,exist_ok=False)
    work=root/'outputs';work.mkdir()
    cfg={'job_id':job,'cwd':str(work),'command':[sys.executable,'-c',
         "from pathlib import Path;import time;time.sleep(2);Path('dummy-checkpoint.json').write_text('{\"dummy\":true,\"cursor\":1}')"],
         'required_files':['dummy-checkpoint.json'],'max_seconds':20}
    o.atomic(root/'worker.json',cfg)
    rc=subprocess.run([sys.executable,str(o.ROOT/'worker.py'),str(root/'worker.json')]).returncode
    archive=root/'test.tar'
    with tarfile.open(archive,'w') as tar:tar.add(work,arcname='outputs')
    manifest=root/'manifest.json';o.atomic(manifest,{'job_id':job,'label':job,'instance_id':None,
        'training':o.read(work/'.neo-worker/status.json'),'test_only':True})
    result=o.finalize(manifest,archive,o.DriveStore(),NoCloudGPU(),time.time()+90)
    if rc or not result['archive']['verified'] or not result['cleanup']['confirmed']:raise RuntimeError('Integration failed')
    receipt={'test_only':True,'GPU_operations':'none (mock provider)', 'job_id':job,
             'storage':result['archive'],'outcome':result['outcome'],'local_manifest':str(manifest)}
    o.atomic(o.ROOT/'results/storage-service-test.json',receipt)
    print(json.dumps(receipt,indent=2))
