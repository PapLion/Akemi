from run import *

def main():
 out={};before=read('attention-before');after=read('attention-after')
 for fmt in ['A','B']:
  ds=dataset(fmt);m,o,cp=restore(ROOT/'results'/f'short-{fmt}-17.pt',ds['train']);idx=order(ds['train'],17);consumed=[ds['train'][idx[(8*u+j)%48]] for u in range(200) for j in range(8)]
  position={};attention=[]
  for split,rows in ds.items():
   pred=evaluate(m,rows,'full');position[split]={}
   for order_id in [0,1]:
    select=[p for p,r in zip(pred,rows) if r['order']==order_id];position[split][str(order_id)]={'n':len(select),'accuracy':sum(p['correct'] for p in select)/len(select)}
   for start in range(0,len(rows),2):
    summary,_=inspect_attention(m,rows[start:start+2]);attention.append({'split':split,'program':rows[start]['program_id'],**summary})
  # A learned colour key does not encode preceding entity in this one attention layer.
  rows=ds['train'][:2];x,last,_=tensors(rows);embedding=m.emb(x).detach().requires_grad_();k=m.blocks[0].k(m.blocks[0].n1(embedding));factstart=97;valuepos=next(i for i in range(factstart,len(rows[0]['prefix'])) if int(x[0,i])==rows[0]['choices'][rows[0]['values'][0]])
  gradient=torch.autograd.grad(k[0,valuepos].sum(),embedding)[0];off=gradient.clone();off[0,valuepos]=0
  assert torch.count_nonzero(off)==0
  trainpred=evaluate(m,ds['train'],'full');newpred=evaluate(m,ds['dev-combinations'],'full')
  same_old=None
  if fmt=='A':
   oldpath=ROOT.parent.parent/'cryo-language-binding-diagnostic-v1/binding-diagnostic/results/short-17.pt'
   if oldpath.exists():
    old=torch.load(oldpath,weights_only=True);same_old=all(torch.equal(v,old['model'][k]) for k,v in m.state_dict().items());assert same_old
  out[fmt]={'initial_weights_sha':read('initial-identity')['weights_sha'],'replicates_previous_A_weights_exactly':same_old,'answer_counts':dict(Counter(r['gold'] for r in consumed)),'query_side_counts':dict(Counter(r['query_side'] for r in consumed)),'entity_value_counts':{str(k):v for k,v in Counter((r['query_side'],r['gold']) for r in consumed).items()},'train_prediction_counts':dict(Counter(p['pred_id'] for p in trainpred)),'dev_pair_prediction_counts':dict(Counter(p['pred_id'] for p in newpred)),'order_accuracy':position,'colour_key_embedding_gradient_nonlocal_nonzeros':int(torch.count_nonzero(off)),'colour_key_local_gradient_norm':float(gradient[0,valuepos].norm()),'response_query_gradient':conditioning(m,ds['train']),'steps':cp['cursor_updates'],'samples':cp['cursor_samples'],'optimizer_states':len(o.state),'checkpoint_sha':file_sha(ROOT/'results'/f'short-{fmt}-17.pt')}
  save_json(fmt+'-attention-all-panels',attention)
 save_json('diagnostics',out)
if __name__=='__main__':main()
