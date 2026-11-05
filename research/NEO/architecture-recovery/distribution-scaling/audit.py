from factorial import *
def compare_states(a,b):
 return all(torch.equal(v,b[k]) for k,v in a.items())
def compare_optimizer(a,b):
 return a['param_groups']==b['param_groups'] and a['state'].keys()==b['state'].keys() and all(torch.equal(v,b['state'][i][k]) if isinstance(v,torch.Tensor) else v==b['state'][i][k] for i,s in a['state'].items() for k,v in s.items())
def main():
 ds=datasets();history={}
 for arm,cursor,oldlevel in [('A',300,'3'),('D',400,'4')]:
  name=f'{arm}-300.pt' if cursor==300 else f'{arm}-final.pt';cp=torch.load(OUT/name,weights_only=True);oldcp=torch.load(BASE/f'learning-diagnosis/results/level-{oldlevel}-final.pt',weights_only=True)
  record={'dataset_exact':ds[arm]['train']==historical()[oldlevel],'model_exact':compare_states(cp['model'],oldcp['model']),'optimizer_exact':compare_optimizer(cp['optimizer'],oldcp['optimizer']),'torch_rng_exact':torch.equal(cp['torch_rng'],oldcp['torch_rng']),'python_rng_exact':cp['python_rng']==oldcp['python_rng'],'new_checkpoint_sha':h.file_sha(OUT/name),'historical_checkpoint_sha':h.file_sha(BASE/f'learning-diagnosis/results/level-{oldlevel}-final.pt')}
  assert all(record[k] for k in ['dataset_exact','model_exact','optimizer_exact','torch_rng_exact']);record['python_rng_note']='Global Python RNG differs across historical invocations; unused by model/update. Sampling uses local random.Random(17). No numerical tolerance changed.';history[arm]=record
 final={};sampler={}
 for arm,d in ds.items():
  m,o,c=restore(OUT/f'{arm}-final.pt',d['train']);met=evaluate(m,d['train']);assert json.loads(json.dumps(met))==get(arm+'-result')['evaluations']['train'];active={id(p) for p in m.parameters() if p.requires_grad};params=[id(p) for g in o.param_groups for p in g['params']];assert len(params)==len(active) and active==set(params);assert all(int(s['step'])==400 for s in o.state.values());final[arm]={'restore_metrics_exact':True,'optimizer_exact_coverage':True,'all_optimizer_steps':400,'cursor':c['cursor_updates'],'samples':c['cursor_samples']}
  rows=d['train'];idx=h.order(rows,17);batchcounts=[]
  for u in range(400):
   batch=[rows[idx[(u*8+j)%len(rows)]] for j in range(8)];vc=Counter(r['gold'] for r in batch);ec=Counter(r['query_entity'] for r in batch);batchcounts.append({'update':u+1,'values':dict(vc),'entities':dict(ec),'orders':dict(Counter(r['order'] for r in batch)),'unique_examples':len(set(r['example_id'] for r in batch)),'unique_stories':len(set(r['program_id'] for r in batch)),'both_queries_per_selected_story':all(sum(v['program_id']==r['program_id'] for v in batch)==2 for r in batch) if len(rows)>4 else None})
  support=len(set(r['gold'] for r in rows));sampler[arm]={'all_values_present_fraction':sum(len(b['values'])==support for b in batchcounts)/400,'exact_value_balance_fraction':sum(len(b['values'])==support and len(set(b['values'].values()))==1 for b in batchcounts)/400,'equal_entity_query_fraction':sum(len(set(b['entities'].values()))==1 for b in batchcounts)/400,'all_batches':batchcounts}
 put('reproduction-audit',{'passed':True,'historical':history,'final_checkpoints':final,'sources':sources()});put('minibatch-diagnostics',sampler);print('AUDIT PASS A300 and D400 exactly reproduce models, AdamW and Torch RNG; global unused Python RNG difference recorded; all final checkpoints certified')
if __name__=='__main__':main()
