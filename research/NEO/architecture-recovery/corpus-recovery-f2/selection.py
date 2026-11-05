"""Build fail-closed reference-only F2 selection. Does not train or copy text."""
from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(__file__).resolve().parent
def shingles(docs,n):
 s=set()
 for r in docs:
  w=re.findall(r'\w+',Path(r['path']).read_text().lower());s.update(tuple(w[i:i+n]) for i in range(max(0,len(w)-n+1)))
 return s
def build():
 r=json.loads((ROOT/'results/v3-counts.json').read_text());docs=r['selected'];tr=[d for d in docs if d['split']=='train'];dev=[d for d in docs if d['split']=='dev']
 assert len({d['sha'] for d in docs})==len(docs)
 assert not {d['family'] for d in tr}&{d['family'] for d in dev}
 overlap={str(n):len(shingles(tr,n)&shingles(dev,n)) for n in [5,12,64]};assert overlap['64']==0
 normalized=[hashlib.sha256(' '.join(Path(d['path']).read_text().split()).encode()).hexdigest() for d in docs];assert len(set(normalized))==len(docs)
 targets=sum(d['effective_targets_bos_text_eos'] for d in tr);result={'schema':'neo-f2-selection-v1','documents':docs,'train_documents':len(tr),'dev_documents':len(dev),'train_independent_targets':targets,'dev_targets':sum(d['effective_targets_bos_text_eos'] for d in dev),'requested_train_targets':5000000,'deficit_targets':5000000-targets,'ready':targets>=5000000,'known_train_dev_shared_word_shingles':overlap,'splits':'original document/repository family; Requests dev excluded train; CPython family excluded due D0 test reservation','rights_evidence':r['license_evidence_hashes'],'repeat_to_fill_budget_allowed':False,'span_policy':'n text IDs + BOS/EOS; windows stride context-1; each shifted target exactly once; no document boundary loss','limitations':'code/expository English only; no approved Spanish text in this selection; global benchmark contamination not certified'}
 (ROOT/'results/f2-selection.json').write_text(json.dumps(result,indent=2)+'\n');return result
def gate():
 r=json.loads((ROOT/'results/f2-selection.json').read_text())
 if not r['ready']:raise SystemExit(f"BLOCKED: {r['train_independent_targets']} independent approved targets; need {r['requested_train_targets']}. No training started.")
 raise SystemExit('Data volume gate passed; full F2 training still requires future authorization. No training started.')
if __name__=='__main__':
 import sys
 if '--check-training-gate' in sys.argv:gate()
 else:print(json.dumps({k:v for k,v in build().items() if k!='documents'},indent=2))
