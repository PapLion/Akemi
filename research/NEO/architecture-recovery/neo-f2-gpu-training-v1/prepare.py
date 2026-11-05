"""Bounded private-research selection; retain historical rights status unchanged."""
from pathlib import Path
import sys,json,hashlib,sqlite3,array,re,collections,shutil,time
import numpy as np
R=Path(__file__).resolve().parent;BASE=R.parent;PROJECT=BASE.parent
sys.path.insert(0,str(BASE/'corpus-recovery-f2'));import count_v3
s=json.loads((BASE/'f2-corpus-release/results/conditional-selection.json').read_text());tok=count_v3.load()
cache=sqlite3.connect('file:'+str(BASE/'f2-corpus-release/counts.sqlite')+'?mode=ro',uri=True)
# Concrete exceptions flagged for exclusion; absence of markers is not a guarantee of title.
pat=re.compile(r'fair[ -]use|all rights reserved|todos los derechos reservados|uso (?:leg[ií]timo|justo)|non[- ]commercial|no comercial|permission required|permiso (?:expreso|previo)',re.I)
out=R/'private/bundle';out.mkdir(parents=True,exist_ok=True)
selected=[];excluded=[];arrays={x:[] for x in ['train','dev']};offsets={x:[0] for x in arrays};quality=collections.Counter()
for d in s['documents']:
 with open(d['path'],'rb') as f:f.seek(d['offset']);record=json.loads(f.readline())
 text=record['text'];assert hashlib.sha256(text.encode()).hexdigest()==d['sha256']
 if pat.search(text):excluded.append(dict(key=d['key'],sha256=d['sha256'],reason='explicit rights/exception marker requires separate review'));continue
 assert record['provenance']['revision']==d['source_revision'] and record['provenance']['source_url']==d['source_url']
 fp,n,blob=cache.execute('select fp,n,ids from counts where sha=?',(d['sha256'],)).fetchone();assert fp==count_v3.FP and n==d['text_ids']
 ids=np.frombuffer(blob,dtype=np.uint16).copy();assert tok.decode(ids.tolist())==text
 split=d['split'];arr=np.concatenate([np.array([257],dtype=np.uint16),ids,np.array([258],dtype=np.uint16)])
 arrays[split].append(arr);offsets[split].append(offsets[split][-1]+len(arr))
 item={k:v for k,v in d.items() if k not in ['path','offset']};item['dataset_doc_index']=len(arrays[split])-1;item['release_status']='ELIGIBLE_PRIVATE_LICENSED_RESEARCH';item['historical_status']='CONDITIONAL';selected.append(item)
for split,ls in arrays.items():np.savez_compressed(out/(split+'.npz'),ids=np.concatenate(ls),offsets=np.array(offsets[split],dtype=np.int64),langs=np.array([d['lang'] for d in selected if d['split']==split]))
meta=dict(schema='neo-f2-gpu-dataset-v1',documents=selected,excluded=excluded,tokenizer=count_v3.FP,tokenizer_sha256=count_v3.sha(count_v3.ART),targets_available={split:sum(len(a)-1 for a in ls) for split,ls in arrays.items()},train_target_cap=5000000,scope='private bounded experiment under declared CC-BY-SA original-text license, attribution retained; no public corpus/weights release',historical_conditions_not_globally_closed=True,rights_exception_screen='explicit rights markers; not legal guarantee or full manual review',created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
(out/'dataset.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
attrs=[json.loads(x) for x in (BASE/'f2-corpus-release/results/attribution.jsonl').read_text().splitlines()];keys={d['key'] for d in selected}
(out/'attribution.jsonl').write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in attrs if a['key'] in keys))
shutil.copy(BASE/'f2-corpus-release/evidence/license.txt',out/'LICENSE_CC_BY_SA_3.txt');shutil.copy(count_v3.ART,out/'tokenizer.json');shutil.copy(PROJECT/'neotoken-v3/core.py',out/'core.py')
for name in ['regex','tokenizers']:
 import importlib.metadata
 print(name,importlib.metadata.version(name))
print(json.dumps(dict(documents=len(selected),excluded=len(excluded),available=meta['targets_available']),indent=2))
(R/'results/dataset-summary.json').write_text(json.dumps(dict(documents=len(selected),excluded=len(excluded),available=meta['targets_available'],tokenizer=meta['tokenizer']),indent=2)+'\n')
