"""Resumable content-addressed exact V3 certificates, no text/IDs stored."""
from pathlib import Path
import sys,json,hashlib,sqlite3,random,collections,time,math,statistics,argparse
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent.parent;C=PROJECT/'chinchilla-corpus';V3=PROJECT/'neotoken-v3'
sys.path[:0]=[str(V3),str(V3/'.venv/lib/python3.11/site-packages')]
from core import NeoTokenizer
FP='813e5d1b255d832728941a570052afb59b1ad1be13100ae6d6698cd1d95f127b';ART=V3/'artifacts/bpe-8192.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load():return NeoTokenizer.load(ART,expected_fingerprint=FP)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--sample-per-stratum',type=int,default=24);args=ap.parse_args();tok=load();start=time.monotonic();out=ROOT/'results'
 assert sha(ART)=='8489cd9a98fb4a7339fe802be74621774f2ee68b465cfb0b16846a07fe99a156'
 checks=[]
 for s in ['Español: pingüino, ¿qué ocurrió?','English café — code: x = 3\n','未知🙂\x00\t\n']:
  ids=tok.encode(s);assert ids==tok.encode(s) and tok.decode(ids)==s;checks.append({'bytes':len(s.encode()),'characters':len(s),'ids':len(ids)})
 cache=sqlite3.connect(out/'v3-certificates.sqlite');cache.execute('create table if not exists certificates(sha text primary key,tokenizer text,ids integer,bytes integer,chars integer,roundtrip integer)')
 def count(r,text):
  digest=hashlib.sha256(text.encode()).hexdigest();assert digest==r['sha'];row=cache.execute('select ids from certificates where sha=? and tokenizer=?',(digest,FP)).fetchone()
  if row:n=row[0]
  else:
   ids=tok.encode(text);assert tok.decode(ids)==text and ids==tok.encode(text);n=len(ids);cache.execute('insert or replace into certificates values(?,?,?,?,?,1)',(digest,FP,n,len(text.encode()),len(text)));cache.commit()
  return r|{'text_bytes':len(text.encode()),'characters':len(text),'v3_text_ids':n,'effective_targets_bos_text_eos':n+1,'tokenizer_fingerprint':FP}
 # Rights-approved local D0.1 texts only. No sealed contents read.
 selected=[];license_hashes={n:sha(PROJECT/'data/d0.1/raw'/n) for n in ['click-LICENSE.rst','requests-LICENSE']}
 for l in (PROJECT/'data/d0.1/accepted.jsonl').open():
  r=json.loads(l)
  if not r['source'].startswith(('click-','requests-')):continue
  p=PROJECT/'data'/r['provenance']['local_path'];assert sha(p)==r['provenance']['sha256'];text=p.read_text();assert text==r['text'];assert hashlib.sha256(text.encode()).hexdigest()==r['text_sha256']
  selected.append(count({'id':r['id'],'sha':r['text_sha256'],'path':str(p),'split':r['split'],'family':r['group'],'lang':r['lang'],'domain':r['domain'],'license':r['provenance']['license'],'decision':'APROBADO','source':'D0.1'},text))
 assert not {r['sha'] for r in selected if r['split']=='train'}&{r['sha'] for r in selected if r['split']=='dev'}
 # Stratified reservoir fixed BEFORE encoding; full strata sampled uniformly, no size-based stopping bias.
 p=C/'curation-v1/runs/1b-refined/index.sqlite';db=sqlite3.connect(f'file:{p}?mode=ro',uri=True);db.execute('begin');rng=random.Random(17005);samples=collections.defaultdict(list);N=collections.Counter()
 for k,path,off,length,digest,lang,domain,source in db.execute('select k,path,off,length,sha,lang,domain,source from docs where decision="keep" order by i'):
  st=(source,lang,domain);N[st]+=1;row={'key':k,'path':str(C/'releases/growth-1b-v1-estimated-1000000000'/path),'offset':off,'length':length,'sha':digest,'lang':lang,'domain':domain,'source':source}
  if len(samples[st])<args.sample_per_stratum:samples[st].append(row)
  else:
   j=rng.randrange(N[st])
   if j<args.sample_per_stratum:samples[st][j]=row
 db.close();sampled=[];pending=[]
 for st,rows in sorted(samples.items()):
  for row in rows:
   # CPython was reserved as D0 test family: do not open its content in this study.
   if row['source']=='python/cpython':pending.append(row|{'reason':'historical test-family reservation'});continue
   if time.monotonic()-start>args.seconds:pending.append(row|{'reason':'bounded count deadline; rerun same command to reuse cache'});continue
   with Path(row['path']).open('rb') as f:f.seek(row['offset']);record=json.loads(f.read(row['length']))
   sampled.append(count(row,record['text']))
 result=[]
 for st,n in sorted(N.items()):
  ss=[r for r in sampled if (r['source'],r['lang'],r['domain'])==st];vals=[r['v3_text_ids'] for r in ss];complete=len(ss)==len(samples[st]);a={'source':st[0],'lang':st[1],'domain':st[2],'population_documents':n,'sample_documents':len(vals),'sample_plan_complete':complete,'exact_sample_ids':sum(vals),'exact_sample_bytes':sum(r['text_bytes'] for r in ss)}
  if complete and vals:
   mean=statistics.mean(vals);se=math.sqrt((1-len(vals)/n)*statistics.variance(vals)/len(vals)) if len(vals)>1 else 0;a.update(estimated_population_ids=n*mean,normal_95_halfwidth=n*1.96*se,warning='Exploratory stratified normal interval: small samples/heavy tails; not a certified total')
  result.append(a)
 report={'artifact_sha256':sha(ART),'fingerprint':FP,'roundtrip_determinism':checks,'special_ids':{'PAD':256,'BOS':257,'EOS':258},'selected':selected,'license_evidence_hashes':license_hashes,'strata':result,'sample':sampled,'pending':pending,'seconds':time.monotonic()-start,'all_sample_strata_complete':not pending,'cache_unique_documents':cache.execute('select count(*),sum(ids) from certificates').fetchone(),'targets_definition':'[BOS]+text+[EOS]; n_text+1 shifted targets; stride=context-1 masks repeated input seam, no cross-document targets','not_counted':'no exhaustive V3 total; CPython historical test family contents unopened; no SFT counted'}
 (out/'v3-counts.json').write_text(json.dumps(report,indent=2)+'\n');print('V3',len(sampled),'sample documents;',len(pending),'pending;',sum(r['v3_text_ids'] for r in selected),'selected IDs',flush=True)
if __name__=='__main__':main()
