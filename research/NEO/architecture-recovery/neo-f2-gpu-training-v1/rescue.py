from pathlib import Path
import sys,json,hashlib,shlex
import remote
R=Path(__file__).resolve().parent;kind=sys.argv[1]
code="import pathlib,json,hashlib; p=max(pathlib.Path('results/"+kind+"').glob('targets-*.pt'),key=lambda x:int(x.stem.split('-')[1]));print(json.dumps(dict(name=p.name,sha=hashlib.sha256(p.read_bytes()).hexdigest())))"
x=remote.ssh('cd /workspace/neo-f2 && python -c '+shlex.quote(code));meta=json.loads(x.strip().splitlines()[-1]);dest=R/'private/rescued'/kind;dest.mkdir(parents=True,exist_ok=True)
remote.scp('/workspace/neo-f2/results/'+kind+'/'+meta['name'],dest/meta['name'],download=True);assert hashlib.sha256((dest/meta['name']).read_bytes()).hexdigest()==meta['sha'];(R/'results'/(kind+'-rescued.json')).write_text(json.dumps(meta,indent=2)+'\n');print('RESCUED',kind,meta)
