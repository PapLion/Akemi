"""Non-destructive streaming recovery. Writes metadata only in this worktree."""
from pathlib import Path
import json,hashlib,sqlite3,collections,time,statistics,re,unicodedata
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'results'
C=Path('/PATH/TO/NEO_HOME/research/neo-architecture-recovery/chinchilla-corpus')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def put(n,r): (OUT/(n+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
def main():
 start=time.time();db=sqlite3.connect(OUT/'recovered.sqlite');db.execute('create table if not exists docs(view text,k text,sha text,path text,off integer,nbytes integer,chars integer,lang text,domain text,source text,family text,split text,rights text,primary key(view,k))');db.execute('create index if not exists content on docs(sha)');db.commit()
 views={'raw1b':C/'releases/growth-1b-v1-estimated-1000000000','curated500':C/'curation-v1/runs/500m-refined/release','curated1b':C/'curation-v1/runs/1b-refined/release'}
 report=json.loads((OUT/'integrity-progress.json').read_text()) if (OUT/'integrity-progress.json').exists() else {};receipts=[]
 for name,base in views.items():
  manifest=json.loads((base/'manifest.json').read_text());counts=collections.Counter();groups=collections.Counter();lengths=[];issues=collections.Counter();stored=0
  for track,t in manifest['tracks'].items():
   mp=base/t['manifest'];assert sha(mp)==t.get('sha256',t.get('manifest_sha256'));tm=json.loads(mp.read_text());receipts.append({'path':str(mp),'sha256':sha(mp),'status':'verified'})
   for s in tm['shards']:
    p=mp.parent/s['path']
    if name in report:
     assert sha(p)==s['sha256'] and p.stat().st_size==s['bytes'];receipts.append({'path':str(p),'sha256':s['sha256'],'stored_bytes':s['bytes'],'status':'verified'});continue
    h=hashlib.sha256();off=0;n=0
    with p.open('rb') as f:
     for line in f:
      h.update(line);stored+=len(line)
      try:r=json.loads(line)
      except (ValueError,UnicodeError):issues['corrupt_json']+=1;off+=len(line);continue
      n+=1;text=r.get('text','');b=text.encode();digest=hashlib.sha256(b).hexdigest();prov=r.get('provenance',{});cur=r.get('curation',{})
      issues['empty']+=not bool(text.strip());issues['text_sha_mismatch']+=digest!=r.get('text_sha256');issues['byte_mismatch']+=len(b)!=r.get('utf8_bytes');issues['missing_required']+=not all(k in r for k in ['id','text','family','language','domain','provenance','key','split','track'])
      issues['email_pattern_documents']+=bool(re.search(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',text));issues['private_key_or_token_pattern_documents']+=bool(re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|\b(?:ghp|sk_live)_[A-Za-z0-9]{20,}',text))
      counts[track]+=1;counts[track+'_text_bytes']+=len(b);lang=r.get('language','unknown');source=prov.get('source',prov.get('repo','unknown'));domain=r.get('domain','unknown');groups[(track,source,lang,domain,r.get('split','unknown'))]+=1
      if track in ['BASE_LM','BASE_LM_CLEAN']:
       lengths.append(len(b));db.execute('insert or replace into docs values(?,?,?,?,?,?,?,?,?,?,?,?,?)',(name,r['key'],digest,str(p),off,len(b),len(text),lang,domain,source,r['family'],r['split'],str(prov.get('rights_status',''))))
      off+=len(line)
    actual=h.hexdigest();assert actual==s['sha256'],str(p);assert p.stat().st_size==s['bytes'];receipts.append({'path':str(p),'sha256':actual,'stored_bytes':p.stat().st_size,'records':n,'status':'verified'})
    db.commit()
   print(name,track,counts[track],flush=True)
  if name in report:continue
  lengths.sort();report[name]={'manifest':str(base/'manifest.json'),'manifest_sha256':sha(base/'manifest.json'),'counts':dict(counts),'stored_jsonl_bytes':stored,'issues':dict(issues),'groups':[dict(zip(['track','source','lang','domain','split'],k),documents=v) for k,v in sorted(groups.items())],'text_byte_quantiles':{str(q):lengths[min(len(lengths)-1,int(q*(len(lengths)-1)))] for q in [0,.25,.5,.75,.9,.99,1]},'base_exact_duplicate_excess':db.execute('select count(*)-count(distinct sha) from docs where view=?',(name,)).fetchone()[0]}
  put('integrity-progress',report)
 relations={}
 for name in ['curated500','curated1b']:
  relations[name]={'keys_without_master':db.execute('select count(*) from docs c where c.view=? and not exists(select 1 from docs r where r.view="raw1b" and r.k=c.k)',(name,)).fetchone()[0], 'same_key_changed_text':db.execute('select count(*) from docs c join docs r on r.k=c.k and r.view="raw1b" where c.view=? and c.sha!=r.sha',(name,)).fetchone()[0]}
 relations['500_not_in_1b_keys']=db.execute('select count(*) from docs c where c.view="curated500" and not exists(select 1 from docs r where r.view="curated1b" and r.k=c.k)').fetchone()[0]
 put('integrity',{'views':report,'relations':relations,'seconds':time.time()-start});put('shard-receipts',receipts)
 # Reuse existing bounded near-duplicate analysis, never rerun O(N²).
 audits={}
 for name in ['500m-refined','1b-refined']:
  p=C/'curation-v1/runs'/name/'index.sqlite';con=sqlite3.connect(f'file:{p}?mode=ro',uri=True);con.execute('begin')
  audits[name]={'quick_check':con.execute('pragma quick_check').fetchone()[0],'decisions':con.execute('select decision,rights,count(*),sum(clean_bytes) from docs group by 1,2').fetchall(),'edges':con.execute('select count(*) from edges').fetchone()[0],'quality_reasons':con.execute('select reason,count(*) from docs where decision!="keep" group by reason').fetchall(),'documented_files':con.execute('select k,path,off,length,family,split,clean_sha,clean_bytes,decision from docs where rights="documented_file"').fetchall()};con.close()
 put('curation-audits',audits);db.close()
if __name__=='__main__':main()
