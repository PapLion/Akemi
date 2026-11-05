import json,copy,hashlib,time,collections,datetime
import torch
import trapos_train as T
M=T.M;D=T.D;R=T.R;O=T.O
out={};decisions=[]
for path in sorted(O.glob('[ABCD]-??.pt')):
 tag=path.stem;arm,ss=tag.split('-');seed=int(ss);rows=D.train(seed);m,o,s=T.restore(path,rows);m.eval();assert s['step']==300
 original=torch.load(path,weights_only=True,map_location='cpu');assert D.S.A.I.equal(m.state_dict(),original['model']) and D.S.A.I.equal(o.state_dict(),original['optimizer'])
 ref=torch.load(O/f'C-{seed}-initial.pt',weights_only=True,map_location='cpu');init=torch.load(O/(tag+'-initial.pt'),weights_only=True,map_location='cpu');assert D.S.A.I.equal(init['model'],ref['model'])
 out[tag]={'safe_checkpoint_exact':True,'initial_models_identical':True,'no_more_than_300':True}
 if arm!='C':continue
 agreement=collections.Counter();n=0;per=[]
 with torch.no_grad():
  for family,rr in D.dev().items():
   for start in range(0,len(rr),32):
    batch=rr[start:start+32];_,tr=M.forward(m,batch,trace=True)
    for chunk in tr:
     for w in chunk['writes']:
      for i,r in enumerate(batch):
       if not w['candidate'][i]:continue
       pos=int(w['end_index'][i]);record=pos//4;flag=r['ids'][(record-1)*4+1]==49;g=bool(w['gate'][i]);lab=r['labels'][(record-2)//4];agreement[family+'-confirmed_only']+=g==flag;agreement[family+'-oracle']+=g==lab;agreement[family+'-n']+=1;n+=1
       per.append({'id':r['id'],'family':family,'end_index':pos,'probability':float(w['prob'][i]),'accept':g,'oracle':lab,'confirmed_only':flag})
 T.dump(tag+'-filter-decisions',per);out[tag]['decision_heuristic_agreement']={family:{'confirmed_only':agreement[family+'-confirmed_only']/agreement[family+'-n'],'oracle':agreement[family+'-oracle']/agreement[family+'-n'],'n':agreement[family+'-n']} for family in D.dev()}
 # Actual inputs to policy head, sampled without changing model parameters.
 captured=[]
 hook=m.core.trapos.register_forward_pre_hook(lambda mod,args:captured.append(args[0].detach()))
 with torch.no_grad():M.forward(m,rows[:8]);hook.remove()
 with torch.no_grad():
  for _ in range(20):
   for x in captured:m.core.trapos(x)
  begin=time.perf_counter()
  for _ in range(200):
   for x in captured:m.core.trapos(x)
  seconds=time.perf_counter()-begin
 T.dump('policy-timing',{'seed':seed,'head_calls_per_forward':len(captured),'input_shapes':[list(x.shape) for x in captured],'timed_forward_repetitions':200,'head_only_ms_per_model_forward':seconds/200*1000,'scope':'CPU no-grad head calls on actual captured features, excludes common hidden/write/read/backward; not total speedup','threads':1})
 # No hidden foreground route: exact Jacobian zero outside local block, not bit equality claim.
 rr=D.dev()['contaminated_pair'][:2];x,y,_=M.inputs(rr);c=[]
 def capture(mod,args,value):value.retain_grad();c.append(value)
 handle=m.core.emb.register_forward_hook(capture);m.zero_grad(set_to_none=True);m.core.hidden(x,None,None)[:,-16:].sum().backward();handle.remove();assert torch.count_nonzero(c[0].grad[:,:80])==0
 out[tag]['foreground_prefix_jacobian_nonzero']=0
freeze=json.loads((O/'FREEZE.json').read_text())
for name,h in freeze['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
source=R.parent.parent/'cryo-addressable-stability-v1/stability';manifest={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (source/'SHA256SUMS').read_text().splitlines()}
for seed in [17,29,43]:
 p=source/'results'/f'C-{seed}.pt';assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest[f'results/C-{seed}.pt']
assert (R.parent/'addressable/address_model.py').read_bytes()==(source.parent/'addressable/address_model.py').read_bytes()
T.dump('final-integrity',{'checks':out,'frozen_files_unchanged':True,'source_checkpoints_original':True,'historical_architecture_unchanged':True,'sealed_evaluations':0,'gpu':False,'diagnostic_updates':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print('FINAL CHECKS PASS')
