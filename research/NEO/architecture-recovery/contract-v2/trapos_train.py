import json,copy,hashlib,time,random,datetime,resource,collections
from pathlib import Path
import torch
import torch.nn.functional as F
import trapos_model as M
D=M.D;R=D.R;O=R/'results';O.mkdir(exist_ok=True);torch.set_num_threads(1)
PROTOCOL={'name':'trapos-contract-v2','base':'23cb2d7; Addressable V1.2 C weights per seed','updates':300,'batch':8,'seeds':[17,29,43],'lr':.003,'betas':[.9,.95],'decay':.01,'clip':1.,'precision':'CPU FP32 one thread','loss':'answer CE + C only .1 acceptance BCE; hard-forward STE unchanged','architecture':'byte-identical V1 trapos_model.py; 545 policy parameters; shared weights trainable','policy':'pair retention scope; first header entity is focus; both may be retained and queried; final focus change supplied causally','acceptance':'confirmed AND not negated AND member of retention scope; valid repeat accepted; outside scope is not declared false','data':'2400 sequences; paired focal/secondary queries; 1200 programs; no A-C train; 12000 proposal labels','initialization':'identical A/C from Addressable V1.2, NOT V1 final; same recipe and head seed','checkpoint':'final300 only','aux_weight':.1,'controls':'A trained; D and random and deterministic heuristics same-C-weight inference interventions, no extra training; random calibrated TRAIN only','triage':{'precision':.95,'recall':.95,'functional':.95,'joint':.90,'advantage_A':.05,'advantage_random':.05,'advantage_confirmed':.05,'clean_drop':.05,'counterfactual':.90},'confirmation':'A/C29,43 only when all pilot gates pass; unchanged recipe','limits':'CPU only, no sealed evaluation, no paid resources, no language training'}

def dump(n,x):(O/(n+'.json')).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def data(seed):return D.train(seed)
def update(m,o,rows):
 o.zero_grad(set_to_none=True);logits,tr=M.forward(m,rows,trace=True);y=torch.tensor([r['label'] for r in rows]);lm=F.cross_entropy(logits[:,-1],y);scores,gates,labels,types=M.selection(tr,rows);aux=F.binary_cross_entropy_with_logits(scores,labels);loss=lm+.1*aux if m.core.policy=='C' else lm;loss.backward()
 grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert torch.isfinite(loss) and all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None)
 norm=float(torch.nn.utils.clip_grad_norm_(m.parameters(),1.));o.step()
 return {'lm':float(lm.detach()),'acceptance_bce':float(aux.detach()),'loss':float(loss.detach()),'accepted_fraction':float(gates.detach().mean()),'answer_accuracy':float((logits[:,-1].argmax(-1)==y).float().mean()),'grad_norms':grads,'clip_norm':norm}
def save(path,m,o,seed,arm,step,rows):
 torch.save({'model':m.state_dict(),'optimizer':o.state_dict(),'step':step,'cursor':step*8,'microstep':0,'accumulation':1,'sampler':'materialized order, no runtime RNG','dataset_sha':D.digest(rows),'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'seed':seed,'arm':arm,'random_rate':m.core.random_rate,'protocol':PROTOCOL,'source_sha':hashlib.sha256((R.parent.parent/'cryo-addressable-stability-v1/stability/results'/f'C-{seed}.pt').read_bytes()).hexdigest(),'architecture_sha':hashlib.sha256((R/'trapos_model.py').read_bytes()).hexdigest()},path)
def restore(path,rows):
 s=torch.load(path,weights_only=True,map_location='cpu');assert s['protocol']==PROTOCOL and s['dataset_sha']==D.digest(rows) and s['cursor']==s['step']*8 and s['architecture_sha']==hashlib.sha256((R/'trapos_model.py').read_bytes()).hexdigest();m,o=M.setup(s['seed'],s['arm'],s['random_rate']);m.load_state_dict(s['model'],strict=True);o.load_state_dict(s['optimizer']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng']);return m,o,s

def predictions(m,rows,tag=None,override=None,intervention=None,diagnostic=None):
 m.eval();out=[];sel=collections.Counter();bytype=collections.defaultdict(collections.Counter);states=[];delta=collections.defaultdict(list)
 with torch.no_grad():
  for start in range(0,len(rows),32):
   rr=rows[start:start+32];
   if diagnostic:
    x,y,mask=M.inputs(rr)
    if diagnostic!='oracle':
     for i,r in enumerate(rr):
      for j,ev in enumerate(r['events']):
       pos=ev['record']*4;c=r['ids'][pos-3]==49;n=r['ids'][pos-2]==49;scope=chr(r['ids'][pos+1]) in r['goal']
       mask[i,pos+3]={'confirmed':c,'goal':scope,'confirmed_nonnegated':c and not n}[diagnostic]
    old=m.core.policy;m.core.policy='D'
    try:logits,tr=m.core(x,oracle_mask=mask,trace=True,intervention=intervention)
    finally:m.core.policy=old
   else:logits,tr=M.forward(m,rr,trace=True,override=override,intervention=intervention)
   pr=logits[:,-1].argmax(-1).tolist();scores,gates,labels,types=M.selection(tr,rr)
   for g,y,typ in zip(gates.tolist(),labels.tolist(),types):
    key='tp' if g and y else 'fp' if g else 'fn' if y else 'tn';sel[key]+=1;bytype[typ][key]+=1
   for i,r in enumerate(rr):out.append({'id':r['id'],'q':r['q'],'other':r['other'],'affected':r['affected'],'label':r['label'],'prediction':pr[i]})
   for chunk in tr:
    for w in chunk['writes']:
     for i in range(len(rr)):
      if w['candidate'][i]:delta['accepted' if w['gate'][i] else 'rejected'].append(float((w['after'][i]-w['before'][i]).norm()))
   if start==0:states=[chunk['memory'].cpu()[:8] for chunk in tr]
 tp,fp,fn,tn=[sel[k] for k in ['tp','fp','fn','tn']];n=tp+fp+fn+tn
 met={'normal':sum(p['prediction']==p['label'] for p in out)/len(out),'n':len(out),'selection':dict(sel,precision=tp/(tp+fp) if tp+fp else 0.,recall=tp/(tp+fn) if tp+fn else 0.,false_positive_rate=fp/(fp+tn) if fp+tn else 0.,false_negative_rate=fn/(tp+fn) if tp+fn else 0.,accepted_rate=(tp+fp)/n),'by_type':dict(bytype),'state_change':{k:{'mean':sum(v)/len(v),'max':max(v),'n':len(v)} for k,v in delta.items()}}
 if tag:
  dump(tag+'-predictions',out);torch.save(states,O/(tag+'-states.pt'))
 return out,met

def evaluate(m,tag):
 sets=D.dev();report={}
 for name,rr in sets.items():
  pp,met=predictions(m,rr,tag+'-'+name);other,om=predictions(m,[D.other_query(r) for r in rr],tag+'-'+name+'-other');met['joint']=sum(a['prediction']==a['label'] and b['prediction']==b['label'] for a,b in zip(pp,other))/len(rr)
  for role in ['corrected','preserved']:
   ix=[i for i,r in enumerate(rr) if (r['q']==r['affected'])==(role=='corrected')];met[role]=sum(pp[i]['prediction']==pp[i]['label'] for i in ix)/len(ix)
  if name!='clean':
   cf={}
   for kind in ['invalid','current','obsolete']:
    pairs=[(i,D.counterfactual(r,kind)) for i,r in enumerate(rr)];pairs=[(i,r) for i,r in pairs if r is not None];alt,am=predictions(m,[r for i,r in pairs],tag+'-'+name+'-'+kind)
    cf[kind]={'n':len(pairs),'joint_correct':sum(pp[i]['prediction']==pp[i]['label'] and b['prediction']==b['label'] for (i,r),b in zip(pairs,alt))/len(pairs),'prediction_invariance':sum(pp[i]['prediction']==b['prediction'] for (i,r),b in zip(pairs,alt))/len(pairs)}
   met['counterfactuals']=cf
  report[name]=met
 # Same trained C, decisions forced to all writes: parameter/capacity matched policy intervention.
 if m.core.policy=='C':
  _,force=predictions(m,sets['contaminated_pair'],tag+'-override-all',override='all');report['override_all']=force
 rr=sets['contaminated_pair'];p,reset=predictions(m,rr,tag+'-reset',intervention='reset');report['reset']=reset
 # Pair compatible sessions that differ only in the current valid value. Core roll swaps state before query chunk.
 correct=follow=0
 for r in rr[:48]:
  partner=D.counterfactual(r,'current');cases=[r,partner];m.eval()
  with torch.no_grad():pr=M.forward(m,cases,intervention='swap')[:,-1].argmax(-1).tolist()
  correct+=pr[0]==r['label'];follow+=pr[0]==partner['label']
 report['compatible_swap']={'n':48,'original_accuracy':correct/48,'follows_partner':follow/48}
 dump(tag+'-metrics',report);return report

def train(arm,seed,rate=.6):
 rows=data(seed);tag=f'{arm}-{seed}';assert not (O/(tag+'.pt')).exists();m,o=M.setup(seed,arm,rate);save(O/(tag+'-initial.pt'),m,o,seed,arm,0,rows);logs=[];start=time.monotonic()
 for step in range(300):
  m.train();logs.append(dict(step=step+1,**update(m,o,rows[8*step:8*step+8])))
  if (step+1)%100==0:print(tag,step+1,'lm',logs[-1]['lm'],'aux',logs[-1]['acceptance_bce'],flush=True)
 seconds=time.monotonic()-start;save(O/(tag+'.pt'),m,o,seed,arm,300,rows);dump(tag+'-curve',logs);dump(tag+'-cost',{'seconds':seconds,'parameters':sum(p.numel() for p in m.parameters()),'trainable':sum(p.numel() for p in m.parameters() if p.requires_grad),'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'answer_targets':2400,'aux_targets':12000 if arm=='C' else 0,'input_ids':230400})
 if arm=='C':
  _,cal=predictions(m,rows);dump(f'calibration-{seed}',{'source':'TRAIN only, final deterministic policy','accepted_rate':cal['selection']['accepted_rate'],'targets':12000,'selection':cal['selection']});rate=cal['selection']['accepted_rate']
 return m,rate


def interventions(m,seed,tag):
 rows=D.train(seed);_,cal=predictions(m,rows);rate=cal['selection']['accepted_rate'];dump(tag+'-calibration',{'source':'TRAIN only','rate':rate})
 out={}
 for family,rr in D.dev().items():
  out[family]={}
  for name in ['oracle','confirmed','goal','confirmed_nonnegated']:
   _,d=predictions(m,rr,tag+'-'+family+'-'+name,diagnostic=name);out[family][name]=d
  _,d=predictions(m,rr,tag+'-'+family+'-all',override='all');out[family]['all']=d
  old=m.core.policy;oldrate=m.core.random_rate;m.core.policy='B';m.core.random_rate=rate
  try:_,d=predictions(m,rr,tag+'-'+family+'-random')
  finally:m.core.policy=old;m.core.random_rate=oldrate
  out[family]['random']=d
 dump(tag+'-interventions',out);return out

def gate(rep,iv):
 checks={};c=rep['C']
 for fam in ['contaminated_pair','layout','surface','focus_change']:
  v=c[fam];ss=v['selection']
  checks[fam+'-precision']=ss['precision']>=.95;checks[fam+'-recall']=ss['recall']>=.95
  checks[fam+'-answer']=v['normal']>=.95;checks[fam+'-joint']=v['joint']>=.9
  checks[fam+'-preservation']=v['preserved']>=.95;checks[fam+'-correction']=v['corrected']>=.95
  for kind,z in v['counterfactuals'].items():checks[fam+'-'+kind]=z['joint_correct']>=.9
 for control in ['random','confirmed']:
  checks['advantage-'+control]=c['contaminated_pair']['normal']>=iv['contaminated_pair'][control]['normal']+.05
 checks['advantage-trained-A']=c['contaminated_pair']['normal']>=rep['A']['contaminated_pair']['normal']+.05
 checks['clean']=c['clean']['normal']>=.95 and c['clean']['normal']>=rep['A']['clean']['normal']-.05
 return {'passed':all(checks.values()),'checks':checks}

def campaign(seed):
 rep={}
 for arm in ['C','A']:
  m,_=train(arm,seed);rep[arm]=evaluate(m,f'{arm}-{seed}')
  if arm=='C':iv=interventions(m,seed,f'C-{seed}')
 g=gate(rep,iv);dump(f'gate-{seed}',g);print('GATE',seed,g,flush=True);return g

def main():
 assert json.loads((O/'preflight.json').read_text())['passed'];f=json.loads((O/'FREEZE.json').read_text())
 for name,h in f['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
 g=campaign(17)
 if g['passed']:
  for seed in [29,43]:campaign(seed)
 print('DONE; sealed evaluations=0',flush=True)
if __name__=='__main__':main()
