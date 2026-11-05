"""Non-destructive rights ledger and resumable exact candidate counts. No training."""
from pathlib import Path
import sys,sqlite3,json,hashlib,time,collections,urllib.request,array
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
sys.path.insert(0,str(ROOT.parent/'corpus-recovery-f2'))
import count_v3
C=PROJECT/'chinchilla-corpus'
OLD=PROJECT/'neo-corpus-recovery-f2-readiness-v1/corpus-recovery-f2'
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(name,obj): (ROOT/'results'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def connect(p):return sqlite3.connect(f'file:{p}?mode=ro',uri=True)
def main():
 started=time.time(); tok=count_v3.load()
 evidence=[]
 urls={'license':'https://creativecommons.org/licenses/by-sa/3.0/legalcode','attribution':'https://meta.wikimedia.org/wiki/Licensing_update/Implementation','card':'https://huggingface.co/datasets/wikimedia/wikipedia/raw/b04c8d1ceb2f5cd4588862100d08de323dccfbaa/README.md','oasst':'https://huggingface.co/datasets/OpenAssistant/oasst1/raw/main/README.md'}
 for name,url in urls.items():
  dest=ROOT/'evidence'/(name+'.txt')
  try:
   if not dest.exists():dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NEO-rights-audit/1.0'}),timeout=30).read())
   evidence.append(dict(name=name,url=url,sha256=sha(dest.read_bytes()),retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(dest.stat().st_mtime)),version='pinned revision' if name=='card' else 'retrieved live; not proof of historical version'))
  except Exception as e:evidence.append(dict(name=name,url=url,error=str(e)))
 dump('evidence.json',evidence)
 db=connect(C/'curation-v1/runs/1b-refined/index.sqlite');idx=connect(OLD/'results/recovered.sqlite')
 decisions=[]
 for source,track,decision,n,nb in db.execute('select source,track,decision,count(*),sum(clean_bytes) from docs group by source,track,decision'):
  status='EXCLUDED' if decision.startswith('exclude') or source=='python/cpython' else 'QUARANTINED' if decision!='keep' or source.startswith(('HuggingFaceFW/','HuggingFaceTB/')) else 'CONDITIONAL'
  decisions.append(dict(source=source,track=track,historical_decision=decision,documents=n,text_bytes=nb,status=status,scope='F2 BASE release; SFT not converted'))
 dump('source-decisions.json',decisions)
 rows=db.execute('select k,clean_sha,lang,domain,family,split,component,repairs from docs where source="wikimedia/wikipedia" and decision="keep" order by k').fetchall()
 ledger=[]
 for k,digest,lang,domain,family,split,component,repairs in rows:
  ledger.append(dict(key=k,sha256=digest,lang=lang,domain=domain,family=family,historical_split=split,component=component,repairs=json.loads(repairs),status='CONDITIONAL',conditions=['per-document external-content attribution and license exceptions unresolved','review intended training/output-distribution obligations; no automatic legal conclusion'],source_revision='b04c8d1ceb2f5cd4588862100d08de323dccfbaa'))
 with (ROOT/'results/wiki-rights-ledger.jsonl').open('w') as f:
  for r in ledger:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 # Freeze candidate order by content hash, independent of length/token count/results.
 # Historical test documents are NEVER opened. Preserve historical dev; no dev moved into train.
 candidates=sorted((r for r in ledger if r['historical_split'] in ['train','dev']),key=lambda r:sha(r['key'].encode()))
 cache=sqlite3.connect(ROOT/'counts.sqlite');cache.execute('create table if not exists counts(sha text primary key,fp text,n integer,ids blob)')
 targets=collections.Counter(); selected=[];groups={};seen=set();attr=[]
 limits={('train','en'):2500000,('train','es'):2500000,('dev','en'):100000,('dev','es'):100000}
 for r in candidates:
  st=(r['historical_split'],r['lang'])
  if targets[st]>=limits[st]:continue
  # Component assignment prevents exact/known-near-duplicate leakage. Skip conflicting groups.
  group=str(r['component']);split=st[0]
  if group in groups and groups[group]!=split:continue
  if r['sha256'] in seen:continue
  recordloc=idx.execute('select path,off from docs where view="curated1b" and k=?',(r['key'],)).fetchone();assert recordloc
  path,off=recordloc
  with open(path,'rb') as f:f.seek(off);record=json.loads(f.readline())
  text=record['text'];assert sha(text.encode())==r['sha256']
  prov=record['provenance'];fields=record['metadata'].get('source_fields',{})
  url=prov.get('source_url');assert url and url.startswith('https://'+r['lang']+'.wikipedia.org/wiki/')
  assert prov['revision']==r['source_revision']
  old=cache.execute('select fp,n,ids from counts where sha=?',(r['sha256'],)).fetchone()
  if old:assert old[0]==count_v3.FP;n=old[1]
  else:
   ids=tok.encode(text);assert ids==tok.encode(text) and tok.decode(ids)==text;n=len(ids)
   cache.execute('insert into counts values(?,?,?,?)',(r['sha256'],count_v3.FP,n,array.array('H',ids).tobytes()));cache.commit()
  # Bound article dominance; count remains exact even for rejected long articles.
  if n>30000:continue
  item=r|dict(path=path,offset=off,source_url=url,title=fields.get('title'),article_id=fields.get('id'),source_path=prov['path'],source_offset=prov['offset'],text_ids=n,effective_targets=n+1,text_bytes=len(text.encode()),characters=len(text),split=split)
  selected.append(item);seen.add(r['sha256']);groups[group]=split;targets[st]+=n+1
  attr.append(dict(key=r['key'],sha256=r['sha256'],title=fields.get('title'),credit='Wikipedia contributors',article_url=url,history_url=url+'?action=history',license='CC-BY-SA-3.0 for original textual content, subject to exceptions',license_url=urls['license'],snapshot_revision=prov['revision'],source_path=prov['path'],source_offset=prov['offset'],modifications=['mwparserfromhell plain-text extraction','historical curation; repairs='+json.dumps(r['repairs'])],status='CONDITIONAL',article_revision_id_available=False,external_attribution_review='PENDING'))
  if len(selected)%100==0:print('counted',len(selected),dict(targets),flush=True)
 dump('conditional-selection.json',dict(documents=selected,targets={f'{s}/{l}':n for (s,l),n in targets.items()},tokenizer=count_v3.FP,authorized_for_training=False,selection_policy='whole articles; deterministic key-hash order; <=30000 text IDs/article; historical train/dev; known dedup components isolated; historical test never opened',planning_train_target_cap=5000000,seconds=time.time()-started))
 with (ROOT/'results/attribution.jsonl').open('w') as f:
  for a in attr:f.write(json.dumps(a,ensure_ascii=False)+'\n')
 approved=json.loads((ROOT.parent/'corpus-recovery-f2/results/f2-selection.json').read_text())
 for r in approved['documents']:r['decision']='APPROVED'
 dump('approved-selection.json',approved)
 dump('summary.json',dict(wiki_current_keep_documents=len(ledger),wiki_status='CONDITIONAL',candidate_documents=len(selected),exact_candidate_targets={f'{s}/{l}':n for (s,l),n in targets.items()},approved_train_targets=approved['train_independent_targets'],approved_dev_targets=approved['dev_targets'],deficit=approved['deficit_targets'],ready=False,full_corpus_v3_counted=False,seconds=time.time()-started))
 print('DONE',targets,flush=True)
if __name__=='__main__':main()
