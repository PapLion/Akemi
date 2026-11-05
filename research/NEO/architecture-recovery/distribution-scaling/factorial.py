from pathlib import Path
import sys,json,hashlib,random,time,math,resource
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'foreground-binding'))
import harness as h
import torch
import torch.nn.functional as F
P=json.loads((ROOT/'PROTOCOL.json').read_text());OUT=ROOT/'results';OUT.mkdir(exist_ok=True);torch.set_num_threads(1)
def put(n,d):
 p=OUT/(n+'.json');assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
def get(n):return json.loads((OUT/(n+'.json')).read_text())
def historical():return json.loads((BASE/'learning-diagnosis/results/ladder-datasets.json').read_text())
def supports():return sorted(set(historical()['3'][0]['values']))
def datasets():
 ds=h.data();arms={}
 for arm,cfg in P['arms'].items():
  values=supports() if isinstance(cfg['values'],str) else cfg['values'];orders=cfg['orders'];keep=lambda r:all(v in values for v in r['values']) and r['order'] in orders
  arms[arm]={'train':[r for r in ds['train'] if keep(r)],'dev-layouts':[r for r in ds['dev-layouts'] if keep(r)],'dev-new-entity-pair':[r for r in ds['dev-combinations'] if keep(r)]}
  if len(orders)==1:arms[arm]['dev-opposite-order']=[r for r in ds['train'] if all(v in values for v in r['values']) and r['order'] not in orders]
 return arms
def sources():return {**h.sources(),'distribution-scaling/factorial.py':h.file_sha(Path(__file__)),'distribution-scaling/PROTOCOL.json':h.file_sha(ROOT/'PROTOCOL.json')}
def checkpoint(path,m,opt,cursor,rows,arm):
 assert not path.exists();torch.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'cursor_updates':cursor,'cursor_samples':cursor*8,'order':h.order(rows,17),'dataset_sha':h.digest(rows),'tokenizer_fingerprint':h.FP,'tokenizer_sha':h.file_sha(h.ARTIFACT),'protocol':P,'arm':arm,'seed':17,'sources':sources(),'scheduler':None,'pending_gradients':None,'accumulation':1},path)
def restore(path,rows):
 c=torch.load(path,weights_only=True);assert c['protocol']==P and c['sources']==sources() and c['dataset_sha']==h.digest(rows) and c['order']==h.order(rows,17) and c['tokenizer_sha']==h.file_sha(h.ARTIFACT) and c['tokenizer_fingerprint']==h.FP;m=h.model('B');m.load_state_dict(c['model']);o=h.optimizer(m);o.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,o,c

def evaluate(m,rows,tag=None):
 m.eval()
 with torch.no_grad():y=h.logits(m,rows);labels=torch.tensor([r['answer'] for r in rows]);prob=y.softmax(-1);ce=F.cross_entropy(y,labels,reduction='none');pred=y.argmax(-1)
 if tag:torch.save({'logits':y,'labels':labels,'input_ids':h.tensors(rows)[0],'last_positions':h.tensors(rows)[1]},OUT/(tag+'-logits.pt'))
 predictions=[];progs=defaultdict(list)
 for i,r in enumerate(rows):
  v={'example_id':r['example_id'],'program_id':r['program_id'],'entity':r['query_entity'],'query_side':r['query_side'],'values':r['values'],'order':r['order'],'gold':r['gold'],'target':r['answer'],'pred_id':int(pred[i]),'pred_value':r['choices'].index(int(pred[i])) if int(pred[i]) in r['choices'] else -1,'correct':int(pred[i])==r['answer'],'p_correct':float(prob[i,labels[i]]),'ce':float(ce[i]),'four_logits':y[i,r['choices']].tolist(),'four_probs_full_softmax':prob[i,r['choices']].tolist()};predictions.append(v);progs[r['program_id']].append(v)
 counts=Counter(r['gold'] for r in rows);entropy=-sum((n/len(rows))*math.log(n/len(rows)) for n in counts.values());chance=1/len(counts);by={(tuple(v[0]['values']),v[0]['order']):v for v in progs.values()};sw=[]
 for (values,order),v in by.items():
  if values[0]<values[1]:
   other=by[(tuple(reversed(values)),order)];sw.append(all(t['correct'] for t in v+other))
 result={'n':len(rows),'stories':len(progs),'accuracy':sum(v['correct'] for v in predictions)/len(rows),'joint_accuracy':sum(all(v['correct'] for v in p) for p in progs.values())/len(progs),'ce':float(ce.mean()),'mean_p_correct':float(prob[torch.arange(len(rows)),labels].mean()),'min_p_correct':float(prob[torch.arange(len(rows)),labels].min()),'valid_four_mass':float(prob[:,rows[0]['choices']].sum(-1).mean()),'pred_counts':dict(Counter(pred.tolist())),'same_answer_stories':sum(p[0]['pred_id']==p[1]['pred_id'] for p in progs.values()),'strict_swaps':{'n':len(sw),'correct':sum(sw),'accuracy':sum(sw)/len(sw)},'chance_marginal':chance,'chance_joint_independent_guesses':chance**2,'label_entropy_nats':entropy,'ce_over_label_entropy':float(ce.mean())/entropy,'by_entity':{},'by_value':{},'by_order':{}}
 result['accuracy_above_chance']=result['accuracy']-chance;result['accuracy_normalized_above_chance']=result['accuracy_above_chance']/(1-chance)
 for key,field in [('by_entity','entity'),('by_value','gold'),('by_order','order')]:
  for v in sorted(set(p[field] for p in predictions)):
   group=[p for p in predictions if p[field]==v];result[key][str(v)]={'n':len(group),'accuracy':sum(p['correct'] for p in group)/len(group),'ce':sum(p['ce'] for p in group)/len(group)}
 if tag:put(tag+'-predictions',predictions)
 return result

def frequencies(rows):
 return {'responses':len(rows),'programs':len(set(r['program_id'] for r in rows)),'unique_inputs':len(set(tuple(r['prefix']+r['query']) for r in rows)),'entities':dict(Counter(r['query_entity'] for r in rows)),'values':dict(Counter(r['gold'] for r in rows)),'orders':dict(Counter(r['order'] for r in rows)),'entity_value':{str(k):v for k,v in Counter((r['query_entity'],r['gold']) for r in rows).items()},'value_pair_order':{str(k):v for k,v in Counter((tuple(r['values']),r['order']) for r in rows).items()},'valid_lengths':dict(Counter(len(r['prefix'])+len(r['query']) for r in rows))}
def validate_data():
 arms=datasets();hist=historical();assert arms['A']['train']==hist['3'] and arms['D']['train']==hist['4'];out={}
 for arm,ds in arms.items():
  rows=ds['train'];values=set(r['gold'] for r in rows);orders=set(r['order'] for r in rows);expected=len(values)*(len(values)-1)*len(orders)*2;assert len(rows)==expected
  assert len(set(Counter(r['gold'] for r in rows).values()))==1 and len(set(Counter(r['query_entity'] for r in rows).values()))==1;assert len(set(Counter((r['query_entity'],r['gold']) for r in rows).values()))==1
  x,last,labels=h.tensors(rows)
  for i,r in enumerate(rows):assert r['answer']==r['choices'][r['values'][r['query_side']]] and labels[i]==r['answer'] and last[i]==len(r['prefix'])+len(r['query'])-1 and h.TOK.encode(r['query_text'])==r['query'] and h.TOK.decode(h.TOK.encode(r['facts']))==r['facts']
  for i in range(0,len(rows),2):assert rows[i]['query'][-1]!=rows[i+1]['query'][-1] and rows[i]['prefix']==rows[i+1]['prefix']
  train_inputs={tuple(r['prefix']+r['query']) for r in rows}
  for split,r in ds.items():
   if split!='train':assert not train_inputs.intersection(tuple(v['prefix']+v['query']) for v in r)
  idx=h.order(rows,17);used=[rows[idx[(u*8+j)%len(rows)]] for u in range(400) for j in range(8)]
  out[arm]={'dataset':{split:frequencies(r) for split,r in ds.items()},'effective_exposure':frequencies(used),'per_example_exposures':dict(Counter(r['example_id'] for r in used)),'dataset_sha':h.digest(rows),'order':idx,'complete_cycles':3200//len(rows),'remainder':3200%len(rows),'vocabulary':8192,'tokenizer_sha':h.file_sha(h.ARTIFACT)}
 return out

def train_arm(arm,ds):
 rows=ds['train'];m=h.model('B');o=h.optimizer(m);initial=h.state_sha(m);checkpoint(OUT/f'{arm}-initial.pt',m,o,0,rows,arm);curves=[];initial_eval=evaluate(m,rows,f'{arm}-initial');start=time.perf_counter();trainseconds=0
 for u in range(400):
  m.train();rec=h.update(m,o,rows,u,17);trainseconds+=rec['seconds'];norm=math.sqrt(sum(g*g for g in rec['gradients'].values()));rec['global_pre_clip_norm']=norm;rec['clip_scale']=min(1,1/(norm+1e-6))
  if (u+1)%50==0:rec['full_train_post_update']=evaluate(m,rows,f'{arm}-update-{u+1}')
  curves.append(rec)
  if u==299:checkpoint(OUT/f'{arm}-300.pt',m,o,300,rows,arm)
 checkpoint(OUT/f'{arm}-final.pt',m,o,400,rows,arm);evals={k:evaluate(m,v,f'{arm}-{k}-final') for k,v in ds.items()};ev=evals['train'];passed=ev['accuracy']==1 and ev['joint_accuracy']==1 and ev['strict_swaps']['accuracy']==1 and ev['ce']<=.1 and ev['min_p_correct']>=.9
 result={'arm':arm,'initial_sha':initial,'updates':400,'responses':3200,'initial_evaluation':initial_eval,'evaluations':evals,'passed_microfit':passed,'curves':curves,'seconds_train_updates_only':trainseconds,'seconds_including_curve_evaluation':time.perf_counter()-start,'targets_s_updates_only':3200/trainseconds,'process_peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'clipping_frequency':sum(r['global_pre_clip_norm']>1 for r in curves)/400,'checkpoint_sha':h.file_sha(OUT/f'{arm}-final.pt')};put(arm+'-result',result);print(arm,'n',len(rows),'accuracy',ev['accuracy'],'joint',ev['joint_accuracy'],'ce',ev['ce'],'swaps',ev['strict_swaps'],'PASS',passed,flush=True)
 return result

def main():
 assert get('contracts')['passed'] and get('contracts')['sources']==sources();put('datasets',datasets());put('frequencies',validate_data());res={}
 for arm,ds in datasets().items():res[arm]=train_arm(arm,ds)
 assert len(set(v['initial_sha'] for v in res.values()))==1
 comparisons={}
 for metric in ['accuracy','joint_accuracy','ce_over_label_entropy','accuracy_normalized_above_chance']:
  a={k:v['evaluations']['train'][metric] for k,v in res.items()};comparisons[metric]={'B_minus_A':a['B']-a['A'],'C_minus_A':a['C']-a['A'],'D_minus_B':a['D']-a['B'],'D_minus_C':a['D']-a['C'],'interaction_D_minus_B_minus_C_plus_A':a['D']-a['B']-a['C']+a['A']}
 put('factorial-effects',comparisons);put('primary-comparison',{k:{n:v for n,v in x.items() if n!='curves'} for k,x in res.items()})
if __name__=='__main__':main()
