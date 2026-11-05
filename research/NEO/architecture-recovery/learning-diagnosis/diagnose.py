from pathlib import Path
import sys,json,hashlib,time,random,math,resource
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'foreground-binding'))
import harness as h
import torch
import torch.nn.functional as F
from collections import Counter
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
def put(n,d):
 p=OUT/(n+'.json');assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
def stats(m,rows,save=None):
 m.eval()
 with torch.no_grad():y=h.logits(m,rows);labels=torch.tensor([r['answer'] for r in rows]);ce=F.cross_entropy(y,labels,reduction='none');prob=y.softmax(-1);pred=y.argmax(-1)
 if save:torch.save({'logits_full_vocab':y,'labels':labels,'ids':h.tensors(rows)[0],'last_positions':h.tensors(rows)[1]},OUT/(save+'.pt'))
 return {'ce':float(ce.mean()),'accuracy':float((pred==labels).float().mean()),'min_p_correct':float(prob[torch.arange(len(rows)),labels].min()),'mean_p_correct':float(prob[torch.arange(len(rows)),labels].mean()),'pred_counts':dict(Counter(pred.tolist())),'rows':[{'id':r['example_id'],'target':r['answer'],'pred':int(pred[i]),'p_correct':float(prob[i,labels[i]]),'ce':float(ce[i]),'four_logits':y[i,r['choices']].tolist(),'four_probs_full_softmax':prob[i,r['choices']].tolist(),'valid_mass':float(prob[i,r['choices']].sum())} for i,r in enumerate(rows)]}
def grad_detail(m,rows):
 m.zero_grad(set_to_none=True);y=h.logits(m,rows);y.retain_grad();labels=torch.tensor([r['answer'] for r in rows]);ce=F.cross_entropy(y,labels);ce.backward()
 ps={n:{'grad_norm':float(p.grad.norm()),'weight_norm':float(p.norm()),'grad_max':float(p.grad.abs().max())} for n,p in m.named_parameters() if p.grad is not None}
 norm=math.sqrt(sum(v['grad_norm']**2 for v in ps.values()))
 return {'ce':float(ce.detach()),'parameters':ps,'global_grad_norm':norm,'clip_scale':min(1.,1/(norm+1e-6)),'correct_logit_gradient':y.grad[torch.arange(len(rows)),labels].tolist(),'gradient_ce_matches_softmax':bool(torch.allclose(y.grad,(y.detach().softmax(-1)-F.one_hot(labels,8192))/len(rows),atol=1e-7))}
def forensic():
 result={};full={}
 ds=h.data()
 for arm in 'ABC':
  initial,_,_=h.restore(BASE/'foreground-binding/results'/f'{arm}-17-initial.pt',ds['train']);final,opt,cp=h.restore(BASE/'foreground-binding/results'/f'{arm}-17-final.pt',ds['train'])
  tr=h.get(f'{arm}-17-training');res={'initial':{},'final':{},'gradients':{},'parameter_deltas':{},'historical_curves_available':'CE and gradient norms only; no intermediate full-logit checkpoints'}
  for phase,m in [('initial',initial),('final',final)]:
   for split,rows in ds.items():res[phase][split]=stats(m,rows,f'forensic-{arm}-{phase}-{split}')
   res['gradients'][phase]=grad_detail(m,ds['train'])
  for n,p in final.named_parameters():
   q=dict(initial.named_parameters())[n];res['parameter_deltas'][n]={'norm_initial':float(q.detach().norm()),'norm_final':float(p.detach().norm()),'delta_norm':float((p-q).detach().norm()),'relative_delta':float((p-q).detach().norm()/(q.detach().norm()+1e-12)),'trainable':p.requires_grad}
  ys=h.logits(final,ds['train']).detach();res['query_pair_logit_max_deltas']=[float((ys[i]-ys[i+1]).abs().max()) for i in range(0,48,2)]
  res['last_train_minibatch_ce_before_update']=tr['curves'][-1]['ce_answer'];idx=h.order(ds['train'],17);batch=[ds['train'][idx[(399*8+j)%48]] for j in range(8)];res['same_last_batch_post_update']=stats(final,batch)
  res['all_minibatches_post_update_ce']=[stats(final,[ds['train'][idx[(i*8+j)%48]] for j in range(8)])['ce'] for i in range(6)]
  res['mean_last_6_logged_ce']=sum(c['ce_answer'] for c in tr['curves'][-6:])/6
  active={id(p) for p in final.parameters() if p.requires_grad};covered=[id(p) for g in opt.param_groups for p in g['params']];assert active==set(covered) and len(covered)==len(active)
  res['optimizer_coverage_exact']=True;res['optimizer_groups']=[{k:v for k,v in g.items() if k!='params'} for g in opt.param_groups]
  res['curve_checkpoints']=[{k:c[k] for k in ['update','ce_answer','gradients']} for c in tr['curves'] if c['update'] in [1,10,50,100,200,300,400]]
  result[arm]=res
 put('forensics',result)
 print('FORENSICS COMPLETE',flush=True)
def datasets():
 ds=h.data();rows=ds['train'];a,b=rows[:2];sw=[r for r in rows if r['order']==a['order'] and r['values']==list(reversed(a['values']))]
 assert len(sw)==2
 return {'1':rows[:1],'2':rows[:2],'3':rows[:2]+sw,'4':rows}
def snapshot(path,m,opt,cursor,rows):
 assert not path.exists();torch.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'cursor':cursor,'samples':cursor*8,'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'dataset_sha':h.digest(rows),'order':h.order(rows,17),'tokenizer_sha':h.file_sha(h.ARTIFACT),'protocol':json.loads((ROOT/'PROTOCOL.json').read_text()),'model_code_sha':h.sources(),'script_sha':h.file_sha(Path(__file__))},path)
def restore(path,rows):
 c=torch.load(path,weights_only=True);assert c['dataset_sha']==h.digest(rows) and c['order']==h.order(rows,17) and c['tokenizer_sha']==h.file_sha(h.ARTIFACT) and c['model_code_sha']==h.sources() and c['script_sha']==h.file_sha(Path(__file__)) and c['protocol']==json.loads((ROOT/'PROTOCOL.json').read_text());m=h.model('B');m.load_state_dict(c['model']);o=h.optimizer(m);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c

def train_level(level,rows,updates):
 m=h.model('B');opt=h.optimizer(m);curves=[];start=time.perf_counter();idx=h.order(rows,17);assert not (OUT/f'level-{level}-final.pt').exists()
 for u in range(updates):
  batch=[rows[idx[(u*8+j)%len(rows)]] for j in range(8)];before={n:p.detach().clone() for n,p in m.named_parameters() if p.requires_grad};m.train();opt.zero_grad(set_to_none=True);ys=h.logits(m,batch);ce=F.cross_entropy(ys,torch.tensor([r['answer'] for r in batch]));ce.backward();grads={n:float(p.grad.norm()) for n,p in m.named_parameters() if p.grad is not None};norm=float(torch.nn.utils.clip_grad_norm_(m.parameters(),1));opt.step()
  delta={n:float((p.detach()-before[n]).norm()) for n,p in m.named_parameters() if n in before};assert math.isfinite(float(ce.detach())) and all(math.isfinite(v) for v in grads.values());rec={'update':u+1,'ce_pre_update_minibatch':float(ce.detach()),'gradients':grads,'pre_clip_norm':norm,'clip_scale':min(1.,1/(norm+1e-6)),'parameter_update_norms':delta}
  if u==0 or (u+1)%25==0 or u==updates-1:rec['full_train_post_update']=stats(m,rows,f'level-{level}-step-{u+1}-logits')
  curves.append(rec)
 elapsed=time.perf_counter()-start;snapshot(OUT/f'level-{level}-final.pt',m,opt,updates,rows);ev=stats(m,rows,f'level-{level}-final-logits');passed=ev['accuracy']==1 and ev['ce']<=.1 and ev['min_p_correct']>=.9
 out={'level':level,'updates':updates,'examples':len(rows),'seconds':elapsed,'peak_rss_mib_process':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'train':ev,'passed':passed,'curves':curves,'final_gradient':grad_detail(m,rows),'dev':{k:stats(m,v) for k,v in h.data().items() if k!='train'}};put(f'level-{level}',out);print('LEVEL',level,'acc',ev['accuracy'],'ce',ev['ce'],'min_p',ev['min_p_correct'],'PASS',passed,flush=True);return m,out

def ladder():
 assert json.loads((OUT/'signal-contracts.json').read_text())['passed'];data=datasets();put('ladder-datasets',data);p=json.loads((ROOT/'PROTOCOL.json').read_text());completed=[]
 for level,rows in data.items():
  m,res=train_level(level,rows,p['updates'][level]);completed.append(level)
  if not res['passed']:
   put('ladder-decision',{'first_failed_level':level,'completed':completed,'next_levels':'NOT EXECUTED','extra_interventions':'NOT EXECUTED: no demonstrated implementation cause yet'});return
 put('ladder-decision',{'first_failed_level':None,'completed':completed,'next_levels':'none'})
if __name__=='__main__':
 {'forensic':forensic,'ladder':ladder}[sys.argv[1]]()
