"""Prepare the existing contrastive job without renting, training, or rebuilding frozen science."""
import argparse
from pathlib import Path
import sys
import time
import operations as o

PY='/home/dani.pp/evaluations/cryo-legacy-viability/.venv/bin/python'

def config():
    study=o.ROOT.parent/'neo-binding-objective-contrast-v1';bundle=study/'private/bundle.tar.gz'
    if not bundle.is_file():raise FileNotFoundError('Prepared historical bundle not present; do not reconstruct silently')
    source={name:o.sha(study/name) for name in ['objective.py','learning.py','adaptation.jsonl','panel.jsonl','OBJECTIVE_PROTOCOL.md']}
    env={'PYTHONPATH':'/workspace/neo/deps','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','CUBLAS_WORKSPACE_CONFIG':':4096:8'}
    remote='/workspace/neo/'+study.name
    return {'job_id':'neo-binding-'+time.strftime('%Y%m%d-%H%M%S',time.gmtime()),
        'authorization_reference':None,'offer_id':None,'instance_id':None,
        'max_usd':.75,'max_runtime_seconds':3600,'recovery_seconds':900,'hourly_usd':.3,
        'transfer_reserve_usd':.2,'max_transfer_gb':8,'disk_gb':40,
        'python':PY,'bundle':str(bundle),'bundle_sha256':o.sha(bundle),
        'architecture':['F8 normalized 8195840 parameters','Transformer8 7998720 parameters'],
        'dataset':{'version':'preregistered contrastive panel','hashes':source},'seed':17,
        'remote_dir':remote,'env':env,'training_command':['python','objective_driver.py','--device','cuda'],
        'setup_commands':[
            'cd /workspace/neo && python -m pip install --target deps --no-deps regex==2026.9.29 tokenizers==0.23.3',
            "cd /workspace/neo && python -c \"import hashlib,json,pathlib;m=json.load(open('HASHES.json'));assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in m.items())\"",
            'cd '+remote+' && env PYTHONPATH=/workspace/neo/deps OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 python objective_driver.py --device cuda --contracts'],
        'artifact_paths':['results/gpu','private/trained'],
        'required_files':['results/gpu/complete.json','private/trained/F8-0.0001.pt',
                          'private/trained/F8-0.003.pt','private/trained/Transformer8-0.0001.pt',
                          'private/trained/Transformer8-0.003.pt'],
        'validate_command':[PY,str(o.ROOT/'validate_archive.py')], 'sync_seconds':300}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(o.PRIVATE/'job-DRAFT.json'));args=ap.parse_args()
    dest=Path(args.output)
    if dest.exists():raise FileExistsError('Never overwrite a prepared job configuration')
    o.atomic(dest,config());print(dest)
