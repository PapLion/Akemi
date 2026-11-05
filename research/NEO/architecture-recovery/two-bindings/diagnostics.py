from two_bindings import *
def counterfactual(r,kind):
 s=copy.deepcopy(r);entity=r['affected'] if kind=='obsolete' else r['q']
 indices=[i for i,(op,e,v) in enumerate(s['ops']) if op in '=!' and e==entity]
 index=indices[0] if kind=='obsolete' else indices[-1];s['ops'][index][2]=str((int(s['ops'][index][2])+1)%4)
 z=P.make_record(s['ops'],s['q'],'counterfactual','diagnostic');s.update(ids=z['ids'],label=z['label']);return s

def grad_diagnostics(m,d,rows):
 batch=[rows[i] for i in range(0,len(rows),20)];params=[p for p in m.parameters() if p.requires_grad];lm,a,b,_,_=losses(m,d,batch)
 grads=[]
 for term in [lm,a[0],b[0]]:
  g=torch.autograd.grad(term,params,allow_unused=True,retain_graph=True);grads.append(torch.cat([(torch.zeros_like(p) if x is None else x).flatten() for p,x in zip(params,g)]))
 def cosine(a,b):return float(F.cosine_similarity(a,b,dim=0))
 return dict(lm_norm=float(grads[0].norm()),initial_norm=float(grads[1].norm()),post_norm=float(grads[2].norm()),cosine_initial_post=cosine(grads[1],grads[2]),cosine_initial_lm=cosine(grads[1],grads[0]),scope='fixed 16-program batch, model trainable params only; raw terms before .1 weighting/clipping')

def main():
 out=R/'results';rows=data();allresults={}
 for arm in 'AB':
  m,d,o,rng,step=restore(out/f'{arm}-150.pt',rows,arm);g=grad_diagnostics(m,d,rows);probes={}
  for kind in ['obsolete','current']:
   source=[r for r in rows if kind=='current' or r['kind']=='correct'];target=[counterfactual(r,kind) for r in source]
   aa,_=evaluate(m,d,source);bb,_=evaluate(m,d,target);pairs=[]
   for a,b,r in zip(aa['predictions'],bb['predictions'],source):
    post_a=a['stages']['post'];post_b=b['stages']['post'];pairs.append(dict(id=r['id'],query_corrected=r['affected']==r['q'],original_correct=a['original_prediction']==a['original_label'],changed_correct=b['original_prediction']==b['original_label'],original_invariant=a['original_prediction']==b['original_prediction'],post_joint_both_versions=all(x==y for x,y in zip(post_a['pred'],post_a['label'])) and all(x==y for x,y in zip(post_b['pred'],post_b['label'])),post_query_joint=post_a['pred'][0]==post_a['label'][0] and post_b['pred'][0]==post_b['label'][0],post_other_joint=post_a['pred'][1]==post_a['label'][1] and post_b['pred'][1]==post_b['label'][1]))
   metrics={}
   for group in ['all','query_corrected','other_corrected']:
    pp=[p for p in pairs if group=='all' or p['query_corrected']==(group=='query_corrected')]
    metrics[group]=dict(n=len(pp),original_joint=sum(p['original_correct'] and p['changed_correct'] for p in pp)/len(pp),original_invariance=sum(p['original_invariant'] for p in pp)/len(pp),post_joint_both_versions=sum(p['post_joint_both_versions'] for p in pp)/len(pp),post_query_joint=sum(p['post_query_joint'] for p in pp)/len(pp),post_other_joint=sum(p['post_other_joint'] for p in pp)/len(pp))
   probes[kind]=dict(metrics=metrics,pairs=pairs)
  # Matched donor differs only in CURRENT query value; final block identical.
  tally=collections.Counter()
  with torch.no_grad():
   for start in range(0,len(rows),16):
    batch=rows[start:start+16];donors=[counterfactual(r,'current') for r in batch];x=torch.tensor([r['ids'] for r in batch]);dx=torch.tensor([r['ids'] for r in donors]);assert torch.equal(x[:,48:],dx[:,48:]);base=m(x)[:,-1].argmax(-1);_,tr=m(dx,trace=True)
    head=m.core.memory_head;read=head._read;counter=[0]
    def patched(xx,mem):
     j=counter[0];counter[0]+=1;return read(xx,tr[6]['memory'] if j==7 else mem)
    head._read=patched
    try:pred=m(x)[:,-1].argmax(-1)
    finally:head._read=read
    y=torch.tensor([r['label'] for r in batch]);dy=torch.tensor([r['label'] for r in donors]);tally['n']+=len(batch);tally['joint']+=int(((base==y)&(pred==dy)).sum());tally['donor_correct']+=int((pred==dy).sum())
  allresults[arm]=dict(gradients=g,counterfactuals=probes,compatible_donor=dict(tally))
 dump(out/'diagnostics.json',allresults)
 print({a:{'gradients':r['gradients'],'donor':r['compatible_donor']} for a,r in allresults.items()})
if __name__=='__main__':main()
