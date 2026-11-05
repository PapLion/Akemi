from pathlib import Path
import sys,json,hashlib,random,time,math,resource,ast,re,collections,os
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;PROJECT=BASE.parent
sys.path.insert(0,str(BASE/'foreground-binding'))
import harness as h
import torch
import torch.nn.functional as F
from vendor.cryo_historical import Baseline
D=PROJECT/'data/d0.1';OUT=ROOT/'results';torch.set_num_threads(1)
P={'seed':17,'updates_per_arm':128,'batch':2,'sequence':128,'stride':127,'cpu_threads':1,'precision':'FP32','max_seconds_per_arm':180,'max_total_training_targets_per_arm':32512,'lr':.003,'betas':[.9,.95],'weight_decay':.01,'clip':1,'arms':['foreground','baseline'],'checkpoint_policy':'fixed final128, evaluate0/32/64/96/128; no selection','prompts':['The command line interface','To specify an argument','def get_value('],'data_policy':'only complete Click train / Requests dev files already acquired; no OASST/Gutenberg/synthetic/test','memory':'Hielo OFF; Trapos OFF; full causal128 foreground; reset every window'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):
 p=OUT/(name+'.json');assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n')
def make(kind):
 random.seed(17);torch.manual_seed(17)
 return h.model('B',17) if kind=='foreground' else Baseline(v=8192,d=32,layers=2,dropout=0.)
def counts(m):
 cats=collections.Counter()
 for name,p in m.named_parameters():
  cat='embedding_tied_output' if name=='emb.weight' else 'attention' if any('.'+x+'.' in name for x in ['q','k','v','o']) else 'mlp' if any('.'+x+'.' in name for x in ['up','down']) else 'norms' if 'norm' in name or '.n1.' in name or '.n2.' in name else 'fast_refinement' if name.startswith('fast.') else 'inactive_memory'
  cats[cat]+=p.numel()
 return {'total':sum(p.numel() for p in m.parameters()),'trainable':sum(p.numel() for p in m.parameters() if p.requires_grad),'categories':dict(cats),'parameters':[{'name':n,'n':p.numel(),'trainable':p.requires_grad} for n,p in m.named_parameters()]}
def prepare():
 docs=[];inventory=collections.Counter();licenses={n:sha(D/'raw'/n) for n in ['click-LICENSE.rst','requests-LICENSE']}
 assert 'Redistribution and use' in (D/'raw/click-LICENSE.rst').read_text() and 'Apache License' in (D/'raw/requests-LICENSE').read_text()
 for line in (D/'accepted.jsonl').open():
  r=json.loads(line);inventory[(r['split'],r['lang'],r['domain'],r['provenance']['license'])]+=1
  if not r['source'].startswith(('click-','requests-')):continue
  assert r['split'] in ['train','dev'];assert r['provenance']['license'] in ['BSD-3-Clause','Apache-2.0']
  raw=PROJECT/'data'/r['provenance']['local_path'];assert sha(raw)==r['provenance']['sha256'];assert hashlib.sha256(r['text'].encode()).hexdigest()==r['text_sha256'];assert r['text']==raw.read_text()
  if r['domain']=='code':ast.parse(r['text'])
  ids=h.TOK.encode(r['text']);assert h.TOK.decode(ids)==r['text'];assert not re.search(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',r['text'])
  docs.append({k:r[k] for k in ['id','split','lang','domain','group','text_sha256','provenance']}|{'ids':[257]+ids+[258],'bytes':len(r['text'].encode()),'source_path':str(raw)})
 tr=[r for r in docs if r['split']=='train'];dv=[r for r in docs if r['split']=='dev'];assert len(tr)==3 and len(dv)==2
 assert not {r['group'] for r in tr}&{r['group'] for r in dv};assert not {r['text_sha256'] for r in tr}&{r['text_sha256'] for r in dv}
 def shingles(rr,n):
  out=set()
  for r in rr:
   w=re.findall(r'\w+',Path(r['source_path']).read_text().lower());out.update(tuple(w[i:i+n]) for i in range(len(w)-n+1))
  return out
 overlap={str(n):len(shingles(tr,n)&shingles(dv,n)) for n in [12,64]};assert overlap['64']==0
 put('data',docs);put('data-audit',{'licenses':licenses,'inventory':{str(k):v for k,v in inventory.items()},'source_manifest_sha':sha(D/'accepted.jsonl'),'normalized_word_shared_shingles':overlap,'train_dev_groups_disjoint':True,'code_ast_parse':True,'roundtrip_all_selected':True,'tokenizer_sha':sha(h.ARTIFACT),'tokenizer_fingerprint':h.FP,'excluded':'OASST unverified individual provenance/PII; PG jurisdiction; all synthetic and sealed evaluations'})
 return docs
def windows(docs,split):
 return [{'id':r['id'],'domain':r['domain'],'lang':r['lang'],'offset':i,'ids':r['ids'][i:i+128]} for r in docs if r['split']==split for i in range(0,len(r['ids'])-1,127)]
def batch(rr):
 T=max(len(r['ids']) for r in rr);x=torch.full((len(rr),T),256,dtype=torch.long);v=torch.zeros_like(x,dtype=torch.bool)
 for i,r in enumerate(rr):x[i,:len(r['ids'])]=torch.tensor(r['ids']);v[i,:len(r['ids'])]=True
 return x,v
def logits(m,kind,x):
 if kind=='baseline':return m(x)
 z,_=m.chunk_hidden(x,m.emb.weight.new_zeros(len(x),8,32),False)
 return F.linear(z,m.emb.weight)
def ce(m,kind,rr):
 x,v=batch(rr);y=logits(m,kind,x);mask=v[:,1:]&v[:,:-1];return F.cross_entropy(y[:,:-1][mask],x[:,1:][mask]),int(mask.sum())
def evaluate(m,kind,ww):
 totals=collections.defaultdict(lambda:[0.,0]);m.eval()
 with torch.no_grad():
  for r in ww:
   c,n=ce(m,kind,[r])
   for key in ['all',r['lang']+'/'+r['domain']]:totals[key][0]+=float(c)*n;totals[key][1]+=n
 return {k:{'nll':a/n,'ppl':math.exp(a/n),'targets':n} for k,(a,n) in totals.items()}
def sequence(ww,u):
 idx=list(range(len(ww)));random.Random(17).shuffle(idx);return [ww[idx[(u*2+j)%len(idx)]] for j in range(2)]
def update(m,o,kind,ww,u):
 rr=sequence(ww,u);o.zero_grad(set_to_none=True);start=time.perf_counter();c,n=ce(m,kind,rr);assert torch.isfinite(c);c.backward();gr={k:float(p.grad.norm()) for k,p in m.named_parameters() if p.grad is not None};assert all(math.isfinite(v) for v in gr.values());gn=float(torch.nn.utils.clip_grad_norm_(m.parameters(),1));o.step();return {'update':u+1,'ce':float(c.detach()),'targets':n,'input_ids':sum(len(r['ids']) for r in rr),'seconds':time.perf_counter()-start,'gradients':gr,'preclip_norm':gn}
def save(path,m,o,u,kind,docs):
 assert not path.exists();torch.save({'model':m.state_dict(),'optimizer':o.state_dict(),'cursor':u,'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'protocol':P,'kind':kind,'dataset_sha':h.digest(docs),'source_sha':sha(__file__),'tokenizer_sha':sha(h.ARTIFACT)},path)
def load(path,docs):
 c=torch.load(path,weights_only=True);assert c['protocol']==P and c['dataset_sha']==h.digest(docs) and c['source_sha']==sha(__file__) and c['tokenizer_sha']==sha(h.ARTIFACT);m=make(c['kind']);o=h.optimizer(m);m.load_state_dict(c['model']);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c

def contracts(docs):
 from collections.abc import Mapping
 def eq(a,b):
  if isinstance(a,torch.Tensor):return torch.equal(a,b)
  if isinstance(a,Mapping):return a.keys()==b.keys() and all(eq(a[k],b[k]) for k in a)
  if isinstance(a,(list,tuple)):return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
  return a==b
 ww=windows(docs,'train');result={}
 for kind in P['arms']:
  m=make(kind);o=h.optimizer(m);x,v=batch(ww[:2]);y=logits(m,kind,x);alt=x.clone();alt[:,64:]=(alt[:,64:]+13)%8192;assert torch.equal(y[:,:64],logits(m,kind,alt)[:,:64]);assert torch.allclose(y[:1],logits(m,kind,x[:1]),atol=1e-6,rtol=1e-5)
  a,n=ce(m,kind,ww[:2]);mask=v[:,1:]&v[:,:-1];b=F.cross_entropy(y[:,:-1][mask],x[:,1:][mask]);assert torch.equal(a,b) and n==int(mask.sum())
  assert {id(p) for p in m.parameters() if p.requires_grad}=={id(p) for g in o.param_groups for p in g['params']}
  for u in range(3):update(m,o,kind,ww,u)
  save(OUT/f'contract-{kind}.pt',m,o,3,kind,docs)
  for u in range(3,7):update(m,o,kind,ww,u)
  end=(m.state_dict(),o.state_dict(),torch.get_rng_state(),random.getstate());a,b,c=load(OUT/f'contract-{kind}.pt',docs)
  for u in range(c['cursor'],7):update(a,b,kind,ww,u)
  assert eq(end,(a.state_dict(),b.state_dict(),torch.get_rng_state(),random.getstate()));result[kind]={'causal':True,'isolation':True,'shift_mask':True,'optimizer_coverage':True,'resume_7_vs_3_plus_4_exact':True}
 put('contracts',result)
def main():
 assert not (ROOT/'PROTOCOL.json').exists();(ROOT/'PROTOCOL.json').write_text(json.dumps(P,indent=2)+'\n');docs=prepare();contracts(docs);ww=windows(docs,'train');dv=windows(docs,'dev');put('capacity',{k:counts(make(k)) for k in P['arms']});put('windows',{'train':ww,'dev':dv})
 # Evaluation and generation settings fixed before training; no sealed sets consulted.
 for kind in P['arms']:
  m=make(kind);o=h.optimizer(m);curve=[];metrics={'0':{'train':evaluate(m,kind,ww),'dev':evaluate(m,kind,dv)}};save(OUT/f'{kind}-0.pt',m,o,0,kind,docs);start=time.perf_counter();seen=0
  for u in range(P['updates_per_arm']):
   if time.perf_counter()-start>P['max_seconds_per_arm']:raise RuntimeError('CPU deadline: stop, do not expand')
   m.train();r=update(m,o,kind,ww,u);seen+=r['targets'];assert seen<=P['max_total_training_targets_per_arm'];r['targets_seen']=seen;curve.append(r)
   if (u+1)%32==0:metrics[str(u+1)]={'targets_seen':seen,'train':evaluate(m,kind,ww),'dev':evaluate(m,kind,dv)};print(kind,u+1,metrics[str(u+1)],flush=True)
  save(OUT/f'{kind}-128.pt',m,o,128,kind,docs)
  generations=[]
  with torch.no_grad():
   for prompt in P['prompts']:
    ids=[257]+h.TOK.encode(prompt);out=[]
    for _ in range(32):
     x=torch.tensor([ids[-128:]]);n=int(logits(m,kind,x)[0,-1].argmax());ids.append(n);out.append(n)
     if n==258:break
    generations.append({'prompt':prompt,'ids':out,'continuation':h.TOK.decode(out)})
  uses=collections.Counter((r['id'],r['offset']+i) for u in range(128) for r in sequence(ww,u) for i in range(1,len(r['ids'])))
  result={'kind':kind,'metrics':metrics,'curves':curve,'targets_seen':seen,'unique_target_positions_seen':len(uses),'repeat_fraction':1-len(uses)/seen,'train_available_targets':sum(len(r['ids'])-1 for r in ww),'unique_id_types_train':len({i for r in ww for i in r['ids']}),'seconds_updates':sum(r['seconds'] for r in curve),'targets_s':seen/sum(r['seconds'] for r in curve),'peak_process_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'generations':generations}
  put(kind,result)
if __name__=='__main__':main()
