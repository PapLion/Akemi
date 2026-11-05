"""Addressable V1.2: frozen architecture, response-only paired data contrast."""
import sys,json,copy,random,time,hashlib,datetime,collections,resource
from pathlib import Path
import torch
import torch.nn.functional as F
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'addressable-consolidation'))
import runner_v11 as V
D=V.D;A=V.A;torch.set_num_threads(1)
O=ROOT/'results';O.mkdir(exist_ok=True)
PROTOCOL={'version':'stability-v1.2','seeds':[17,29,43],'updates':300,'batch':8,'lr':.003,'betas':[.9,.95],'weight_decay':.01,'clip':1.,'objective':'response CE ONLY, both arms; prior V1.1 initial auxiliary removed from BOTH','selection':'final update300 only','correction_fraction':.5,'query_corrected_fraction_given_correction':.5,'reserve_pair':['A','C'],'train_C_initial':[[0,1],[2,3],[4,5]],'train_C_correction':[6,8,10],'train_C_distractor':'25% third-entity writes at record11; never overwrites queried pair','triage':{'corrected':.95,'preserved':.95,'joint':.90,'swap':.95,'obsolete_cf':.95,'current_cf':.95,'novel_joint':.90,'layout_joint':.90,'max_drop_vs_B':.05},'sealed':'never opened; no confirmatory evaluation','precision':'CPU FP32 single thread','initialization':'V1.1 seed-specific historical warmstart; identical B/C; auxiliary decoder retained frozen, no inference or loss use','comparison':'B original V1.1 treatment DISTRIBUTION, not original combined objective; C changes only data distribution','capacity':'architecture unchanged; optimizer contains all and only trainable model parameters; decoder excluded identically'}
def dump(n,x):(O/(n+'.json')).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def pair(q,e):return tuple(sorted((q,e)))
def c_row(base,k):
 r=copy.deepcopy(base);choices=[e for e in 'ABCDE' if e!=r['q'] and pair(e,r['q'])!=('A','C')];new=choices[k%len(choices)];old=r['other']
 ops=[[op,new if e==old else e,v] for op,e,v in r['ops']];r['other']=new
 if r['affected']==old:r['affected']=new
 r=D.recode(r,ops,'Ctrain');initial=[(0,1),(2,3),(4,5)][(k//12)%3];corr=[6,8,10][(k//36)%3]
 third=next(e for e in 'ABCDE' if e not in [r['q'],r['other']])
 return D.move(r,initial,corr,(11,third,(k//108)%4) if k%4==0 else None)
def schedule(seed,arm):
 rng=random.Random(seed);pool=D.treatment();rows=[];order=[]
 for step in range(300):
  for slot in range(8):
   ix=rng.randrange(160);variant=(step*8+slot)%12;r=pool[ix*12+variant]
   if arm=='C':r=c_row(r,step*8+slot)
   rows.append(copy.deepcopy(r));order.append([ix,variant])
 return rows,order

def map_pair(r,other):
 z=copy.deepcopy(r);old=z['other'];z['other']=other
 if z['affected']==old:z['affected']=other
 return D.recode(z,[[op,other if e==old else e,v] for op,e,v in z['ops']],'independent')
def evaluation():
 corr=[r for r in D.treatment() if r['kind']=='correct'];form=D.dev_sets()['formation']
 # Held-out unordered pair A,C; both query directions. No training C uses that pair.
 novel=[map_pair(r,('C' if r['q']=='A' else 'A')) for r in corr if r['q'] in 'AC']
 formation=[map_pair(r,('C' if r['q']=='A' else 'A')) for r in form if r['q'] in 'AC']
 layout=[D.move(r,(6,7),11) for r in corr]
 alternate=[D.move(r,(1,4),9) for r in corr]
 distractor=[]
 for r in novel:
  third=next(e for e in 'ABCDE' if e not in [r['q'],r['other']]);distractor.append(D.move(r,(6,7),10,(8,third,2)))
 return {'held_pair':novel,'held_formation':formation,'new_layout':layout,'alternate':alternate,'held_distractor':distractor}
def setup(seed):
 m,d,_,rng=V.setup(seed);d.requires_grad_(False)
 o=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 return m,d,o,rng
def update(m,o,rows):
 o.zero_grad(set_to_none=True);x=torch.tensor([r['ids'] for r in rows]);y=torch.tensor([r['label'] for r in rows]);logits=m(x);loss=F.cross_entropy(logits[:,-1],y);loss.backward()
 grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None}
 assert torch.isfinite(loss) and all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
 norm=float(torch.nn.utils.clip_grad_norm_(m.parameters(),1));o.step()
 return {'ce':float(loss.detach()),'accuracy':float((logits[:,-1].argmax(-1)==y).float().mean()),'gradients':grads,'clip_input_norm':norm}
def save(path,m,d,o,seed,arm,step,rows,order):
 torch.save({'model':m.state_dict(),'decoder':d.state_dict(),'optimizer':o.state_dict(),'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'cursor':step*8,'step':step,'microstep':0,'accumulation':1,'scheduler':None,'seed':seed,'arm':arm,'dataset_sha':sha(rows),'order_sha':sha(order),'protocol':PROTOCOL,'architecture_sha':hashlib.sha256((ROOT.parent/'addressable/address_model.py').read_bytes()).hexdigest()},path)
def restore(path,rows,order):
 s=torch.load(path,weights_only=True,map_location='cpu');assert s['protocol']==PROTOCOL and s['dataset_sha']==sha(rows) and s['order_sha']==sha(order) and s['cursor']==s['step']*8
 m,d,o,_=setup(s['seed']);assert s['architecture_sha']==hashlib.sha256((ROOT.parent/'addressable/address_model.py').read_bytes()).hexdigest();m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True);o.load_state_dict(s['optimizer']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng']);return m,d,o,s

def predict(m,rows,trace=False):
 pp=[];states=[]
 with torch.no_grad():
  for i in range(0,len(rows),32):
   batch=rows[i:i+32];x=torch.tensor([r['ids'] for r in batch]);logits,tr=m(x,trace=True);pred=logits[:,-1].argmax(-1).tolist()
   for j,(r,p) in enumerate(zip(batch,pred)):
    pp.append(dict(id=r['id'],q=r['q'],other=r['other'],affected=r['affected'],kind=r['kind'],prediction=p,label=r['label']))
    if trace:states.append(torch.stack([tr[k]['memory'][j].cpu() for k in [r['stages'][0],r['stages'][1],6]]))
 return pp,states

def evaluate(m,tag):
 report={};allpred={};sets=evaluation()
 for family,rows in sets.items():
  base,states=predict(m,rows,True);other,_=predict(m,[D.query_other(r) for r in rows]);acc=lambda pp:sum(r['prediction']==r['label'] for r in pp)/len(pp)
  met={'normal':acc(base),'joint':sum(a['prediction']==a['label'] and b['prediction']==b['label'] for a,b in zip(base,other))/len(rows),'n':len(rows)}
  for name,condition in [('corrected',lambda r:r['q']==r['affected']),('preserved',lambda r:r['q']!=r['affected'])]:
   inds=[i for i,r in enumerate(rows) if r['kind']=='correct' and condition(r)]
   if inds:met[name]=sum(base[i]['prediction']==base[i]['label'] for i in inds)/len(inds)
  met['pair_accuracy']={str(p):sum(base[i]['prediction']==base[i]['label'] for i,r in enumerate(rows) if pair(r['q'],r['other'])==p)/sum(pair(r['q'],r['other'])==p for r in rows) for p in sorted({pair(r['q'],r['other']) for r in rows})}
  cf={}
  for kind in (['obsolete','current'] if family!='held_formation' else ['swap']):
   altered,_=predict(m,[D.transform(r,kind) for r in rows]);cf[kind]={'joint_correct':sum(a['prediction']==a['label'] and b['prediction']==b['label'] for a,b in zip(base,altered))/len(rows),'prediction_invariance':sum(a['prediction']==b['prediction'] for a,b in zip(base,altered))/len(rows)};allpred[family+'-'+kind]=altered
  met['cf']=cf;report[family]=met;allpred[family]=base;allpred[family+'-other-query']=other
  torch.save({'states':torch.stack(states),'ids':[r['id'] for r in rows]},O/(tag+'-'+family+'-states.pt'))
 # Compatible states with same entities/layout, changed current query value.
 rows=sets['held_formation'];pred={k:[] for k in ['normal','reset','swap']};partner_labels=[]
 for r in rows:
  rr=D.transform(r,'current');partner_labels.append(rr['label']);x=torch.tensor([r['ids'],rr['ids']])
  with torch.no_grad():
   for mode in pred:pred[mode].append(int(m(x,intervention=None if mode=='normal' else mode)[0,-1].argmax()))
 report['interventions']={k:{'accuracy':sum(p==r['label'] for p,r in zip(pp,rows))/len(rows),'follows_partner':sum(p==y for p,y in zip(pp,partner_labels))/len(rows)} for k,pp in pred.items()}
 keys=F.normalize(m.core.address(m.core.emb(torch.tensor([ord(e) for e in 'ABCDE']))),dim=-1).detach();report['key_gram']=(keys@keys.T).tolist()
 dump(tag+'-predictions',allpred);dump(tag+'-metrics',report);return report

def gate(c,b):
 checks={}
 for family in ['held_pair','new_layout','alternate','held_distractor']:
  for key,threshold in [('corrected',.95),('preserved',.95),('joint',.9)]:checks[family+'-'+key]=c[family][key]>=threshold
  for key in ['obsolete','current']:checks[family+'-'+key+'-cf']=c[family]['cf'][key]['joint_correct']>=.95
 for family in ['held_formation','new_layout','alternate']:
  checks[family+'-no-degradation']=c[family]['joint']>=b[family]['joint']-.05
 checks['novel_joint']=c['held_formation']['joint']>=.9
 checks['swap']=c['held_formation']['cf']['swap']['joint_correct']>=.95
 return {'passed':all(checks.values()),'checks':checks}

def frequencies(rows):
 counts=collections.Counter();trans=collections.Counter();heur=collections.Counter()
 for r in rows:
  role='corrected' if r['kind']=='correct' and r['affected']==r['q'] else ('preserved' if r['kind']=='correct' else 'no_correction')
  counts[(r['q'],r['other'],role,r['label']-48)]+=1
  if r['kind']=='correct':trans[(r['affected'],D.oracle(r['ops'][:r['event']],r['affected']),D.oracle(r['ops'][:r['event']+1],r['affected']))]+=1
  writes=[(e,int(v)) for op,e,v in r['ops'] if op in '=!'];first=next(v for e,v in writes if e==r['q']);last=writes[-1][1];entity=next(v for e,v in reversed(writes) if e==r['q'])
  for k,p in [('first_query',first),('last_global',last),('last_query',entity),('presence_constant',0)]:heur[k]+=p==r['label']-48
 return {'records':len(rows),'bytes':sum(len(bytes(r['ids'])) for r in rows),'input_ids':len(rows)*64,'answer_targets':len(rows),'auxiliary_targets':0,'unique_programs':len({tuple(r['ids']) for r in rows}),'conditional_targets':[{'query':q,'other':e,'role':role,'value':v,'n':n} for (q,e,role,v),n in sorted(counts.items())],'transitions':[{'entity':e,'old':a,'new':b,'n':n} for (e,a,b),n in sorted(trans.items())],'heuristics':{k:n/len(rows) for k,n in heur.items()}}

def preflight():
 assert not (O/'FREEZE.json').exists();report={};sets=evaluation()
 for seed in [17,29,43]:
  br,bo=schedule(seed,'B');cr,co=schedule(seed,'C');assert bo==co
  for arm,rows in [('B',br),('C',cr)]:
   D.verify(rows);assert len(rows)==2400 and sum(r['kind']=='correct' for r in rows)==1200
   assert sum(r['kind']=='correct' and r['q']==r['affected'] for r in rows)==600
   if arm=='C':assert all(pair(r['q'],r['other'])!=('A','C') for r in rows)
   train={tuple(r['ids']) for r in rows};overlap={name:sum(tuple(r['ids']) in train for r in rr) for name,rr in sets.items()};assert not any(overlap.values()),overlap
   dump(f'{arm}-{seed}-data',rows);dump(f'{arm}-{seed}-frequencies',dict(frequencies(rows),dev_overlap=overlap));dump(f'{arm}-{seed}-order',bo)
  m,d,o,_=setup(seed);n,e,p,_=setup(seed);assert A.I.equal(m.state_dict(),n.state_dict()) and A.I.equal(d.state_dict(),e.state_dict())
  if seed!=17:continue
  pars=[p for p in m.parameters() if p.requires_grad];opt=[p for g in o.param_groups for p in g['params']];assert len(opt)==len(set(map(id,opt)))==len(pars) and set(map(id,opt))==set(map(id,pars))
  rows=cr[:8];x=torch.tensor([r['ids'] for r in rows])
  for mode in [False,True]:
   m.train(mode);y=m(x)
   for cut in [1,4,8,16,24,32,40,48,60]:
    xx=x.clone();xx[:,cut:]=120;assert torch.equal(y[:,:cut],m(xx)[:,:cut])
   assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-5,rtol=1e-5)
   joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1);assert torch.allclose(m(joined,doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
   valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127;assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
  m.eval();update(m,o,rows)
  for key in ['core.address.weight','core.event_value.weight','core.address_out.weight']:assert dict(m.named_parameters())[key].grad.norm()>0
  for arm,rr,order in [('B',br,bo),('C',cr,co)]:
   m,d,o,_=setup(17)
   logs=[update(m,o,rr[i*8:i*8+8]) for i in range(4)];save(O/(arm+'-resume.pt'),m,d,o,17,arm,4,rr,order)
   tail=[update(m,o,rr[i*8:i*8+8]) for i in range(4,10)];end=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),torch.get_rng_state(),random.getstate()))
   n,e,p,s=restore(O/(arm+'-resume.pt'),rr,order);tail2=[update(n,p,rr[i*8:i*8+8]) for i in range(s['step'],10)]
   assert tail==tail2 and A.I.equal(end,(n.state_dict(),e.state_dict(),p.state_dict(),torch.get_rng_state(),random.getstate()))
  report={'passed':True,'causality_train_eval':True,'mask_and_reset':True,'initial_identity':True,'optimizer_exact_coverage':True,'response_gradients_write_read':True,'resume_continuous10_vs4plus6_exact':True,'no_auxiliary_decoder_gradients':all(p.grad is None for p in d.parameters())}
 for name,rr in sets.items():D.verify(rr);dump('eval-'+name,rr)
 dump('preflight',report);(ROOT/'protocol.json').write_text(json.dumps(PROTOCOL,indent=2)+'\n')
 dump('FREEZE',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'protocol.json',ROOT.parent/'addressable/address_model.py']},'datasets':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('*-data.json'))},'status':'BEFORE MAIN TRAINING'})
 print('PREFLIGHT PASS',flush=True)

def train(arm,seed):
 rows,order=schedule(seed,arm);tag=f'{arm}-{seed}';assert not (O/(tag+'.pt')).exists();m,d,o,_=setup(seed);save(O/(tag+'-initial.pt'),m,d,o,seed,arm,0,rows,order);logs=[];start=time.monotonic()
 for i in range(300):
  logs.append(dict(step=i+1,**update(m,o,rows[i*8:i*8+8])))
  if (i+1)%100==0:print(tag,i+1,logs[-1]['ce'],flush=True)
 save(O/(tag+'.pt'),m,d,o,seed,arm,300,rows,order);dump(tag+'-curves',logs);dump(tag+'-cost',{'seconds':time.monotonic()-start,'updates':300,'targets':2400,'input_ids':153600,'parameters':sum(p.numel() for p in m.parameters()),'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
 met=evaluate(m,tag);fit,_=predict(m,rows);dump(tag+'-fit',{'normal_accuracy':sum(r['prediction']==r['label'] for r in fit)/len(fit)});return met

def main():
 preflight();b=train('B',17);c=train('C',17);g=gate(c,b);dump('primary-gate',g);print('GATE',g,flush=True)
 if g['passed']:
  for seed in [29,43]:
   b=train('B',seed);c=train('C',seed);dump(f'confirmation-{seed}-gate',gate(c,b))
 print('DONE; sealed evaluations=0',flush=True)
if __name__=='__main__':main()
