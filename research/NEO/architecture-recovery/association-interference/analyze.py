import interference_runner as E
from interference_runner import *
def changed(r,which):
 s=copy.deepcopy(r);q=s['q'];event=s['event']
 if which=='obsolete':
  if s['ops'][event][1]!=q:return None
  for op in s['ops'][:event]:
   if op[0]=='=' and op[1]==q:op[2]=str((int(op[2])+1)%4)
 else:
  ix=max(i for i,(op,e,v) in enumerate(s['ops']) if op in '=!' and e==q);s['ops'][ix][2]=str((int(s['ops'][ix][2])+1)%4)
 z=P.make_record(s['ops'],q,'counterfactual','diagnostic');s.update(ids=z['ids'],label=z['label'],answer=z['answer']);return s

def tests():
 results={}
 for c in 'ABCD':
  rr=fixture(c);counts=collections.Counter()
  for r in rr:
   for b,j,e,y in entries([r]):
    prefix=r['ops'][:2*j+2];last=next(int(v) for op,ee,v in reversed(prefix) if ee=='ABCDE'[e] and op in '=!');assert y==last
   q=r['q'];vv=[int(v) for op,e,v in r['ops'] if op in '=!' and e==q];glob=[int(v) for op,e,v in r['ops'] if op in '=!'];true=r['label']-48
   for name,p in [('first_queried',vv[0]),('last_queried',vv[-1]),('last_any',glob[-1]),('presence_constant',0)]:counts[name]+=p==true
  results[c]={k:v/len(rr) for k,v in counts.items()}
 dump(R/'results/heuristics.json',results)

def probes(c,m,d,rr):
 res={};rr=rr[::8] # deterministic 80 matched programs, not chosen by predictions
 with torch.no_grad():
  x=torch.tensor([r['ids'] for r in rr]);base,tr=m(x,trace=True);p=base[:,-1].argmax(-1);target=torch.tensor([r['label'] for r in rr])
  for iv in ['reset','swap']:
   pp=m(x,intervention=iv)[:,-1].argmax(-1);res[iv]=dict(original_accuracy=float((pp==target).float().mean()),prediction_changed=float((pp!=p).float().mean()),scope='last-chunk Hielo intervention; swap is batch roll, contexts not all matched, exploratory only')
  for kind in ['obsolete','current']:
   pairs=[(r,changed(r,kind)) for r in rr];pairs=[(a,b) for a,b in pairs if b is not None]
   if not pairs:continue
   a=[a for a,b in pairs];b=[b for a,b in pairs];pa=m(torch.tensor([r['ids'] for r in a]))[:,-1].argmax(-1);pb=m(torch.tensor([r['ids'] for r in b]))[:,-1].argmax(-1);ya=torch.tensor([r['label'] for r in a]);yb=torch.tensor([r['label'] for r in b]);_,_,aa,yy,_,ta,en=forward(m,d,a);_,_,bb,zz,_,tb,_=forward(m,d,b)
   res[kind]=dict(n=len(a),original_accuracy=float((pa==ya).float().mean()),changed_accuracy=float((pb==yb).float().mean()),joint_correct=float(((pa==ya)&(pb==yb)).float().mean()),prediction_invariance=float((pa==pb).float().mean()),aux_pair_joint=float(((aa.argmax(-1)==yy)&(bb.argmax(-1)==zz)).float().mean()),memory_distance_after_event=float((ta[2]['memory']-tb[2]['memory']).norm(dim=(-2,-1)).mean()))
  # Paired same final visible query/distractors; donor differs only in current queried value.
  donors=[changed(r,'current') for r in rr];_,donor_trace=m(torch.tensor([r['ids'] for r in donors]),trace=True);head=m.core.memory_head;original=head._read;counter=[0]
  def patched(xx,mem):
   j=counter[0];counter[0]+=1
   return original(xx,donor_trace[6]['memory'] if j==7 else mem)
  head._read=patched
  try:sw=m(x)[:,-1].argmax(-1)
  finally:head._read=original
  res['compatible_current_donor']=dict(n=len(rr),follows_donor=float((sw==torch.tensor([r['label'] for r in donors])).float().mean()),joint_original_and_donor=float(((p==target)&(sw==torch.tensor([r['label'] for r in donors]))).float().mean()))
 return res

def main():
 tests()
 for c in 'ABCD':
  m,d,o,rng=setup();s=torch.load(R/'results'/f'{c}.pt',weights_only=True);m.load_state_dict(s['model'],strict=True);d.load_state_dict(s['decoder'],strict=True)
  dump(R/'results'/f'{c}-interventions.json',probes(c,m,d,fixture(c)))
 for p in (R/'results').glob('*.pt'):
  s=torch.load(p,weights_only=True)
  # Correct dataset identity in derived sidecar; do not rewrite trained checkpoint.
  if p.stem in 'ABCD':dump(p.with_suffix('.identity.json'),dict(actual_dataset_sha256=hashlib.sha256(json.dumps(fixture(p.stem)).encode()).hexdigest(),note='Embedded dataset_sha is A fixture reference shared by certification; use this per-arm sidecar.'))
if __name__=='__main__':main()
