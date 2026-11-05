from mw_run import *
import statistics

def modified(r,mode):
 s=copy.deepcopy(r)
 if mode=='swap':
  ix=[i for i,(op,e,v) in enumerate(s['ops']) if op=='='];s['ops'][ix[0]][2],s['ops'][ix[1]][2]=s['ops'][ix[1]][2],s['ops'][ix[0]][2]
 elif mode=='obsolete':
  ix=next(i for i,(op,e,v) in enumerate(s['ops']) if op=='=' and e==r['affected']);s['ops'][ix][2]=str((int(s['ops'][ix][2])+1)%4)
 else:
  ix=max(i for i,(op,e,v) in enumerate(s['ops']) if op in '=!' and e==r['q']);s['ops'][ix][2]=str((int(s['ops'][ix][2])+1)%4)
 z=C.P.make_record(s['ops'],r['q'],'counterfactual','diagnostic');s.update(ids=z['ids'],label=z['label']);return s

def correction_panel(condition):
 rows=[]
 for r in C.data(condition):
  for affected in [r['q'],r['other']]:
   for kind in ['preserve','correct']:
    s=copy.deepcopy(r);old=C.P.oracle(r['ops'],affected);s['ops'][8]=['!',affected,str(old if kind=='preserve' else (old+1)%4)]
    z=C.P.make_record(s['ops'],s['q'],kind,'diagnostic');s.update(ids=z['ids'],label=z['label'],kind=kind,affected=affected,stages=[1,4]);rows.append(s)
 return rows

def joint_pairs(a,b,stage='initial'):
 n=len(a['predictions']);strict=sum(all(p==y for p,y in zip(x['stages'][stage]['pred'],x['stages'][stage]['label'])) and all(p==y for p,y in zip(z['stages'][stage]['pred'],z['stages'][stage]['label'])) for x,z in zip(a['predictions'],b['predictions']))
 functional=sum(x['original_prediction']==x['original_label'] and z['original_prediction']==z['original_label'] for x,z in zip(a['predictions'],b['predictions']))
 return dict(n=n,strict_binding_pair_accuracy=strict/n,original_joint_accuracy=functional/n)

def benchmark(m,d,rows):
 # Same fixed batches across arms; time WITHOUT trace logging/profiler overhead beyond loss extraction common to all.
 batch=rows[:8];o=torch.optim.AdamW([p for p in [*m.parameters(),*d.parameters()] if p.requires_grad],lr=.003,betas=(.9,.95),weight_decay=.01,foreach=False);times=[]
 for step in range(7):
  o.zero_grad();t=time.perf_counter();lm,a,b,_,_=T.losses(m,d,batch);t1=time.perf_counter();(lm+.1*a[0]).backward();t2=time.perf_counter();torch.nn.utils.clip_grad_norm_([*m.parameters(),*d.parameters()],1);o.step();t3=time.perf_counter()
  if step>=2:times.append(dict(forward_ms=1000*(t1-t),backward_ms=1000*(t2-t1),clip_adamw_ms=1000*(t3-t2)))
 return dict(steps=5,warmup=2,means={k:statistics.mean(x[k] for x in times) for k in times[0]},scope='Disposable loaded copy; includes common loss extraction; not pure model forward')

def main():
 allresults={};orders=[]
 for arm,K,condition in [('A',1,'same'),('B',2,'same'),('C',1,'separate')]:
  rows=C.data(condition);m,d,o,rng,step=load(OUT/f'{arm}-300.pt',rows,K);orders.append([x['indices'] for x in json.loads((OUT/f'{arm}-curves.json').read_text())]);base=json.loads((OUT/f'{arm}-train-evaluation.json').read_text());sw=[modified(r,'swap') for r in rows];swap,ss=C.evaluate(m,d,sw);indices=[i for i,r in enumerate(rows) if r['initial_values'][0]!=r['initial_values'][1]]
  sub=lambda ev:dict(predictions=[ev['predictions'][i] for i in indices])
  result=dict(value_swap=joint_pairs(sub(base),sub(swap)),swap_marginal=swap['metrics']['all']['initial'])
  panel=correction_panel(condition);cor,states=C.evaluate(m,d,panel);dump(f'{arm}-correction-evaluation.json',cor);torch.save(dict(states=states,ids=[r['id'] for r in panel]),OUT/f'{arm}-correction-states.pt')
  result['correction_metrics']=cor['metrics'];cf=[r for r in panel if r['kind']=='correct'];original,_=C.evaluate(m,d,cf)
  for mode in ['obsolete','current']:
   changed,_=C.evaluate(m,d,[modified(r,mode) for r in cf]);result[mode]=joint_pairs(original,changed,'post');dump(f'{arm}-{mode}-evaluation.json',changed)
  if K==2:
   batch=rows[::20];m.zero_grad();lm,a,b,_,tr=T.losses(m,d,batch);a[0].backward();t=tr[1];qg=m.core.memory_head.summary_query.grad
   result['candidates']=dict(query_cosine=float(F.cosine_similarity(m.core.memory_head.summary_query[0],m.core.memory_head.summary_query[1],dim=0)),state_cosine=float(F.cosine_similarity(t['candidates'][:,0],t['candidates'][:,1],dim=-1).mean()),weight_l1=float((t['weights'][:,0]-t['weights'][:,1]).abs().sum(-1).mean()),query_gradient_norms=qg.norm(dim=-1).tolist(),query_gradient_cosine=float(F.cosine_similarity(qg[0],qg[1],dim=0)),contribution_norms=t['contributions'].norm(dim=(-2,-1)).mean(0).tolist(),mean_write_gate=t['write'].mean((0,2)).tolist())
   torch.save({name:t[name].detach() for name in ['weights','candidates','keys','values','controls','contributions','memory']},OUT/'B-candidate-trace.pt')
   dump('B-selection-weights.json',dict(ids=[r['id'] for r in batch],weights=t['weights'].detach().tolist(),stats=result['candidates']))
  # Profiling bounded disposable forward to isolate writer label cost is separate from throughput.
  with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU]) as prof:
   with torch.no_grad():m(torch.tensor([r['ids'] for r in rows[:8]]))
  (OUT/f'{arm}-cpu-profile.txt').write_text(prof.key_averages().table(sort_by='self_cpu_time_total',row_limit=30))
  # Reload so timing cannot modify checkpoint used for scientific evaluation.
  m,d,o,rng,step=load(OUT/f'{arm}-300.pt',rows,K);result['timing']=benchmark(m,d,rows)
  allresults[arm]=result;print(arm,result['value_swap'],flush=True)
 assert orders[0]==orders[1]==orders[2];dump('analysis.json',allresults);dump('batch-order-verification.json',dict(identical=True,steps=300))
 a=json.loads((OUT/'A-dev-evaluation.json').read_text())['metrics']['all']['initial']['joint_accuracy'];b=json.loads((OUT/'B-dev-evaluation.json').read_text())['metrics']['all']['initial']['joint_accuracy'];at=json.loads((OUT/'A-train-evaluation.json').read_text())['metrics']['all']['initial']['joint_accuracy'];bt=json.loads((OUT/'B-train-evaluation.json').read_text())['metrics']['all']['initial']['joint_accuracy'];gate=b-a>=.1 and bt-at>=.1 and b>=.5 and allresults['B']['value_swap']['strict_binding_pair_accuracy']>=.25
 dump('confirmation-gate.json',dict(pass_gate=gate,dev_gain=b-a,train_gain=bt-at,dev_joint=b,swap_joint=allresults['B']['value_swap']['strict_binding_pair_accuracy'],note='If false: stop K exploration; no extra seeds or larger K.'))
if __name__=='__main__':main()
