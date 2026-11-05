import copy,json,hashlib,collections,torch
import trapos_train as T
R=T.R;O=T.O;D=T.D;M=T.M
checks={}
for arm in ['A','C']:
 for seed in [17,29,43]:
  path=O/f'{arm}-{seed}.pt'
  if not path.exists():continue
  m,o,s=T.restore(path,D.train(seed));assert s['step']==300
  raw=torch.load(path,map_location='cpu',weights_only=True);assert D.S.A.I.equal(raw['model'],m.state_dict()) and D.S.A.I.equal(raw['optimizer'],o.state_dict())
  init=torch.load(O/f'{arm}-{seed}-initial.pt',map_location='cpu',weights_only=True);ref=torch.load(O/f'C-{seed}-initial.pt',map_location='cpu',weights_only=True);assert D.S.A.I.equal(init['model'],ref['model'])
  checks[f'{arm}-{seed}']={'full_checkpoint_restore':True,'initial_identity':True}
  if arm!='C':continue
  decisions=[]
  m.eval()
  with torch.no_grad():
   for family,rows in D.dev().items():
    for start in range(0,len(rows),32):
     rr=rows[start:start+32];_,tr=M.forward(m,rr,trace=True)
     for chunk in tr:
      for w in chunk['writes']:
       for i,r in enumerate(rr):
        if not w['candidate'][i]:continue
        p=int(w['end_index'][i])-3;j=(p//4-2)//4;ev=r['events'][j]
        decisions.append({'id':r['id'],'family':family,'position':p,'type':ev['type'],'entity':ev['entity'],'value':ev['value'],'confirmed':r['ids'][p-3]==49,'negated':r['ids'][p-2]==49,'in_scope':chr(r['ids'][p+1]) in r['goal'],'oracle':r['labels'][j],'accepted':bool(w['gate'][i]),'probability':float(w['prob'][i])})
  T.dump(f'C-{seed}-filter-decisions',decisions)
  agreement={}
  for fam in D.dev():
   rr=[r for r in decisions if r['family']==fam]
   agreement[fam]={k:sum(r['accepted']==pred(r) for r in rr)/len(rr) for k,pred in {'confirmed':lambda r:r['confirmed'],'confirmed_nonnegated':lambda r:r['confirmed'] and not r['negated'],'goal':lambda r:r['in_scope'],'oracle':lambda r:r['oracle']}.items()}
  checks[f'{arm}-{seed}']['heuristic_agreement']=agreement
freeze=json.loads((O/'FREEZE.json').read_text())
for name,h in freeze['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
assert (R/'trapos_model.py').read_bytes()==(R.parent/'trapos/trapos_model.py').read_bytes()
source=R.parent.parent/'cryo-addressable-stability-v1/stability';hs={l.split('  ',1)[1]:l.split('  ',1)[0] for l in (source/'SHA256SUMS').read_text().splitlines()}
for seed in [17,29,43]:
 p=source/'results'/f'C-{seed}.pt';assert hashlib.sha256(p.read_bytes()).hexdigest()==hs[f'results/C-{seed}.pt']
# Paired queries differ only in the final declared focus and query, not accepted prefix.
for r in D.train(17):
 s=D.other_query(r);assert r['ids'][:80]==s['ids'][:80] and r['labels']==s['labels'];assert chr(s['ids'][-15])==s['q'];assert D.oracle(r)[0]==D.oracle(s)[0]
T.dump('final-integrity',{'passed':True,'checks':checks,'model_byte_identical_V1':True,'source_checkpoints_original':True,'frozen_code_unchanged':True,'paired_query_causal_contract':True,'gpu':False,'sealed_sets_opened':0})
print('FINAL CHECKS PASS')
