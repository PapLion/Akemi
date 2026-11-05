"""Read-only frozen V1 checkpoint evaluation under prospectively declared V2 semantics."""
import hashlib,json,torch
import trapos_train as T
p=T.R.parent.parent/'cryo-trapos-selection-v1/trapos/results/C-17.pt'
h=hashlib.sha256(p.read_bytes()).hexdigest();m,o=T.M.setup(17,'C');s=torch.load(p,map_location='cpu',weights_only=True);m.load_state_dict(s['model'],strict=True)
d=T.evaluate(m,'V1-frozen-on-V2');iv=T.interventions(m,17,'V1-frozen-on-V2')
agree={}
for fam,rr in T.D.dev().items():
 n=matches=0
 with torch.no_grad():
  for start in range(0,len(rr),32):
   batch=rr[start:start+32];_,tr=T.M.forward(m,batch,trace=True)
   for chunk in tr:
    for w in chunk['writes']:
     for i,r in enumerate(batch):
      if w['candidate'][i]:
       pos=int(w['end_index'][i])-3;matches+=bool(w['gate'][i])==(r['ids'][pos-3]==49);n+=1
 agree[fam]={'n':n,'confirmed_rule_agreement':matches/n}
assert hashlib.sha256(p.read_bytes()).hexdigest()==h
T.dump('V1-checkpoint-diagnostic',{'source':str(p),'sha256':h,'read_only':True,'agreement':agree})
print('V1 diagnostic complete; no updates',flush=True)
