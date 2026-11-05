from model import *
import random,time,resource,math

def records():return json.loads((ROOT/'results/data.json').read_text())
def windows(split):
 out=[]
 for r in records():
  if r['split']!=split:continue
  for offset in range(0,len(r['ids'])-1,127):
   ids=r['ids'][offset:offset+128]
   if len(ids)>1:out.append({'id':r['id'],'offset':offset,'ids':ids,'lang':r['lang'],'domain':r['domain'],'synthetic':r['synthetic']})
 return out

def batch(samples):
 n=max(len(s['ids']) for s in samples);ids=torch.full((len(samples),n),256,dtype=torch.long);valid=torch.zeros_like(ids,dtype=torch.bool);doc=torch.zeros_like(ids)
 for i,s in enumerate(samples):ids[i,:len(s['ids'])]=torch.tensor(s['ids']);valid[i,:len(s['ids'])]=True
 return ids,doc,valid

def order():
 w=windows('train');idx=list(range(len(w)));random.Random(17).shuffle(idx);return idx

def at(cursor):
 w=windows('train');idx=order();return batch([w[idx[(cursor*2+j)%len(idx)]] for j in range(2)])

def update(m,opt,cursor):
 ids,doc,valid=at(cursor);opt.zero_grad(set_to_none=True);start=time.perf_counter();ce,n=loss(m(ids,doc,valid),ids,doc,valid);ce.backward()
 grads={name:float(p.grad.norm()) for name,p in m.named_parameters() if p.grad is not None};assert all(math.isfinite(x) for x in grads.values());torch.nn.utils.clip_grad_norm_(m.parameters(),1);opt.step()
 return {'update':cursor+1,'ce':float(ce.detach()),'targets':n,'seconds':time.perf_counter()-start,'gradients':grads}

def save(path,m,opt,cursor):
 torch.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'cursor':cursor,'updates':cursor,'microsteps':cursor,'accumulation':1,'scheduler':None,'rng':torch.get_rng_state(),'python_rng':random.getstate(),'order':order(),'dataset':sha((ROOT/'results/data.json').read_bytes()),'tokenizer':FP,'kind':m.kind,'config':{'vocab':8192,'width':32,'chunk':16,'dropout':0,'precision':'CPU FP32'}},path)

def restore(path):
 c=torch.load(path,weights_only=True);assert c['dataset']==sha((ROOT/'results/data.json').read_bytes()) and c['tokenizer']==FP and c['order']==order();m=create(c['kind']);m.load_state_dict(c['model']);o=optimizer(m);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['rng']);random.setstate(c['python_rng']);return m,o,c['cursor']

def evaluate(m,split):
 totals={};m.eval()
 with torch.no_grad():
  for s in windows(split):
   ids,d,v=batch([s]);ce,n=loss(m(ids,d,v),ids,d,v);key=f"{'synthetic' if s['synthetic'] else 'real'}/{s['lang']}/{s['domain']}";a=totals.setdefault(key,[0.,0]);a[0]+=float(ce)*n;a[1]+=n
 return {k:{'nll':v[0]/v[1],'ppl':math.exp(v[0]/v[1]),'targets':v[1]} for k,v in totals.items()}

def train(kind,steps=64):
 if (ROOT/'results'/f'{kind}-final.pt').exists():raise FileExistsError('Preserve existing smoke checkpoint; reproduce in a new worktree/output copy')
 m=create(kind);opt=optimizer(m);initial={'train':evaluate(m,'train'),'dev':evaluate(m,'dev')};m.train();curves=[];start=time.perf_counter()
 for cursor in range(steps):
  curves.append(update(m,opt,cursor))
  if (cursor+1)%16==0:print(kind,cursor+1,curves[-1]['ce'],flush=True)
 elapsed=time.perf_counter()-start;save(ROOT/'results'/f'{kind}-final.pt',m,opt,steps)
 result={'kind':kind,'steps':steps,'seed':17,'allocated_parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'initial':initial,'final':{'train':evaluate(m,'train'),'dev':evaluate(m,'dev')},'curves':curves,'seconds':elapsed,'targets_per_second':sum(r['targets'] for r in curves)/elapsed,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024};dump('smoke-'+kind,result);return m
if __name__=='__main__':
 torch.set_num_threads(1)
 for kind in ['no_ice','ice','transformer']:train(kind)
