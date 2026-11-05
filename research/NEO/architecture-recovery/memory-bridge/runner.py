from setup import *
P=json.loads((CODE/'protocol.json').read_text())

def model(arm,seed=17):return create('ice' if arm=='ice' else 'no_ice',seed)
def tensors(rows):
 seq=[r['prefix']+r['query'] for r in rows];lengths=torch.tensor([len(x) for x in seq]);n=((int(lengths.max())+15)//16)*16;x=torch.full((len(rows),n),256,dtype=torch.long)
 for i,s in enumerate(seq):x[i,:len(s)]=torch.tensor(s)
 return x,lengths-1,torch.tensor([r['answer'] for r in rows])

def logits(m,rows,arm,trace=False):
 x,last,labels=tensors(rows);hlast=m.emb.weight.new_zeros(len(rows),32);memory=m.emb.weight.new_zeros(len(rows),8,32);states=[]
 if arm=='full':
  h,_=m.chunk_hidden(x,memory,False);hlast=h[torch.arange(len(rows)),last]
 else:
  for start in range(0,x.shape[1],16):
   h,memory=m.chunk_hidden(x[:,start:start+16],memory,True);hlast=torch.where((last//16==start//16)[:,None],h[torch.arange(len(rows)),last%16],hlast)
   if trace:
    memory.retain_grad() if memory.requires_grad else None;states.append(memory)
 y=F.linear(hlast,m.emb.weight);return (y,states) if trace else y

def order(rows,seed=17):
 idx=list(range(len(rows)));random.Random(seed).shuffle(idx);return idx

def update(m,opt,rows,cursor,arm,seed=17):
 idx=order(rows,seed);batch=[rows[idx[(cursor*P['batch']+j)%len(idx)]] for j in range(P['batch'])];opt.zero_grad(set_to_none=True);start=time.perf_counter();y=logits(m,batch,arm);ce=F.cross_entropy(y,torch.tensor([r['answer'] for r in batch]));ce.backward();grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};assert all(math.isfinite(g) for g in grads.values());assert math.isfinite(float(ce.detach()));torch.nn.utils.clip_grad_norm_(m.parameters(),1);opt.step();return {'update':cursor+1,'ce_answer':float(ce.detach()),'seconds':time.perf_counter()-start,'responses':len(batch),'input_ids':sum(len(r['prefix'])+len(r['query']) for r in batch),'gradients':grads}

def checkpoint(path,m,opt,cursor,rows,arm,seed):
 if path.exists():raise FileExistsError(path)
 torch.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'cursor_updates':cursor,'cursor_samples':cursor*P['batch'],'order':order(rows,seed),'dataset_sha':digest(rows),'tokenizer':FP,'model_source_sha':file_sha(BASE/'language-bridge/model.py'),'protocol':P,'arm':arm,'seed':seed,'microsteps':cursor,'accumulation':1,'scheduler':None,'pending_gradients':None},path)

def restore(path,rows):
 c=torch.load(path,weights_only=True);assert c['dataset_sha']==digest(rows) and c['tokenizer']==FP and c['protocol']==P and c['model_source_sha']==file_sha(BASE/'language-bridge/model.py') and c['order']==order(rows,c['seed']);m=model(c['arm'],c['seed']);m.load_state_dict(c['model']);o=optimizer(m);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c

def evaluate(m,rows,arm):
 result=[];m.eval()
 with torch.no_grad():
  for start in range(0,len(rows),32):
   batch=rows[start:start+32];y=logits(m,batch,arm);ce=F.cross_entropy(y,torch.tensor([r['answer'] for r in batch]),reduction='none');pred=y.argmax(-1)
   for i,r in enumerate(batch):result.append({'id':r['example_id'],'program':r['program_id'],'entity':r['query_entity'],'lang':r['lang'],'role':r['role'],'gold':r['gold'],'answer_id':r['answer'],'pred_id':int(pred[i]),'pred_value':r['choices'].index(int(pred[i])) if int(pred[i]) in r['choices'] else -1,'correct':int(pred[i])==r['answer'],'ce':float(ce[i]),'layout':r['layout'],'distance':r['distance']})
 return result

def aggregate(pred):
 groups={}
 for r in pred:
  for k in ['all',r['lang'],r['role'],f"{r['lang']}/{r['role']}",f"layout-{r['layout']}",f"distance-{r['distance']}"]:
   a=groups.setdefault(k,{'n':0,'correct':0,'ce':0.});a['n']+=1;a['correct']+=r['correct'];a['ce']+=r['ce']
 for a in groups.values():a['accuracy']=a['correct']/a['n'];a['nll_answer']=a.pop('ce')/a['n']
 progs={}
 for r in pred:progs.setdefault(r['program'],[]).append(r['correct'])
 groups['joint']={'n':len(progs),'accuracy':sum(all(v) for v in progs.values())/len(progs)};return groups

def train(arm,rows,steps,tag,seed=17):
 path=OUT/'results'/f'{tag}.pt'
 if path.exists():raise FileExistsError(path)
 m=model(arm,seed);o=optimizer(m);curves=[];start=time.perf_counter();m.train()
 for cursor in range(steps):
  curves.append(update(m,o,rows,cursor,arm,seed))
  if (cursor+1)%50==0:print(tag,cursor+1,curves[-1]['ce_answer'],flush=True)
 elapsed=time.perf_counter()-start;checkpoint(path,m,o,steps,rows,arm,seed);pred=evaluate(m,rows,arm);summary={'arm':arm,'seed':seed,'steps':steps,'responses':steps*P['batch'],'parameters_allocated':sum(p.numel() for p in m.parameters()),'parameters_active':sum(p.numel() for p in m.parameters() if p.requires_grad),'train':aggregate(pred),'curves':curves,'seconds_train':elapsed,'input_ids_s':sum(r['input_ids'] for r in curves)/elapsed,'responses_s':steps*P['batch']/elapsed,'peak_process_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'initialization_sha':digest({k:file_sha(BASE/'language-bridge/model.py') for k in ['model']})};save_json(tag,summary);save_json(tag+'-train-predictions',pred);return m,summary

def main():
 pre=read('engineering');assert pre['passed'];assert read('positive-controls')['passed'];micro=read('micro');m,r=train('full',micro,P['microfit_full_updates'],'micro-full-17');ok=r['train']['all']['accuracy']>=P['microfit_full_exact_train_min'] and r['train']['all']['nll_answer']<P['microfit_full_answer_ce_max'];save_json('micro-gate',{'passed':ok,'metrics':r['train']['all'],'rule':'accuracy>=.95 and CE<.3 fixed before training; no budget extension'})
 if not ok:print('STOP: full-context microfit did not pass. No primary training.');return
 rows=read('train');results={}
 for arm in ['full','no_ice','ice']:
  m,r=train(arm,rows,P['updates'],f'{arm}-17');evaluations={}
  for name in ['dev-combinations','dev-structures']:
   pred=evaluate(m,read(name),arm);save_json(f'{arm}-17-{name}-predictions',pred);evaluations[name]=aggregate(pred)
  save_json(f'{arm}-17-dev',evaluations);results[arm]=evaluations
 save_json('primary-dev',results)
if __name__=='__main__':main()
