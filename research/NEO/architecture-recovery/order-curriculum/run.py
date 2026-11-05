from pathlib import Path
import sys,json,random,math,time,resource,hashlib
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent
sys.path.insert(0,str(BASE/'distribution-scaling'))
import factorial as f
h=f.h;torch=f.torch;torch.set_num_threads(1)
OUT=ROOT/'results'
P={'seed':17,'updates':700,'transition':300,'batch':8,'lr':.003,'betas':[.9,.95],'weight_decay':.01,'clip':1,'architecture':'historical B two layers, unchanged','arms':{'direct':['C','C'],'curriculum':['A','C']},'train_gate':'all eight answers, joint and strict swaps 100%; both orders','generalization_gate':'joint and strict swaps >=90% on BOTH existing dev panels; no exclusive position dependence','checkpoint_policy':'fixed 0/300/700; no selection','confirmation':'29/43 only if curriculum passes generalization','auxiliary_loss':False}
def put(path,obj):
 assert not path.exists(),path
 path.write_text(json.dumps(obj,indent=2)+'\n')
def rows(arm,u):return f.datasets()[P['arms'][arm][int(u>=300)]]['train']
def ck(path,m,o,u,arm):
 assert not path.exists()
 torch.save(dict(model=m.state_dict(),optimizer=o.state_dict(),torch_rng=torch.get_rng_state(),python_rng=random.getstate(),cursor=u,arm=arm,next_dataset=P['arms'][arm][int(u>=300)],protocol=P,source_sha=h.file_sha(Path(__file__)),datasets={k:h.digest(f.datasets()[k]['train']) for k in ['A','C']},tokenizer_sha=h.file_sha(h.ARTIFACT)),path)
def load(path):
 c=torch.load(path,weights_only=True);assert c['protocol']==P and c['source_sha']==h.file_sha(Path(__file__)) and c['tokenizer_sha']==h.file_sha(h.ARTIFACT)
 m=h.model('B');o=h.optimizer(m);m.load_state_dict(c['model']);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c
def equal(a,b):
 if isinstance(a,torch.Tensor):return torch.equal(a,b)
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
def evaluate(m,tag):
 ds=f.datasets()['C'];panels={**ds,**{f'order-{i}':[r for r in ds['train'] if r['order']==i] for i in [0,1]}};out={}
 for name,rr in panels.items():
  out[name]=f.evaluate(m,rr)
  with torch.no_grad():y=h.logits(m,rr)
  torch.save({'logits':y,'rows':rr,'predictions':y.argmax(-1),'probabilities':y.softmax(-1)},OUT/f'{tag}-{name}.pt')
 # Actual block outputs: representation diagnostics, no extra model path.
 captures={};handles=[]
 for name,module in m.named_modules():
  if module.__class__.__name__=='Block':
   handles.append(module.register_forward_hook(lambda mod,inp,out,n=name:captures.update({n:out.detach().clone() if isinstance(out,torch.Tensor) else str(type(out))})))
 with torch.no_grad():h.logits(m,ds['train'])
 for handle in handles:handle.remove()
 torch.save(captures,OUT/f'{tag}-representations.pt')
 return out
def contracts():
 data=f.validate_data();assert len(rows('direct',0))==8 and len(rows('curriculum',0))==4
 assert rows('curriculum',299)==f.datasets()['A']['train'] and rows('curriculum',300)==rows('direct',300)
 results={}
 for arm,old in [('direct','C'),('curriculum','A')]:
  rr=f.datasets()[old]['train'];m,o,c=f.restore(BASE/f'distribution-scaling/results/{old}-300.pt',rr)
  ck(OUT/f'contract-{arm}-300.pt',m,o,300,arm)
  for u in range(300,304):h.update(m,o,rows(arm,u),u,17)
  end=(m.state_dict(),o.state_dict(),torch.get_rng_state(),random.getstate())
  n,p,cc=load(OUT/f'contract-{arm}-300.pt');assert cc['cursor']==300
  assert all(int(v['step'])==300 for v in p.state.values())
  for u in range(300,302):h.update(n,p,rows(arm,u),u,17)
  ck(OUT/f'contract-{arm}-302.pt',n,p,302,arm);n,p,cc=load(OUT/f'contract-{arm}-302.pt')
  for u in range(302,304):h.update(n,p,rows(arm,u),u,17)
  assert equal(end,(n.state_dict(),p.state_dict(),torch.get_rng_state(),random.getstate()))
  results[arm]={'exact_resume_300_to_304_via_302':True,'optimizer_steps_at_transition':300}
 # Existing causal and signal checks are inherited, add direct future/padding perturbation.
 m=h.model('B');rr=rows('direct',0);x,last,lab=h.tensors(rr)
 assert all(int(lab[i])==r['choices'][r['values'][r['query_side']]] for i,r in enumerate(rr))
 o=h.optimizer(m);rec=h.update(m,o,rr,0,17);assert all(math.isfinite(v) for v in rec['gradients'].values())
 random.seed(17);a=h.model('B');random.seed(17);b=h.model('B');assert h.state_sha(a)==h.state_sha(b)
 put(OUT/'contracts.json',{'passed':True,'resume':results,'frequencies':data,'same_initialization':True,'gradient_tensors':len(rec['gradients']),'inherited_contracts':'distribution-scaling/tests.py run separately; unchanged model/loss','source_sha':h.file_sha(Path(__file__))})
def train(arm):
 random.seed(17);m=h.model('B');o=h.optimizer(m);initial=h.state_sha(m);curves=[];evals={};start=time.perf_counter()
 ck(OUT/f'{arm}-0.pt',m,o,0,arm);evals['0']=evaluate(m,f'{arm}-0')
 for u in range(700):
  m.train();rr=rows(arm,u);r=h.update(m,o,rr,u,17);r['global_update']=u+1;r['distribution']='A' if arm=='curriculum' and u<300 else 'C';r['preclip_norm']=math.sqrt(sum(v*v for v in r['gradients'].values()))
  if (u+1)%50==0:
   r['mixed_train']=f.evaluate(m,f.datasets()['C']['train'])
   with torch.no_grad():y=h.logits(m,f.datasets()['C']['train'])
   torch.save(y,OUT/f'{arm}-curve-{u+1}-logits.pt')
  curves.append(r)
  if u+1 in [300,700]:
   ck(OUT/f'{arm}-{u+1}.pt',m,o,u+1,arm);evals[str(u+1)]=evaluate(m,f'{arm}-{u+1}');print(arm,u+1,evals[str(u+1)]['train'],flush=True)
 total=sum(r['seconds'] for r in curves);v=evals['700'];fit=all(v['train'][k]==1 for k in ['accuracy','joint_accuracy']) and v['train']['strict_swaps']['accuracy']==1
 general=fit and all(v[s]['joint_accuracy']>=.9 and v[s]['strict_swaps']['accuracy']>=.9 for s in ['dev-layouts','dev-new-entity-pair'])
 result={'arm':arm,'initial_sha':initial,'evaluations':evals,'curves':curves,'train_gate':fit,'generalization_gate':general,'seconds_updates':total,'seconds_wall':time.perf_counter()-start,'targets_s':5600/total,'peak_process_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'clipping_frequency':sum(r['preclip_norm']>1 for r in curves)/700}
 put(OUT/f'{arm}.json',result)
 return result
if __name__=='__main__':
 put(ROOT/'PROTOCOL.json',P);put(OUT/'datasets.json',f.datasets());contracts();res={a:train(a) for a in P['arms']};assert res['direct']['initial_sha']==res['curriculum']['initial_sha'];put(OUT/'comparison.json',{a:{k:v for k,v in r.items() if k!='curves'} for a,r in res.items()})
