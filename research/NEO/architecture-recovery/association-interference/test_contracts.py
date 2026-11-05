"""Additional independent data/mask checks; does not run training."""
from interference_runner import *
def main():
 m,d,o,rng=setup();rr=fixture('D')[:8];x=torch.tensor([r['ids'] for r in rr]);valid=torch.ones_like(x,dtype=torch.bool);valid[:,56:]=False
 with torch.no_grad():
  a,tr=m(x,valid=valid,trace=True);xx=x.clone();xx[:,56:]=127;b,tt=m(xx,valid=valid,trace=True);assert torch.equal(a,b);assert torch.equal(tr[6]['memory'],tt[6]['memory'])
  # Exact auxiliary CE at chunk2 cannot depend on suffix beyond its boundary.
  y,trace=m(x,trace=True);xx=x.clone();xx[:,24:]=120;z,t=m(xx,trace=True)
  entities=torch.tensor([i%5 for i in range(8)]);targets=torch.tensor([i%4 for i in range(8)])
  assert torch.equal(F.cross_entropy(d(trace[2]['memory'].flatten(1),entities),targets),F.cross_entropy(d(t[2]['memory'].flatten(1),entities),targets))
  for j in [0,2]:
   diff=(trace[j]['memory']-m(x[:,:8*(j+1)],trace=True)[1][-1]['memory']).abs();print('prefix state max abs',j,float(diff.max()));assert torch.allclose(trace[j]['memory'],m(x[:,:8*(j+1)],trace=True)[1][-1]['memory'],atol=1e-5,rtol=1e-5)
 # The exact same target order is independently reconstructed.
 for c in 'ABCD':
  rows=fixture(c);target_list=entries(rows)
  independent=[]
  for bi,r in enumerate(rows):
   state={}
   for i,(op,e,v) in enumerate(r['ops']):
    if op in '=!':state[e]=int(v)
    if i in [1,5]:
     for ee in sorted([r['q'],r['other']]):independent.append((bi,i//2,'ABCDE'.index(ee),state[ee]))
  assert independent==target_list
 dump(R/'results/additional-tests.json',dict(padding_invariance=True,aux_ce_future_invariance=True,prefix_only_state_equivalence=True,independent_target_identity_order=True))
 print('PASS additional contracts')
if __name__=='__main__':main()
