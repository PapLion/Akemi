import copy,json,hashlib,datetime
import torch
import torch.nn.functional as F
import study as S
O=S.O
out={}
for path in sorted(O.glob('[BC]-??.pt')):
 tag=path.stem;arm,ss=tag.split('-');seed=int(ss);rows,order=S.schedule(seed,arm);m,d,o,s=S.restore(path,rows,order);m.eval()
 assert s['step']==300 and s['cursor']==2400
 # Frozen diagnostic: per-role response gradients. No optimizer step.
 rr=S.evaluation()['held_pair'];grad={};read={}
 for role in ['corrected','preserved']:
  cases=[r for r in rr if (r['q']==r['affected'])==(role=='corrected')][:32]
  x=torch.tensor([r['ids'] for r in cases]);y=torch.tensor([r['label'] for r in cases]);m.zero_grad(set_to_none=True);logits,tr=m(x,trace=True);loss=F.cross_entropy(logits[:,-1],y);loss.backward()
  grad[role]={n:p.grad.detach().flatten().clone() for n,p in m.named_parameters() if p.grad is not None}
  dif=[]
  with torch.no_grad():
   for i,r in enumerate(cases):
    k=F.normalize(m.core.address(m.core.emb(torch.tensor(ord(r['q'])))),dim=-1);before=tr[r['stages'][0]]['memory'][i];after=tr[r['stages'][1]]['memory'][i];dif.append(float((k@(after-before)).norm()))
  read[role]={'response_ce':float(loss.detach()),'read_vector_change_mean':sum(dif)/len(dif),'n':len(cases)}
 norms={role:{n:float(g.norm()) for n,g in dd.items()} for role,dd in grad.items()};cos={}
 for n in set(grad['corrected'])&set(grad['preserved']):cos[n]=float(F.cosine_similarity(grad['corrected'][n],grad['preserved'][n],dim=0))
 # Full optimizer state survives safe load, exact parameter reproduction.
 cp=torch.load(path,weights_only=True,map_location='cpu');assert S.A.I.equal(cp['model'],m.state_dict()) and S.A.I.equal(cp['optimizer'],o.state_dict())
 initial=torch.load(O/(tag+'-initial.pt'),weights_only=True,map_location='cpu')
 reference=torch.load(O/(f'B-{seed}-initial.pt'),weights_only=True,map_location='cpu')
 assert S.A.I.equal(initial['model'],reference['model']) and S.A.I.equal(initial['decoder'],reference['decoder'])
 # Foreground cannot see changed facts outside its local block.
 case=S.evaluation()['held_pair'][0];changed=S.D.transform(case,'current');xx=torch.tensor([case['ids'],changed['ids']])
 with torch.no_grad():
  hh=m.core.hidden(xx,None,None);assert torch.equal(hh[0,-16:],hh[1,-16:])
  zz=m(xx,intervention='reset');assert torch.equal(zz[0,-1],zz[1,-1])
 out[tag]={'initial_BC_identical':True,'foreground_query_hidden_equal_under_prefix_change':True,'reset_response_equal_under_prefix_change':True,'grad_norms':norms,'gradient_cosine_by_parameter':cos,'read_change':read,'checkpoint_model_optimizer_exact':True,'no_updates_in_diagnostic':True}
S.dump('interference-diagnostics',out)
# Hash only named source code; no sealed evaluation opened.
original=S.ROOT.parent.parent/'cryo-addressable-memory-v1/addressable/address_model.py'
assert original.read_bytes()==(S.ROOT.parent/'addressable/address_model.py').read_bytes()
freeze=json.loads((O/'FREEZE.json').read_text())
for rel,h in freeze['files'].items():assert hashlib.sha256((S.ROOT.parent/rel).read_bytes()).hexdigest()==h
S.dump('final-integrity',{'architecture_matches_original':True,'freeze_files_unchanged':True,'safe_load_full_checkpoint':True,'sealed_evaluations':0,'gpu_used':False,'diagnostic_updates':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print('FINAL DIAGNOSTICS PASS')
