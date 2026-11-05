import copy,json,datetime,hashlib,collections,random
import torch
import torch.nn.functional as F
import trapos_train as T
D=T.D;M=T.M;R=T.R;O=T.O

def main():
 assert not (O/'FREEZE.json').exists();rows=D.train(17);sets=D.dev();trainids={r['id'] for r in rows};overlap={name:sum(r['id'] in trainids for r in rr) for name,rr in sets.items()};assert not any(overlap.values())
 # Independent exact dictionary with parser-derived semantics is a diagnostic, not a neural result.
 for name,rr in [('train',rows),*sets.items()]:
  for r in rr:
   state,labels=D.oracle(r);assert labels==r['labels'] and state[r['q']]+48==r['label'] and state[r['other']]+48==r['other_label']
  T.dump('data-'+name,rr);T.dump('frequencies-'+name,D.frequencies(rr))
 # Each opcode appears on both accepted/rejected proposals. A single surface token is insufficient.
 for op,counts in D.frequencies(rows)['opcode_labels'].items():assert counts['True'] and counts['False']
 report={'positive_exact_dictionary_accuracy':1.,'oracle_targets_and_proposals':True,'dev_train_overlap':overlap,'independent_parse':True}
 rr=rows[:8];xx,yy,mask=M.inputs(rr);m,o=M.setup(17,'C');n,p=M.setup(17,'A');assert D.S.A.I.equal(m.state_dict(),n.state_dict())
 pars=[p for p in m.parameters() if p.requires_grad];opt=[p for g in o.param_groups for p in g['params']];assert len(opt)==len(set(map(id,opt)))==len(pars) and set(map(id,opt))==set(map(id,pars))
 for mode in [False,True]:
  m.train(mode);logits,tr=M.forward(m,rr,trace=True)
  for cut in [1,4,8,12,16,24,32,40,48,64,80,88]:
   changed=xx.clone();changed[:,cut:]=120;ll,tt=m.core(changed,trace=True);assert torch.equal(logits[:,:cut],ll[:,:cut])
   for a,b in zip(tr,tt):
    for wa,wb in zip(a['writes'],b['writes']):
     early=wa['end_index']<cut
     if early.any():assert torch.equal(wa['score'][early],wb['score'][early])
  assert torch.allclose(m(xx.flip(0)).flip(0),logits,atol=1e-5,rtol=1e-5)
  joined=torch.cat([xx[:1],xx[1:2]],1);doc=torch.cat([torch.zeros_like(xx[:1]),torch.ones_like(xx[1:2])],1);assert torch.allclose(m(joined,doc)[:,96:],logits[1:2],atol=1e-5,rtol=1e-5)
  valid=torch.ones_like(xx,dtype=torch.bool);valid[:,88:]=False;changed=xx.clone();changed[:,88:]=127;assert torch.equal(m(xx,valid=valid),m(changed,valid=valid))
 # All rejected means exactly zero Hielo; original rule preserved on every accepted write.
 m.eval();_,tr=M.forward(m,rr,trace=True,override='none');assert all(torch.count_nonzero(t['memory'])==0 for t in tr)
 _,tr=M.forward(m,rr,trace=True,override='all');changes=[]
 for t in tr:
  for w in t['writes']:
   candidates=w['candidate']
   if candidates.any():
    expected=w['before']+w['key'][:,:,None]*(w['value']-(w['key'][:,None]@w['before'])[:,0])[:,None,:]
    assert torch.allclose(w['after'][candidates],expected[candidates],atol=1e-5,rtol=1e-5);changes.extend((w['after']-w['before']).norm(dim=(-2,-1))[candidates].tolist())
 assert max(changes)>0
 # BCE-only gradients reach actual filter and causal representations; real AdamW alters policy.
 m.train();_,tr=M.forward(m,rr,trace=True);score,gate,label,typ=M.selection(tr,rr);o.zero_grad(set_to_none=True);F.binary_cross_entropy_with_logits(score,label).backward();gr={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert gr['core.trapos.0.weight']>0 and gr['core.trapos.2.weight']>0
 before=copy.deepcopy(m.core.trapos.state_dict());o.step();assert not D.S.A.I.equal(before,m.core.trapos.state_dict())
 # Oracle argument is rejected in normal C inference.
 try:m.core(xx,oracle_mask=mask)
 except ValueError:pass
 else:raise AssertionError('oracle leaked into C')
 # Deterministic stateless random decisions, batch/doc independent.
 rb,ro=M.setup(17,'B');rb.eval();one=rb(xx);assert torch.equal(one,rb(xx));assert torch.allclose(rb(xx.flip(0)).flip(0),one,atol=1e-5,rtol=1e-5)
 joined=torch.cat([xx[:1],xx[1:2]],1);doc=torch.cat([torch.zeros_like(xx[:1]),torch.ones_like(xx[1:2])],1);assert torch.allclose(rb(joined,doc)[:,96:],one[1:2],atol=1e-5,rtol=1e-5)
 resume={}
 for arm in ['A','B','C','D']:
  m,o=M.setup(17,arm);logs=[T.update(m,o,rows[i*8:i*8+8]) for i in range(4)];T.save(O/(arm+'-resume.pt'),m,o,17,arm,4,rows)
  logs=[T.update(m,o,rows[i*8:i*8+8]) for i in range(4,10)];end=copy.deepcopy((m.state_dict(),o.state_dict(),torch.get_rng_state(),random.getstate()))
  n,p,s=T.restore(O/(arm+'-resume.pt'),rows);logs2=[T.update(n,p,rows[i*8:i*8+8]) for i in range(4,10)];assert logs==logs2 and D.S.A.I.equal(end,(n.state_dict(),p.state_dict(),torch.get_rng_state(),random.getstate()));resume[arm]=True
 report.update(passed=True,causality_train_eval_and_scores=True,mask_padding_doc_batch=True,optimizer_exact=True,no_write_zero=True,delta_unchanged=True,filter_gradients=gr,filter_real_update=True,oracle_api_forbidden=True,random_causal_deterministic=True,resume10_vs4plus6_exact=resume)
 T.dump('preflight',report);(R/'protocol.json').write_text(json.dumps(T.PROTOCOL,indent=2)+'\n');T.dump('FREEZE',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in ['trapos_data.py','trapos_model.py','trapos_train.py','preflight.py','protocol.json']},'train_sha':D.digest(rows),'dev_sha':{k:D.digest(v) for k,v in sets.items()},'stage':'BEFORE MAIN TRAINING'})
 print('ALL PREFLIGHT CONTRACTS PASS',flush=True)
if __name__=='__main__':main()
