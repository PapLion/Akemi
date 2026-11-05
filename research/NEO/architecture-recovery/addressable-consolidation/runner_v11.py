"""Frozen data-distribution contrasts; imports Addressable implementation unmodified."""
import json,random,time,copy,hashlib,collections,datetime,resource,statistics,platform
from pathlib import Path
import torch
import torch.nn.functional as F
import data_v11 as D
A=D.A;T=D.T;C=D.C;R=D.R;O=R/'results'
torch.set_num_threads(1)
PROTOCOL=json.loads((R/'protocol.json').read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def dump(n,x):T.dump(O/n,x)
def setup(seed=17):
 if seed==17:return A.setup()
 # Same class/equations. Seed-specific historical warmstart, explicitly declared.
 m,cp=A.I.run.extract.load_model('delta_fast',seed);m.requires_grad_(True)
 import network
 ref=network.build('delta_fast',seed,16)
 for (name,p),(nn,q) in zip(m.named_parameters(),ref.named_parameters()):assert name==nn;p.requires_grad_(q.requires_grad)
 m.core.__class__=A.Addressable
 for p in m.core.memory_head.parameters():p.requires_grad_(False)
 torch.manual_seed(101+seed-17);d=A.I.run.probes.Decoder(256,4)
 torch.manual_seed(707+seed-17)
 m.core.address=torch.nn.Linear(32,8,bias=False);m.core.event_value=torch.nn.Linear(32,32);m.core.address_out=torch.nn.Linear(32,32,bias=False)
 o=torch.optim.AdamW([p for p in [*m.parameters(),*d.parameters()] if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False)
 return m,d,o,random.Random(seed)

def batch(rows,arm,step,rng):
 indices=[rng.randrange(160) for _ in range(8)]
 variants=[(step*8+i)%12 for i in range(8)]
 rr=[copy.deepcopy(rows[i] if arm=='A' else rows[12*i+v]) for i,v in zip(indices,variants)]
 if arm=='P':rr=[D.position_variant(r,step,i) for i,r in enumerate(rr)]
 return rr,indices,variants

def update(m,d,o,rng,rows,arm,step):
 rr,ix,var=batch(rows,arm,step,rng);o.zero_grad(set_to_none=True)
 lm,a,b,logits,tr=T.losses(m,d,rr);loss=lm+.1*a[0];loss.backward()
 assert torch.isfinite(loss) and all(torch.isfinite(p.grad).all() for p in [*m.parameters(),*d.parameters()] if p.grad is not None)
 grad={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None}
 norm=float(torch.nn.utils.clip_grad_norm_([*m.parameters(),*d.parameters()],1.));o.step()
 exposures=[dict(base_index=i,variant=v,kind=r['kind'],affected=r['affected'],answer=r['label']-48,positions=r['positions'],event=r.get('event')) for i,v,r in zip(ix,var,rr)]
 return dict(step=step+1,indices=ix,variants=var,exposures=exposures,lm=float(lm.detach()),initial_ce=float(a[0].detach()),post_ce=float(b[0].detach()),total=float(loss.detach()),initial_accuracy=float((a[1].argmax(-1)==a[2]).float().mean()),original_accuracy=float((logits[:,-1].argmax(-1)==torch.tensor([r['label'] for r in rr])).float().mean()),clip_input_norm=norm,gradients=grad)

def save(path,m,d,o,rng,rows,arm,seed,step):
 torch.save(dict(model=m.state_dict(),decoder=d.state_dict(),optimizer=o.state_dict(),sampler_rng=rng.getstate(),torch_rng=torch.get_rng_state(),python_rng=random.getstate(),step=step,microstep=0,accumulation=1,cursor=step*8,scheduler=None,protocol=PROTOCOL,protocol_sha256=digest(PROTOCOL),dataset_sha256=digest(rows),arm=arm,seed=seed,tokenizer='symbolic ASCII fixture, no tokenizer modification',architecture_sha256=hashlib.sha256((R.parent/'addressable/address_model.py').read_bytes()).hexdigest()),path)

def restore(path,rows):
 s=torch.load(path,weights_only=True,map_location='cpu');assert s['protocol_sha256']==digest(PROTOCOL) and s['dataset_sha256']==digest(rows) and s['cursor']==s['step']*8
 m,d,o,rng=setup(s['seed']);assert s['architecture_sha256']==hashlib.sha256((R.parent/'addressable/address_model.py').read_bytes()).hexdigest()
 m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True);o.load_state_dict(s['optimizer']);rng.setstate(s['sampler_rng']);torch.set_rng_state(s['torch_rng']);random.setstate(s['python_rng'])
 return m,d,o,rng,s

def summarize(ev,rows):
 pred=ev['predictions'];acc=ev['metrics']['all'];out=dict(initial=acc['initial'],post=acc['post'],retained=acc['retained'],normal_accuracy=acc['original_accuracy'],n=len(rows))
 for role in ['affected','unmodified']:
  good=n=0
  for p,r in zip(pred,rows):
   if r['kind']!='correct':continue
   k=0 if r['affected']==r['q'] else 1;k=k if role=='affected' else 1-k
   good+=p['stages']['post']['pred'][k]==p['stages']['post']['label'][k];n+=1
  if n:out[role]=dict(n=n,accuracy=good/n)
 return out

def evaluate(m,d,rows,name):
 m.eval();ev,states=T.evaluate(m,d,rows);dump(name+'.json',ev)
 torch.save(dict(states=states,ids=[r['id'] for r in rows]),O/(name+'-states.pt'))
 return ev,summarize(ev,rows)

def cf_metrics(base,changed):
 aa=base['predictions'];bb=changed['predictions'];n=len(aa)
 return dict(n=n,normal_joint_correct=sum(a['original_prediction']==a['original_label'] and b['original_prediction']==b['original_label'] for a,b in zip(aa,bb))/n,normal_invariance=sum(a['original_prediction']==b['original_prediction'] for a,b in zip(aa,bb))/n,strict_binding_joint=sum(all(p==y for p,y in zip(a['stages']['post']['pred'],a['stages']['post']['label'])) and all(p==y for p,y in zip(b['stages']['post']['pred'],b['stages']['post']['label'])) for a,b in zip(aa,bb))/n)

def evaluate_arm(arm,seed,rows):
 tag=f'{arm}-{seed}';m,d,o,rng,s=restore(O/(tag+'.pt'),rows);report={};sets=D.dev_sets()
 for name,rr in sets.items():
  ev,met=evaluate(m,d,rr,tag+'-'+name);report[name]=met
 formation=sets['formation'];ix=[i for i,r in enumerate(formation) if r['initial_values'][0]!=r['initial_values'][1]]
 sw=[D.transform(r,'swap') for r in formation];base,_=evaluate(m,d,formation,tag+'-swap-base');other,_=evaluate(m,d,sw,tag+'-swap')
 report['swap']=dict(n=len(ix),normal_joint_correct=sum(base['predictions'][i]['original_prediction']==base['predictions'][i]['original_label'] and other['predictions'][i]['original_prediction']==other['predictions'][i]['original_label'] for i in ix)/len(ix),binding_joint=sum(all(p==y for p,y in zip(base['predictions'][i]['stages']['initial']['pred'],base['predictions'][i]['stages']['initial']['label'])) and all(p==y for p,y in zip(other['predictions'][i]['stages']['initial']['pred'],other['predictions'][i]['stages']['initial']['label'])) for i in ix)/len(ix))
 both,_=evaluate(m,d,[D.query_other(r) for r in formation],tag+'-other-query');report['formation_normal_both']=sum(a['original_prediction']==a['original_label'] and b['original_prediction']==b['original_label'] for a,b in zip(base['predictions'],both['predictions']))/len(formation)
 for family in ['correction_fixed','correction_layout']:
  base,_=evaluate(m,d,sets[family],tag+'-cf-'+family+'-base');report[family]['counterfactuals']={}
  for kind in ['obsolete','current']:
   altered,_=evaluate(m,d,[D.transform(r,kind) for r in sets[family]],tag+'-cf-'+family+'-'+kind)
   report[family]['counterfactuals'][kind]=cf_metrics(base,altered)
 # Compatible memory swap pairs: same entity, other current value. No batch-position proxy.
 # Every row has same layout, q, other and write order as its partner.
 rr=formation;group={}
 for i,r in enumerate(rr):group[(r['q'],r['other'],r['write_order'],tuple(r['initial_values']))]=i
 pairs=[]
 for i,r in enumerate(rr):
  vv=((r['initial_values'][0]+1)%4,r['initial_values'][1]);partner=group[(r['q'],r['other'],r['write_order'],vv)];pairs.append((i,partner))
 out={k:[] for k in ['normal','reset','swap']}
 with torch.no_grad():
  for i,j in pairs:
   xx=torch.tensor([rr[i]['ids'],rr[j]['ids']])
   for kind in out:out[kind].append(int(m(xx,intervention=None if kind=='normal' else kind)[0,-1].argmax()))
 y=[r['label'] for r in rr];partner_y=[rr[j]['label'] for i,j in pairs]
 report['interventions']={kind:dict(accuracy=sum(p==q for p,q in zip(pp,y))/len(y),follows_partner=sum(p==q for p,q in zip(pp,partner_y))/len(y),prediction_change=sum(p!=q for p,q in zip(pp,out['normal']))/len(y)) for kind,pp in out.items()}
 dump(tag+'-metrics.json',report);return report

def gate(report):
 t=PROTOCOL['triage'];checks={}
 for family in ['correction_fixed','correction_layout']:
  checks[family+'_affected']=report[family]['affected']['accuracy']>=t['corrected_binding_fixed' if family=='correction_fixed' else 'corrected_binding_layout']
  checks[family+'_unmodified']=report[family]['unmodified']['accuracy']>=t['unmodified_binding_min']
  checks[family+'_normal']=report[family]['normal_accuracy']>=t['normal_fixed' if family=='correction_fixed' else 'normal_layout']
  checks[family+'_current_cf']=report[family]['counterfactuals']['current']['normal_joint_correct']>=.9
  checks[family+'_stale_cf']=report[family]['counterfactuals']['obsolete']['normal_joint_correct']>=.9
 checks.update(swap=report['swap']['normal_joint_correct']>=t['swap_strict'] and report['swap']['binding_joint']>=t['swap_strict'],novel_joint=report['novel_pairs']['initial']['joint_accuracy']>=t['novel_joint'],formation_joint=report['formation']['initial']['joint_accuracy']>=t['formation_joint'],normal_both=report['formation_normal_both']>=t['formation_normal'])
 return dict(passed=all(checks.values()),checks=checks)

def train(arm,seed,rows):
 tag=f'{arm}-{seed}';assert not (O/(tag+'.pt')).exists();m,d,o,rng=setup(seed);save(O/(tag+'-initial.pt'),m,d,o,rng,rows,arm,seed,0)
 logs=[];start=time.monotonic()
 for step in range(300):
  logs.append(update(m,d,o,rng,rows,arm,step))
  if (step+1)%100==0:print(tag,step+1,'CE',logs[-1]['lm'],flush=True)
 sec=time.monotonic()-start;save(O/(tag+'.pt'),m,d,o,rng,rows,arm,seed,300)
 dump(tag+'-curve.json',logs);dump(tag+'-cost.json',dict(seconds=sec,updates=300,answer_targets=2400,aux_targets=4800,parameters=sum(p.numel() for p in m.parameters()),trainable=sum(p.numel() for p in m.parameters() if p.requires_grad),aux_parameters=sum(p.numel() for p in d.parameters()),rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
 return logs

def main():
 assert (O/'preflight.json').exists() and json.loads((O/'preflight.json').read_text())['pass_all'];assert not (O/'A-17.pt').exists()
 aa=D.control();bb=D.treatment();logsA=train('A',17,aa);logsB=train('B',17,bb)
 assert [r['indices'] for r in logsA]==[r['indices'] for r in logsB]
 # Literal faithful reconstruction, including every model/decoder value at step300.
 old=R.parent.parent/'cryo-addressable-memory-v1/addressable/results/main.pt';s=torch.load(old,weights_only=True,map_location='cpu');new=torch.load(O/'A-17.pt',weights_only=True)
 assert A.I.equal(s['model'],new['model']) and A.I.equal(s['decoder'],new['decoder']) and A.I.equal(s['optimizer'],new['optimizer'])
 dump('control-reconstruction.json',dict(exact_model_decoder_adamw=True,original=str(old),base_orders_paired=True))
 reports={arm:evaluate_arm(arm,17,aa if arm=='A' else bb) for arm in ['A','B']}
 decision=gate(reports['B']);dump('primary-gate.json',decision);print('PRIMARY GATE',decision,flush=True)
 if decision['passed']:
  for seed in [29,43]:
   for arm,rr in [('A',aa),('B',bb)]:train(arm,seed,rr);evaluate_arm(arm,seed,rr)
 # Freeze model weights while diagnosing positional sensitivity.
 cells=D.grid();grid={}
 for arm in ['A','B']:
  m,d,*_=restore(O/f'{arm}-17.pt',aa if arm=='A' else bb);m.eval();grid[arm]={}
  with torch.no_grad():
   for name,rr in cells.items():
    ev,states=T.evaluate(m,d,rr);grid[arm][name]=summarize(ev,rr)
 dump('position-grid.json',grid)
 spread=max(x['normal_accuracy'] for x in grid['B'].values())-min(x['normal_accuracy'] for x in grid['B'].values())
 position_allowed=spread>=.1 or reports['B']['correction_layout']['normal_accuracy']<=.9
 dump('position-eligibility.json',dict(allowed=position_allowed,spread=spread,criterion=PROTOCOL['position_arm']))
 if position_allowed:
  train('P',17,bb);evaluate_arm('P',17,bb)
  # Prospectively held-out position family, same for B and P; not used for updates.
  held=[D.move(r,(6,7),11) for r in bb if r['kind']=='correct']
  for arm in ['B','P']:
   m,d,*_=restore(O/f'{arm}-17.pt',bb);ev,met=evaluate(m,d,held,arm+'-position-heldout');dump(arm+'-position-heldout-metrics.json',met)
 print('DONE; sealed confirmation not read',flush=True)
if __name__=='__main__':main()
