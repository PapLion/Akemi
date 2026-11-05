from diagnose import *
def loss(m,rows):
 x,last,labels=h.tensors(rows);hidden,_=m.chunk_hidden(x,torch.zeros(len(rows),8,32),False);answer=F.linear(hidden[torch.arange(len(rows)),last],m.emb.weight);ac=F.cross_entropy(answer,labels);hs=[];targets=[];positions=[]
 for i,r in enumerate(rows):
  start=len(r['prefix'])-r['fact_tokens'];end=len(r['prefix']);assert start>0 and r['prefix'][start:]==h.TOK.encode(r['facts'])
  pos=torch.arange(start-1,end-1);hs.append(hidden[i,pos]);targets.extend(r['prefix'][start:end]);positions.append(pos.tolist())
 hs=torch.cat(hs);labels_fact=torch.tensor(targets);fy=F.linear(hs,m.emb.weight);fc=F.cross_entropy(fy,labels_fact);return ac+.1*fc,ac,fc,positions,labels_fact,fy

def certify():
 rows=datasets()['4'][:8];m=h.model('B');total,ac,fc,pos,labels,fy=loss(m,rows);assert torch.equal(ac,F.cross_entropy(h.logits(m,rows),torch.tensor([r['answer'] for r in rows])));assert torch.allclose(total-ac,.1*fc,atol=1e-7);assert len(labels)==sum(r['fact_tokens'] for r in rows);assert all(max(p)<len(r['prefix'])-1 for p,r in zip(pos,rows));assert torch.allclose(fc,-fy.log_softmax(-1)[torch.arange(len(labels)),labels].mean());total.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters() if p.requires_grad)
 # The masked positions are unchanged by modifying later query tokens.
 x,last,lab=h.tensors(rows);changed=x.clone()
 for i,r in enumerate(rows):changed[i,len(r['prefix']):]=(changed[i,len(r['prefix']):]+1)%8192
 a,_=m.chunk_hidden(x,torch.zeros(8,8,32),False);b,_=m.chunk_hidden(changed,torch.zeros(8,8,32),False)
 for i,p in enumerate(pos):assert torch.equal(a[i,p],b[i,p])
 put('dense-contracts',{'passed':True,'answer_loss_unchanged':True,'causal_factual_mask':True,'factual_targets_per_batch':len(labels),'data_sha':h.digest(datasets()['4']),'protocol_sha':h.file_sha(ROOT/'DENSE_PROTOCOL.json'),'mask_positions':pos,'labels':labels.tolist()})

def main():
 decision=json.loads((OUT/'ladder-decision.json').read_text());assert decision['first_failed_level']=='4';certify();rows=datasets()['4'];m=h.model('B');opt=h.optimizer(m);idx=h.order(rows,17);curves=[];start=time.perf_counter()
 for u in range(400):
  batch=[rows[idx[(u*8+j)%48]] for j in range(8)];m.train();opt.zero_grad(set_to_none=True);total,ac,fc,pos,labels,fy=loss(m,batch);total.backward();gr={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert all(math.isfinite(g) for g in gr.values());norm=float(torch.nn.utils.clip_grad_norm_(m.parameters(),1));opt.step();rec={'update':u+1,'loss_total':float(total.detach()),'ce_answer':float(ac.detach()),'ce_facts':float(fc.detach()),'gradients':gr,'pre_clip_norm':norm,'answer_targets':8,'fact_targets':len(labels)}
  if u==0 or (u+1)%25==0:rec['train_answer']=stats(m,rows,f'dense-step-{u+1}-logits')
  curves.append(rec)
 snapshot(OUT/'dense-final.pt',m,opt,400,rows)
 # Extra objective identity belongs alongside checkpoint and is checked here.
 put('dense-checkpoint-contract',{'checkpoint_sha':h.file_sha(OUT/'dense-final.pt'),'dense_protocol_sha':h.file_sha(ROOT/'DENSE_PROTOCOL.json'),'baseline_protocol_sha':h.file_sha(ROOT/'PROTOCOL.json'),'script_sha':h.file_sha(Path(__file__))})
 res={'train':stats(m,rows,'dense-final-logits'),'dev':{k:stats(m,v,f'dense-{k}-logits') for k,v in h.data().items() if k!='train'},'functional':{k:h.evaluate(m,v)[0] for k,v in h.data().items()},'curves':curves,'seconds':time.perf_counter()-start,'responses':3200,'fact_targets':sum(r['fact_targets'] for r in curves),'final_gradient':grad_detail(m,rows)};put('dense-result',res);print('DENSE',res['train']['accuracy'],res['train']['ce'],flush=True)
if __name__=='__main__':main()
