from recover import *
from datetime import datetime,timezone
P=ROOT.parent.parent
items=[]
for p in sorted(C.glob('releases/*/manifest.json'))+sorted(C.glob('curation-v1/runs/*/release/manifest.json')):
 r=json.loads(p.read_text());items.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'modified_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'documents_reported':r.get('documents'),'text_bytes_reported':r.get('text_bytes'),'status':('FOUND_VERIFIED' if p.parent.name=='growth-1b-v1-estimated-1000000000' or p.parent.parent.name in ['1b-refined','500m-refined'] else 'FOUND_MANIFEST_ONLY'),'format':r.get('format',r.get('schema'))})
metadata=[]
for p in sorted((C/'metadata').glob('*')):
 if p.is_file():metadata.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
put('catalog',{'releases':items,'source_evidence':metadata,'scope':['/PATH/TO/NEO_HOME/research','/PATH/TO/NEO_HOME/evaluations','Git worktrees/branches in neo-architecture-recovery'],'notes':['No external backup discovered in searched research/evaluation directories; original release versions and token snapshot located locally. No new downloads.','4360 found as excluded/quarantined BASE documents in MEASURED_500M.md, not verified as a separate 4360-document BASE corpus. master-0001 has16556 records.'],'source_inventory':[{'source':s,'decision':d,'evidence':e,'condition':c} for s,d,e,c in [
 ('python/cpython','APROBADO','metadata/CPython-LICENSE.txt; CPython-sources.json file SHA','Retained7 quality-approved files; EXCLUDE F2 training due historical D0 CPython test-family reservation'),
 ('wikimedia/wikipedia','CUARENTENA','metadata/wikimedia--wikipedia.md; original curation rights audit','Attribution/share-alike and per-document provenance conditions not closed; public availability is insufficient'),
 ('HuggingFaceFW/fineweb-2','CUARENTENA','metadata/HuggingFaceFW--fineweb-2.md','Collection metadata does not clear underlying web rights'),
 ('HuggingFaceFW/fineweb-edu','CUARENTENA','metadata/HuggingFaceFW--fineweb-edu.md','Same underlying-document rights gate'),
 ('HuggingFaceTB/finemath','CUARENTENA','metadata/HuggingFaceTB--finemath.md','Underlying web rights unresolved'),
 ('OpenAssistant/oasst1','CUARENTENA','metadata/OpenAssistant--oasst1.md','765 SFT separate; individual provenance/PII and conditions unresolved; never auto-convert to BASE'),
 ('D0.1 Click','APROBADO','data/d0.1/raw/click-LICENSE.rst; accepted.jsonl file hashes','BSD-3-Clause, preserve notices; original train family'),
 ('D0.1 Requests','APROBADO','data/d0.1/raw/requests-LICENSE; accepted.jsonl file hashes','Apache-2.0, preserve notices; original dev family'),
 ('D0.1 Gutenberg/OASST','CUARENTENA','language-foundation/DATA_READINESS.md','Territorial/individual rights unresolved; no F2 use'),
 ('quality/evaluation-conflict records','EXCLUIDO','curation decision manifests and read-only index','New F2 use prohibited; original preserved')]]})
# Historical V1 cache numbers, not additive across overlapping views.
history={}
for label,p in [('live',C/'curation-v1/token-cache.sqlite'),('frozen500',C/'curation-v1/runs/500m/token-certificates-snapshot.sqlite')]:
 con=sqlite3.connect(f'file:{p}?mode=ro',uri=True);con.execute('begin');history[label]={'path':str(p),'tokenizer':con.execute('select v from meta where k="tokenizer"').fetchone()[0],'certificates':con.execute('select status,count(*),sum(ids),sum(targets) from tokens group by status').fetchall()};con.close()
put('historical-counts',history)
