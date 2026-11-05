"""Counterfactuals + gate observations, no optimizer updates and no sealed reads."""
import json,argparse,statistics
from pathlib import Path
import torch
import panel,network,learn
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def gate_rows():
 rows=panel.load('iid');out=[]
 for task in panel.TASKS:
  for far in [False,True]:out+=sorted([r for r in rows if r['task']==task and r['outside_window']==far],key=lambda r:r['id'])[:2]
 assert len(out)==32
 return out
@torch.no_grad()
@torch.random.fork_rng(devices=[])
def predictions(m,rr,intervention=None):
 if m.mode=='random':torch.manual_seed(991)
 out=[]
 for k in range(0,len(rr),32):out+=m(learn.batch(rr[k:k+32])[0],intervention=intervention)[:,-1].argmax(-1).tolist()
 return out
@torch.no_grad()
def case(cp):
 s=torch.load(cp,weights_only=True,map_location='cpu');cfg=s['config'];m=network.build(cfg['arm'],int(cp.stem.rsplit('-',1)[1]),cfg['window'],cfg['mode'],random_budget=cfg.get('random_budget',.5));m.load_state_dict(s['model'],strict=True);m.eval();rows=panel.load('iid')+panel.load('structural');base=predictions(m,rows);details=[]
 for kind in ['obsolete','valid']:
  pairs=[(i,panel.counterfactual(r,kind)) for i,r in enumerate(rows)];pairs=[(i,r) for i,r in pairs if r is not None]
  if cfg['mode']=='random':
   # Keep batch positions/shapes identical so the original and twins receive
   # exactly the same Bernoulli masks. Missing obsolete twins retain originals.
   full=list(rows)
   for i,r in pairs:full[i]=r
   pp=predictions(m,full);changed=[pp[i] for i,r in pairs]
  else:changed=predictions(m,[r for i,r in pairs])
  for (i,c),pred in zip(pairs,changed):
   r=rows[i];first=next((int(v) for op,e,v in r['ops'] if e==r['entity'] and op in '=!'),4);oldc=next((int(v) for op,e,v in c['ops'] if e==r['entity'] and op in '=!'),4)
   details.append({'id':r['id'],'split':r['split'],'task':r['task'],'entity':r['entity'],'outside_window':r['outside_window'],'kind':kind,'initial_equals_answer':first==r['answer'],'changed_pair_heldout':panel.heldout_pair(c['entity'],c['answer']),'operation_changed':any(a[0]!=b[0] for a,b in zip(r['ops'],c['ops'])),'label':r['label'],'changed_label':c['label'],'prediction':base[i],'changed_prediction':pred,'correct':base[i]==r['label'],'changed_correct':pred==c['label'],'both_correct':base[i]==r['label'] and pred==c['label'],'sensitive':pred!=base[i],'follows_obsolete_both':base[i]==48+first and pred==48+oldc})
 groups={}
 for kind in ['obsolete','valid']:
  for where in ['all','outside','recent']:
   for task in ['all']+panel.TASKS:
    rr=[r for r in details if r['kind']==kind and (where=='all' or r['outside_window']==(where=='outside')) and (task=='all' or r['task']==task)]
    if rr:groups[f'{kind}/{where}/{task}']={'n':len(rr),**{k:statistics.mean(r[k] for r in rr) for k in ['correct','changed_correct','both_correct','sensitive','follows_obsolete_both']}}
 interventions={};intervention_details=[];gates=[]
 if cfg['arm'].endswith('_fast'):
  for inter in ['reset','swap']:
   pp=predictions(m,rows,inter)
   for i,r in enumerate(rows):
    start=(i//32)*32;n=min(32,len(rows)-start);donor=start+(i-start-1)%n
    intervention_details.append({'id':r['id'],'split':r['split'],'task':r['task'],'outside_window':r['outside_window'],'label':r['label'],'base_prediction':base[i],'intervention':inter,'prediction':pp[i],'donor_id':rows[donor]['id'] if inter=='swap' else None})
   for where in ['all','outside','recent']:
    ix=[i for i,r in enumerate(rows) if where=='all' or r['outside_window']==(where=='outside')];interventions[f'{inter}/{where}']={'n':len(ix),'base_accuracy':statistics.mean(base[i]==rows[i]['label'] for i in ix),'accuracy':statistics.mean(pp[i]==rows[i]['label'] for i in ix),'changed':statistics.mean(pp[i]!=base[i] for i in ix)}
  # Deterministically observe 32 IID examples; no human review or global quality claims.
  rr=gate_rows();_,trace=m(learn.batch(rr)[0],trace=True)
  for chunk,tr in enumerate(trace):
   for i,r in enumerate(rr):
    positions=range(chunk*2,min(chunk*2+2,15));ops=[r['ops'][k] for k in positions];relevant=any(e==r['entity'] and op in '=!-' for op,e,v in ops);valid=r['last_valid_record'] in positions
    gates.append({'id':r['id'],'task':r['task'],'chunk':chunk,'contains_current_valid_write':valid,'contains_accepted_target_update':relevant,'contains_rejected_target_proposal':any(e==r['entity'] and op in ['~','x'] for op,e,v in ops),'write_mean':float(tr['write'][i].mean()),'write_low_fraction':float((tr['write'][i]<.05).float().mean()),'write_high_fraction':float((tr['write'][i]>.95).float().mean()),'erase_mean':float(tr['erase'][i].mean()),'recover_mean':float(tr['recover'][i].mean()),'memory_change':float(tr['change'][i]),'memory_norm':float(tr['memory'][i].norm()),'write_executed':True})
 if cfg['arm']=='intact':
  # Call the frozen base implementation explicitly: Variant.forward does not
  # expose return_trace. Normal trained forward is precisely this same route.
  from vendor.cryo_historical import CryoTiny
  rr=gate_rows();x=learn.batch(rr)[0];_,trace=CryoTiny.forward(m.core,x,return_trace=True)
  for token,tr in enumerate(trace):
   for i,r in enumerate(rr):
    op,e,v=(r['ops'][token//4] if token//4<15 else ['?','_','_']);g=tr['gate'][i]
    gates.append({'id':r['id'],'task':r['task'],'chunk':token,'granularity':'token','contains_current_valid_write':token//4==r['last_valid_record'],'contains_accepted_target_update':e==r['entity'] and op in '=!-','contains_rejected_target_proposal':e==r['entity'] and op in ['~','x'],'write_mean':float(g.mean()),'write_low_fraction':float((g<.05).float().mean()),'write_high_fraction':float((g>.95).float().mean()),'erase_mean':None,'recover_mean':None,'memory_change':float((tr['slow'][i]-tr['previous'][i]).norm()),'memory_norm':float(tr['slow'][i].norm()),'write_executed':True})
 for kind in ['obsolete','valid']:
  rr=[r for r in details if r['kind']==kind and r['outside_window'] and r['task'] in ['replace','multiple'] and not r['initial_equals_answer']]
  if rr:groups[f'{kind}/outside/genuine_corrections']={'n':len(rr),**{k:statistics.mean(r[k] for r in rr) for k in ['correct','changed_correct','both_correct','sensitive','follows_obsolete_both']}}
 # A changed valid value can move to the excluded compositional support.
 # Separate that challenge from correction among values seen for this entity.
 for heldout in [False,True]:
  for correction_only in [False,True]:
   rr=[r for r in details if r['kind']=='valid' and r['outside_window'] and r['changed_pair_heldout']==heldout and not r['operation_changed'] and (not correction_only or r['task'] in ['replace','multiple'])]
   if rr:groups[f'valid/outside/value_only/heldout={heldout}/corrections={correction_only}']={'n':len(rr),**{k:statistics.mean(r[k] for r in rr) for k in ['correct','changed_correct','both_correct','sensitive']}}
 lookup={(r['id'],r['kind']):r for r in details};triplets=[]
 for r in details:
  if r['kind']!='valid' or not r['outside_window'] or r['task'] not in ['replace','multiple'] or r['initial_equals_answer']:continue
  old=lookup.get((r['id'],'obsolete'))
  if old is not None:triplets.append({'id':r['id'],'task':r['task'],'split':r['split'],'changed_pair_heldout':r['changed_pair_heldout'],'correct_all_three':r['both_correct'] and old['changed_correct']})
 triplet_groups={}
 for name,ss in [('all',triplets),('seen_pair',[r for r in triplets if not r['changed_pair_heldout']]),('heldout_pair',[r for r in triplets if r['changed_pair_heldout']])]:
  if ss:triplet_groups[name]={'n':len(ss),'correct':sum(r['correct_all_three'] for r in ss),'accuracy':statistics.mean(r['correct_all_three'] for r in ss)}
 return {'checkpoint':str(cp.relative_to(R)),'config':cfg,'step':s['step'],'counterfactual_groups':groups,'critical_triplets':triplets,'critical_triplet_groups':triplet_groups,'inference_interventions':interventions,'intervention_predictions':intervention_details},details,gates

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['pilot','extend','ablations']);a=p.parse_args();d=R/'results'/a.stage;summary=[]
 for cp in sorted(d.glob('*.pt')):
  out,details,gates=case(cp);summary.append(out);(d/(cp.stem+'-counterfactuals.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in details));(d/(cp.stem+'-gate-observations.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in gates));print(cp.stem,flush=True)
 (R/'results'/f'{a.stage}-diagnostics.json').write_text(json.dumps(summary,indent=2))
if __name__=='__main__':main()
