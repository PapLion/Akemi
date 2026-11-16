"""Autonomous lifecycle wrapper around the existing Neo Vast/SSH infrastructure.

No torch dependency: archiving and GPU deletion must work even if ML imports fail.
All runtime state is private. Never automatically rerent, retry training, or reset a cursor.
"""
import argparse
import ast
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT/'private'
RCLONE = Path('/home/dani.pp/.local/share/pa-mini-backup-tools/rclone-v1.75.2-linux-amd64/rclone')
REMOTE = 'pa-drive:NEO-Research-Archives-v1'
REPO = 'PapLion/Akemi'
BRANCH = 'neo-contextual-causal-diagnosis-v1'
REMOTE_ROOT = 'research/NEO/architecture-recovery/neo-training-operations'


def atomic(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def read(path):return json.loads(Path(path).read_text())


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):h.update(b)
    return h.hexdigest()


def command(argv, timeout=60):
    r=subprocess.run(list(map(str,argv)),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if r.returncode:raise RuntimeError(f'{Path(str(argv[0])).name} failed (exit {r.returncode}); credential/output content suppressed')
    return r.stdout


def credential_preflight(key, rclone_config):
    for path in (key,rclone_config):
        if not Path(path).is_file():raise FileNotFoundError('Required private credential file missing')
        if Path(path).stat().st_mode & 0o077:raise PermissionError('Credential file must be private (0600)')


def validate_budget(cfg):
    if not re.fullmatch(r'neo-[a-z0-9-]{12,75}',cfg['job_id']):raise ValueError('Unique neo- job ID required')
    seconds=float(cfg['max_runtime_seconds']);rate=float(cfg['hourly_usd']);reserve=float(cfg['recovery_seconds'])
    if not all(math.isfinite(float(cfg[k])) for k in ('max_runtime_seconds','hourly_usd','recovery_seconds','transfer_reserve_usd','max_usd')):
        raise ValueError('Budget must contain finite numbers')
    if float(cfg['transfer_reserve_usd'])<0 or float(cfg['max_usd'])<=0:raise ValueError('Invalid expense bounds')
    if not 60 <= seconds <= 14400 or not 30 <= reserve < seconds or rate <= 0:
        raise ValueError('Invalid runtime/rate/recovery reserve')
    maximum=rate*seconds/3600+float(cfg['transfer_reserve_usd'])
    if maximum > float(cfg['max_usd']):raise ValueError('Maximum expense exceeds authorization')
    return {'maximum_usd':maximum,'runtime_seconds':seconds,'recovery_seconds':reserve}


class LocalStore:
    def __init__(self,root):self.root=Path(root)
    def put(self,source,key,timeout):
        target=self.root/key;target.parent.mkdir(parents=True,exist_ok=True)
        digest=sha(source)
        if target.exists() and sha(target)!=digest:raise ValueError('Immutable archive collision')
        if not target.exists():
            tmp=target.with_name(target.name+'.partial');shutil.copyfile(source,tmp);os.replace(tmp,target)
        if sha(target)!=digest:raise ValueError('Archive verification failed')
        return {'uri':str(target),'sha256':digest,'verified':True}


class DriveStore:
    def __init__(self,remote=REMOTE,binary=RCLONE):self.remote=remote;self.binary=str(binary)
    def put(self,source,key,timeout):
        # Content-addressed path; verify actual downloaded bytes, not just an upload return code.
        destination=self.remote+'/'+key
        end=time.monotonic()+timeout
        def left():return max(.1,end-time.monotonic())
        command([self.binary,'copyto',source,destination,'--immutable','--retries','1',
                 '--low-level-retries','1','--timeout','30s','--contimeout','15s'],timeout=left())
        with tempfile.TemporaryFile() as f:
            p=subprocess.Popen([self.binary,'cat',destination,'--retries','1','--low-level-retries','1'],
                               stdout=f,stderr=subprocess.DEVNULL)
            try:rc=p.wait(timeout=left())
            except BaseException:p.kill();p.wait();raise
            if rc:raise RuntimeError('Archive download verification failed')
            f.seek(0);h=hashlib.sha256()
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        if h.hexdigest()!=sha(source):raise ValueError('Uploaded SHA-256 mismatch')
        return {'uri':destination,'sha256':h.hexdigest(),'verified':True}

    def prune_snapshot(self, previous, current, job_id):
        prefix=self.remote+'/'+job_id+'/snapshots/'
        old=previous.get('uri','')
        if old!=current['uri'] and old.startswith(prefix) and previous.get('verified'):
            # Only obsolete operational snapshots, after a verified replacement. Never source checkpoints.
            command([self.binary,'deletefile',old,'--drive-use-trash=false','--retries','1'],timeout=30)


def helpers(private):
    spec=importlib.util.spec_from_file_location('neo_existing_vast',ROOT.parent/'neo-language-pretraining-a1-v1/a1_pipeline.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    a.P=Path(private);a.RES=Path(private)
    return a


class Provider:
    def __init__(self,private):self.a=helpers(private)
    def instances(self):return self.a.instances()
    def destroy(self,instance):self.a.cli('destroy','instance',str(instance),'--yes')


def destroy_owned(provider,manifest,attempts=3):
    from watchdog import enforce
    last={'confirmed':False,'attempted':True}
    for _ in range(attempts):
        try:
            last=enforce({**manifest,'deadline':0},provider)
            if last['confirmed']:return {**last,'attempted':True}
        except Exception as e:last={'confirmed':False,'attempted':True,'error_type':type(e).__name__}
    return last


def finalize(path,archive,store,provider,deadline,retries=3,backoff=2):
    m=read(path)
    try:
        if not m.get('archive',{}).get('verified'):
            m['archive']={'verified':False,'attempts':0}
            for n in range(retries):
                if time.time() >= deadline-2:break
                m['archive']['attempts']=n+1;atomic(path,m)
                try:
                    if archive is None:raise FileNotFoundError('No recovered archive')
                    key=m['job_id']+'/'+sha(archive)+'.tar'
                    m['archive']={**store.put(archive,key,max(.1,deadline-time.time()-2)), 'attempts':n+1}
                    break
                except Exception as e:
                    m['archive']['error_type']=type(e).__name__
                    if n+1<retries:time.sleep(min(backoff*2**n,max(0,deadline-time.time()-2)))
            atomic(path,m)
    finally:
        # Shutdown is independent of upload, optional ML validation, and signal state.
        m['cleanup']=destroy_owned(provider,m);m['ended']=time.time()
        train=m.get('training',{})
        if m['cleanup']['confirmed'] and m.get('archive',{}).get('verified'):
            m['outcome']=('completed_archived_shutdown_confirmed' if train.get('outcome')=='completed'
                           and train.get('returncode')==0 and train.get('outputs_valid')
                           and m.get('checkpoint_validation',{}).get('passed',True)
                           else 'failed_or_unknown_training_artifacts_recovered_shutdown_confirmed')
        else:m['outcome']='shutdown_confirmed_archive_failed' if m['cleanup']['confirmed'] else 'shutdown_attempted_unconfirmed'
        atomic(path,m)
        # A final manifest upload failure cannot prevent shutdown; authoritative copy is local.
        if time.time()<deadline-2:
            try:m['manifest_archive']=store.put(path,m['job_id']+'/manifests/'+sha(path)+'.json',deadline-time.time()-1)
            except Exception as e:m['manifest_upload_error_type']=type(e).__name__
            atomic(path,m)
    return m


def snapshot(a,cfg,private,timeout):
    # GNU tar returns 1 for a changing source; reject that snapshot rather than certify corruption.
    paths=cfg['artifact_paths']
    if any(p.startswith('/') or '..' in Path(p).parts for p in paths):raise ValueError('Artifact paths must be within remote workdir')
    root=cfg['remote_dir'];dest=private/'recovered.tar'
    # Missing paths are explicit in required_files validation, but must not prevent rescue of logs.
    sources='; '.join('[ ! -e '+shlex.quote(p)+' ] || set -- "$@" '+shlex.quote(p) for p in paths+['.neo-worker'])
    remote=root+'/.neo-recovery.tar'
    a.ssh('cd '+shlex.quote(root)+' || exit 1; set --; '+sources+'; test "$#" -gt 0 && tar -cf .neo-recovery.tar -- "$@"',timeout=timeout)
    expected=a.ssh('sha256sum '+shlex.quote(remote),timeout=min(30,timeout)).split()[0]
    part=dest.with_suffix('.partial');a.scp(remote,part,download=True,timeout=timeout)
    if sha(part)!=expected:raise ValueError('SCP archive checksum mismatch')
    os.replace(part,dest)
    with tarfile.open(dest) as tar:
        for member in tar:
            if member.name.startswith('/') or '..' in Path(member.name).parts or member.issym() or member.islnk():
                raise ValueError('Unsafe archive member')
    return dest


def arm(cfg,private):
    """Publish only a non-sensitive plan; wait for authenticated external runner receipt."""
    import base64
    now=time.time()
    plan={'job_id':cfg['job_id'],'label':cfg['job_id'],'armed_at':now,
          'deadline':now+cfg['max_runtime_seconds'], 'maximum_usd':validate_budget(cfg)['maximum_usd']}
    if cfg.get('instance_id'):plan['instance_id']=int(cfg['instance_id'])
    # Reject a second watcher/job. A pending stale plan cannot silently authorize another lease.
    runs=json.loads(command(['gh','run','list','-R',REPO,'--branch',BRANCH,'--workflow','neo-watchdog.yml',
                            '--json','status,databaseId','--limit','10']))
    if any(r['status']!='completed' for r in runs):raise RuntimeError('An external watchdog is already pending/active')
    rel=REMOTE_ROOT+'/arm.json';endpoint=f'repos/{REPO}/contents/{rel}'
    old=json.loads(command(['gh','api',endpoint+'?ref='+BRANCH]))
    payload={'message':'Arm bounded Neo GPU deadline '+cfg['job_id'],'branch':BRANCH,
             'content':base64.b64encode(json.dumps(plan,indent=2).encode()).decode(),'sha':old['sha']}
    payload_file=private/'github-plan-request.json';atomic(payload_file,payload)
    result=json.loads(command(['gh','api','-X','PUT',endpoint,'--input',payload_file]))
    commit=result['commit']['sha'];atomic(private/'watchdog-plan.json',plan)
    started=time.time()
    while time.time()-started<180:
        rows=json.loads(command(['gh','run','list','-R',REPO,'--branch',BRANCH,'--commit',commit,
                                '--json','databaseId,status,conclusion','--limit','5']))
        for run in rows:
            if run['status']=='completed':raise RuntimeError('External watchdog exited before rental')
            folder=private/'armed';folder.mkdir(exist_ok=True)
            try:
                command(['gh','run','download',str(run['databaseId']),'-R',REPO,'-n','neo-watchdog-armed','-D',folder],timeout=20)
                receipt=read(folder/'armed.json')
                if receipt['job_id']!=cfg['job_id'] or receipt['plan_sha256']!=sha(private/'watchdog-plan.json'):
                    raise ValueError('Watchdog receipt mismatch')
                receipt['run_id']=run['databaseId'];atomic(private/'external-watchdog.json',receipt)
                return plan
            except RuntimeError:pass
        time.sleep(3)
    raise TimeoutError('No external armed receipt: GPU creation prohibited')


def run(config_path):
    cfg=read(config_path);budget=validate_budget(cfg);private=PRIVATE/cfg['job_id'];private.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (private/'supervisor.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        manifest=private/'manifest.json';a=helpers(private);provider=Provider(private);store=DriveStore()
        archive=None;m=read(manifest) if manifest.exists() else None
        if m and m.get('cleanup',{}).get('confirmed'):return m
        interrupted=[False]
        def stop(signum,frame):interrupted[0]=True
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        try:
            if m is None:
                credential_preflight(Path.home()/'.config/vastai/vast_api_key',Path.home()/'.config/rclone/rclone.conf')
                if not cfg.get('authorization_reference'):raise PermissionError('Explicit job authorization reference missing')
                if not cfg.get('required_files') or not cfg.get('validate_command'):
                    raise ValueError('Explicit completion outputs and scientific checkpoint validator required')
                if sha(Path(cfg['bundle']))!=cfg['bundle_sha256']:
                    raise ValueError('Frozen bundle changed; rental prohibited')
                if cfg.get('source_root'):
                    for name,digest in cfg['dataset']['hashes'].items():
                        if sha(Path(cfg['source_root'])/name)!=digest:
                            raise ValueError('Frozen scientific source/data changed; rental prohibited')
                if not Path(cfg['python']).is_file():raise FileNotFoundError('Configured ML Python missing')
                # Smoke-load torch before renting, avoids previous controller interpreter failure.
                command([cfg['python'],'-c','import torch'],timeout=30)
                if cfg.get('validation_preflight_command'):
                    command(cfg['validation_preflight_command'],timeout=30)
                if not cfg.get('instance_id') and provider.instances():raise RuntimeError('Other instances active; no new lease')
                if a.cli('show','volumes'):raise RuntimeError('Unexpected existing volumes; manual classification required')
                credit=float(a.cli('show','user')['credit'])
                if credit<float(cfg['max_usd']):raise PermissionError('Insufficient existing credit; never buy credits')
                if not cfg.get('instance_id'):
                    # Vast's search `id` filter does not match the returned rental-offer ID.
                    # Query the selected host, then require the exact offered contract locally.
                    host=cfg.get('selected_offer',{}).get('machine_id')
                    query='machine_id='+str(int(host)) if host is not None else 'id='+str(int(cfg['offer_id']))
                    offers=a.cli('search','offers',query,'--limit','100')
                    offer=next(r for r in offers if int(r['id'])==int(cfg['offer_id']))
                    hourly=float(offer['dph_total'])+float(cfg['disk_gb'])*float(offer['storage_cost'])/730
                    if hourly>float(cfg['hourly_usd']):raise ValueError('Live GPU/storage price exceeds configured ceiling')
                    if max(float(offer['inet_up_cost']),float(offer['inet_down_cost']))*float(cfg['max_transfer_gb'])>float(cfg['transfer_reserve_usd']):
                        raise ValueError('Transfer envelope exceeds reserved budget')
                # Real storage readback preflight before any paid create call.
                probe=private/'storage-preflight.json';atomic(probe,{'job_id':cfg['job_id'],'preflight':True})
                storage=store.put(probe,cfg['job_id']+'/preflight.json',60)
                plan=arm(cfg,private)
                m={**plan,'config':cfg,'budget':budget,'storage_preflight':storage,'started':time.time(), 'credit_before':credit,
                   'instance_id':cfg.get('instance_id'),'phase':'armed','external_watchdog':read(private/'external-watchdog.json')}
                atomic(manifest,m)
                if cfg.get('instance_id'):
                    rows=provider.instances();row=next(r for r in rows if int(r['id'])==int(cfg['instance_id']))
                    if row.get('label')!=cfg['job_id']:raise ValueError('Cannot attach unrelated instance')
                else:
                    # No automatic create retries: watchdog covers unique label even if the API response is lost.
                    m['phase']='create_attempted';atomic(manifest,m)
                    response=a.cli('create','instance',str(cfg['offer_id']),'--disk',str(cfg['disk_gb']),
                                   '--image',a.IMAGE,'--ssh','--direct','--cancel-unavail','--label',cfg['job_id'])
                    if not response.get('success') or not response.get('new_contract'):raise RuntimeError('Lease not confirmed')
                    m['instance_id']=int(response['new_contract']);m['phase']='connecting';atomic(manifest,m)
            deadline=m['deadline'];soft=deadline-cfg['recovery_seconds']
            if time.time()>=soft:raise TimeoutError('Recovery reserve reached; no training startup')
            # Recover unacknowledged creates by unique label; never issue another create on restart.
            if not m.get('instance_id'):
                owned=[r for r in provider.instances() if r.get('label')==cfg['job_id']]
                if len(owned)!=1:raise RuntimeError('Create outcome unresolved; watchdog owns cleanup, no rerent')
                m['instance_id']=int(owned[0]['id']);atomic(manifest,m)
            setup_connection(a,cfg,m,private,soft)
            last_sync=0
            while time.time()<soft and not interrupted[0]:
                try:
                    text=a.ssh('cat '+shlex.quote(cfg['remote_dir']+'/.neo-worker/status.json'),timeout=20)
                    m['training']=json.loads(text)
                    if m['training'].get('job_id')!=cfg['job_id']:raise ValueError('Worker receipt belongs to a different job')
                    atomic(manifest,m);break
                except RuntimeError:pass  # only means no exit receipt; never infer success from a missing PID
                if time.time()-last_sync>=cfg.get('sync_seconds',300):
                    try:
                        archive=snapshot(a,cfg,private,min(120,max(1,soft-time.time())))
                        previous=m.get('periodic_archive',{})
                        m['periodic_archive']=store.put(archive,cfg['job_id']+'/snapshots/'+sha(archive)+'.tar',120)
                        atomic(manifest,m)
                        store.prune_snapshot(previous,m['periodic_archive'],cfg['job_id'])
                    except Exception as e:m['periodic_sync_error_type']=type(e).__name__;atomic(manifest,m)
                    last_sync=time.time()
                time.sleep(2)
            else:
                m['training']={'outcome':'interrupted' if interrupted[0] else 'timeout','returncode':None};atomic(manifest,m)
        except BaseException as e:
            if m is not None:
                m['supervisor_error_type']=type(e).__name__;atomic(manifest,m)
            else:raise
        finally:
            if m is not None:
                deadline=m['deadline']
                try:
                    # Signal wrapper, not an unscoped pkill that could kill another experiment.
                    cmd='cd '+shlex.quote(cfg['remote_dir'])+" && python -c "+shlex.quote(
                        "import json,os,signal,pathlib;p=pathlib.Path('.neo-worker/running.json');"
                        "s=pathlib.Path('.neo-worker/status.json');"
                        "os.kill(json.loads(p.read_text())['supervisor_pid'],signal.SIGTERM) if p.exists() and not s.exists() else None")
                    a.ssh(cmd,timeout=min(20,max(1,deadline-time.time())))
                    # Wait for the remote wrapper to flush/terminate the real child before final snapshot.
                    until=min(deadline-60,time.time()+45)
                    while time.time()<until:
                        try:
                            m['training']=json.loads(a.ssh('cat '+shlex.quote(cfg['remote_dir']+'/.neo-worker/status.json'),timeout=10))
                            atomic(manifest,m);break
                        except Exception:time.sleep(1)
                    archive=snapshot(a,cfg,private,min(120,max(1,deadline-time.time()-30)))
                    # Validate model/AdamW/RNG/cursor using the experiment's existing verifier, before deletion.
                    if cfg.get('validate_command'):
                        command([*cfg['validate_command'],str(archive)],timeout=min(60,max(1,deadline-time.time()-20)))
                        m['checkpoint_validation']={'passed':True}
                except Exception as e:
                    m['recovery_error_type']=type(e).__name__
                    if cfg.get('validate_command'):m['checkpoint_validation']={'passed':False}
                atomic(manifest,m)
                if archive is None and (private/'recovered.tar').exists():archive=private/'recovered.tar'
                result=finalize(manifest,archive,store,provider,deadline-5)
                try:
                    result['credit_after']=a.cli('show','user')['credit']
                    result['account_credit_delta_usd']=result['credit_before']-result['credit_after']
                    result['billing_note']='Account credit delta, may include unrelated activity; hourly envelope is separate'
                    atomic(manifest,result)
                except Exception:pass


def attach_ssh(instance,public_key):
    """Installed Vast CLI prints a Python dict for attach, even with --raw.

    The historical JSON-only helper rejects a successful response. Decode only
    this command's data response; never eval code or suppress a failed exit.
    """
    raw=command(['vastai','attach','ssh',str(instance),str(public_key),'--raw'])
    try:result=json.loads(raw)
    except ValueError:result=ast.literal_eval(raw.decode('utf-8'))
    if not isinstance(result,dict) or result.get('success') is not True:
        raise RuntimeError('SSH attachment was not confirmed')
    return result


def setup_connection(a,cfg,m,private,soft):
    """Reuse tested Vast key, SSH transfer and hash mechanics; never rerun a scientific process."""
    if not (private/'ssh_key').exists():
        command(['ssh-keygen','-q','-t','ed25519','-N','','-f',private/'ssh_key','-C',cfg['job_id']])
    # Attach works for an existing account key too. Provider credentials never leave this workstation.
    m['phase']='ssh_key_attachment';atomic(private/'manifest.json',m)
    attach_ssh(m['instance_id'],private/'ssh_key.pub')
    m['phase']='ssh_boot_wait';atomic(private/'manifest.json',m)
    a.BOOT_TIMEOUT_S=min(300,max(1,int(soft-time.time())))
    a.connect(m['instance_id'])
    remote=cfg['remote_dir']
    try:
        status=a.ssh('cat '+shlex.quote(remote+'/.neo-worker/running.json'),timeout=20)
        if json.loads(status)['job_id']==cfg['job_id']:return  # attach without a second Popen
        raise ValueError('Remote work directory belongs to another experiment')
    except RuntimeError:pass
    if cfg.get('attach_only'):raise RuntimeError('Existing worker lacks exit-status wrapper; refusing restart')
    bundle=Path(cfg['bundle'])
    if sha(bundle)!=cfg['bundle_sha256']:raise ValueError('Frozen bundle changed')
    if not remote.startswith('/workspace/neo/'):raise ValueError('Unexpected remote root')
    a.ssh('mkdir -p /workspace/neo',timeout=20);a.scp(bundle,'/workspace/neo/ops-bundle.tar.gz',timeout=180)
    if a.ssh('sha256sum /workspace/neo/ops-bundle.tar.gz',timeout=20).split()[0]!=sha(bundle):raise ValueError('Transferred bundle mismatch')
    a.ssh('cd /workspace/neo && tar xzf ops-bundle.tar.gz',timeout=60)
    for setup in cfg.get('setup_commands',[]):a.ssh(setup,timeout=120)
    a.scp(ROOT/'worker.py','/workspace/neo/neo-worker.py',timeout=30)
    # Existing experiment checks this file for its deadline; preserve its expected interface.
    atomic(private/'RENTAL.json',{'deadline':m['deadline'],'job_id':cfg['job_id'],'instance_id':m['instance_id']})
    a.scp(private/'RENTAL.json',remote+'/private/RENTAL.json',timeout=30)
    worker_cfg={'job_id':cfg['job_id'],'cwd':remote,'command':cfg['training_command'],
                'max_seconds':max(1,soft-time.time()),'env':cfg.get('env',{}),
                'required_files':cfg['required_files'],'term_grace_seconds':30}
    atomic(private/'worker.json',worker_cfg);a.scp(private/'worker.json','/workspace/neo/neo-worker.json',timeout=30)
    a.ssh('nohup python /workspace/neo/neo-worker.py /workspace/neo/neo-worker.json </dev/null '
          '>/workspace/neo/neo-supervisor.log 2>&1 &',timeout=20)


def launch(config_path):
    cfg=read(config_path);validate_budget(cfg)
    if not cfg.get('authorization_reference'):raise PermissionError('Job authorization is required')
    private=PRIVATE/cfg['job_id'];private.mkdir(parents=True,exist_ok=True,mode=0o700)
    frozen=private/'config.json'
    if frozen.exists() and read(frozen)!=cfg:raise ValueError('Do not change an existing job configuration')
    atomic(frozen,cfg)
    unit='neo-training-'+cfg['job_id']
    directory=Path.home()/'.config/systemd/user';directory.mkdir(parents=True,exist_ok=True)
    # Enabled unit + Linger=yes recovers even after a workstation reboot. Fixed absolute paths, no shell.
    quote=lambda x:'"'+str(x).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    text='[Unit]\nDescription=Neo autonomous training lifecycle\nAfter=network-online.target\nWants=network-online.target\n\n[Service]\nType=simple\n'
    text+='ExecStart='+ ' '.join(map(quote,[sys.executable,str(ROOT/'operations.py'),'run',str(frozen)]))+'\n'
    text+='Restart=on-failure\nRestartSec=10\nTimeoutStopSec=240\nKillMode=mixed\nUMask=0077\nEnvironment=PATH=/home/dani.pp/.local/bin:/usr/local/bin:/usr/bin:/bin\n\n[Install]\nWantedBy=default.target\n'
    (directory/(unit+'.service')).write_text(text)
    command(['systemctl','--user','daemon-reload']);command(['systemctl','--user','enable','--now',unit+'.service'])
    print(json.dumps({'unit':unit,'manifest':str(private/'manifest.json'),'journal':'journalctl --user -u '+unit+' -f'}))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['launch','run','guard']);ap.add_argument('config',nargs='?');args=ap.parse_args()
    if args.action=='launch':launch(Path(args.config).resolve())
    elif args.action=='run':run(args.config)
    else:
        # Second, persistent external-to-GPU guard. GitHub is the independent cloud watchdog.
        for path in PRIVATE.glob('neo-*/manifest.json'):
            m=read(path)
            if not m.get('cleanup',{}).get('confirmed') and time.time()>=m['deadline']:
                m['cleanup']=destroy_owned(Provider(path.parent),m);atomic(path,m)


if __name__=='__main__':main()
