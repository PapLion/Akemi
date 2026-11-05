import json,copy,hashlib,collections,random,datetime,platform
import torch
import runner_v11 as V
D=V.D;A=V.A;T=V.T;R=V.R;O=V.O

def main():
 assert not (O/'preflight.json').exists()
 aa=D.control();bb=D.treatment();sets=D.dev_sets();D.verify(aa);D.verify(bb)
 for name,rr in sets.items():D.verify(rr)
 assert aa==D.C.data('same') and len(aa)==160 and len(bb)==1920
 f=D.frequencies(bb);aux=collections.defaultdict(dict);trans=collections.defaultdict(dict)
 for r in f['auxiliary']:aux[r['entity']][r['value']]=r['count']
 for e,c in aux.items():assert len(c)==4 and len(set(c.values()))==1
 for r in f['transitions']:trans[r['entity']][r['old'],r['new']]=r['count']
 for e,c in trans.items():assert len(c)==12 and len(set(c.values()))==1 and all(a!=b for a,b in c)
 train_ids={tuple(r['ids']) for r in aa+bb};overlaps={}
 for name,rr in sets.items():
  n=sum(tuple(r['ids']) in train_ids for r in rr);overlaps[name]=n
  if name!='correction_fit':assert n==0,(name,n)
 # All supervised initial target metadata are unchanged by correction exposure.
 for i,a in enumerate(aa):
  for b in bb[i*12:(i+1)*12]:
   assert a['ids'][:16]==b['ids'][:16] and a['stages'][0]==b['stages'][0]
   for e in [a['q'],a['other']]:assert D.oracle(a['ops'][:4],e)==D.oracle(b['ops'][:4],e)
 # Heuristic controls quantify legitimate lookup vs first/last-global shortcuts.
 heur={}
 for name,rr in [('treatment',bb),*sets.items()]:
  score=collections.Counter()
  for r in rr:
   events=[(e,int(v)) for op,e,v in r['ops'] if op in '=!']
   first=next(v for e,v in events if e==r['q']);last=events[-1][1];entity=next(v for e,v in reversed(events) if e==r['q']);y=r['label']-48
   for k,p in [('first_query_entity',first),('last_global',last),('last_query_entity',entity),('presence_only_constant0',0)]:score[k]+=p==y
  heur[name]={k:n/len(rr) for k,n in score.items()}
 V.dump('data-frequencies.json',dict(control=D.frequencies(aa),treatment=f,dev={name:D.frequencies(rr) for name,rr in sets.items()},train_overlap=overlaps,heuristics=heur))
 V.dump('control-data.json',aa);V.dump('treatment-data.json',bb)
 for name,rr in sets.items():V.dump('eval-data-'+name+'.json',rr)
 # Newly generated confirmation family: only generator/oracle integrity, never evaluated.
 sealed=D.sealed();D.verify(sealed);assert not any(tuple(r['ids']) in train_ids for r in sealed)
 path=R/'confirmatory/SEALED.jsonl';assert not path.exists()
 path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in sealed));path.chmod(0o400)
 V.dump('sealed-manifest.json',dict(records=len(sealed),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),model_evaluations=0,content_inspected=False,creation='deterministic generator/oracle checks only',independence='new structural family, not statistically independent underlying values'))
 report={};m,d,o,rng=V.setup();n,e,p,s=V.setup()
 assert A.I.equal(m.state_dict(),n.state_dict()) and A.I.equal(d.state_dict(),e.state_dict())
 pars=[p for p in [*m.parameters(),*d.parameters()] if p.requires_grad];ops=[p for g in o.param_groups for p in g['params']]
 assert len(ops)==len(set(map(id,ops)))==len(pars) and set(map(id,ops))==set(map(id,pars))
 rows=[bb[12*i+1] for i in range(8)];x=torch.tensor([r['ids'] for r in rows])
 for mode in [False,True]:
  m.train(mode);y,tr=m(x,trace=True)
  for cut in [1,3,4,7,8,12,16,24,32,35,36,40,48,60]:
   xx=x.clone();xx[:,cut:]=120;z=m(xx);assert torch.equal(y[:,:cut],z[:,:cut])
  assert torch.allclose(m(x.flip(0)).flip(0),y,atol=1e-5,rtol=1e-5)
  joined=torch.cat([x[:1],x[1:2]],1);doc=torch.cat([torch.zeros_like(x[:1]),torch.ones_like(x[1:2])],1);assert torch.allclose(m(joined,doc)[:,64:],y[1:2],atol=1e-5,rtol=1e-5)
  valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False;xx=x.clone();xx[:,56:]=127;assert torch.equal(m(x,valid=valid),m(xx,valid=valid))
  pref=m(x[:,:16],trace=True)[1][-1]['memory'];assert torch.allclose(pref,tr[1]['memory'],atol=1e-5,rtol=1e-5)
  a=T.stage(m,d,rows,tr,0);tt=m(torch.cat([x[:,:16],torch.full_like(x[:,16:],120)],1),trace=True)[1];b=T.stage(m,d,rows,tt,0);assert torch.equal(a[0],b[0])
 lm,aux,post,_,tr=T.losses(m,d,rows);o.zero_grad();aux[0].backward();gr={name:float(p.grad.norm()) for name,p in m.named_parameters() if p.grad is not None}
 assert gr['core.address.weight']>0 and gr['core.event_value.weight']>0
 for arm,rr in [('A',aa),('B',bb),('P',bb)]:
  m,d,o,rng=V.setup();logs=[V.update(m,d,o,rng,rr,arm,i) for i in range(4)];V.save(O/(arm+'-resume.pt'),m,d,o,rng,rr,arm,17,4)
  logs.extend(V.update(m,d,o,rng,rr,arm,i) for i in range(4,8));end=copy.deepcopy((m.state_dict(),d.state_dict(),o.state_dict(),rng.getstate(),torch.get_rng_state(),random.getstate()))
  n,e,p,s,saved=V.restore(O/(arm+'-resume.pt'),rr);tail=[V.update(n,e,p,s,rr,arm,i) for i in range(saved['step'],8)]
  assert A.I.equal(end,(n.state_dict(),e.state_dict(),p.state_dict(),s.getstate(),torch.get_rng_state(),random.getstate())) and logs[4:]==tail
  report[arm]=dict(exact_resume=True,continuous=8,cut=4)
 report.update(pass_all=True,initial_identity=True,optimizer_coverage=True,causality_train_eval=True,aux_causal=True,batch_isolation=True,document_reset=True,padding=True,aux_gradients=gr)
 V.dump('preflight.json',report)
 frozen={}
 for rel in ['protocol.json','data_v11.py','runner_v11.py','preflight.py','../addressable/address_model.py']:
  frozen[rel]=hashlib.sha256((R/rel).read_bytes()).hexdigest()
 V.dump('FREEZE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=frozen,control_sha256=V.digest(aa),treatment_sha256=V.digest(bb),dev_sha256={name:V.digest(rr) for name,rr in sets.items()},seed=17,stage='BEFORE main training'))
 print('ALL PREFLIGHT CONTRACTS PASS; protocol frozen',flush=True)
if __name__=='__main__':main()
